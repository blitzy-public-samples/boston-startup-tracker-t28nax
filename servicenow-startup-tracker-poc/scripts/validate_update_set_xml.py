#!/usr/bin/env python3
"""Two-level well-formedness validator for the Boston Startup Tracker Update Set XML.

Implements the prompt section 11.0 requirement to validate the deliverable at both
the outer update-set level and the nested per-record payload level before delivery,
expressed as pre-delivery gates G-1 and G-2 of AAP section 0.11.1:

    gate G-1  outer update-set level: byte prologue (no byte-order mark, XML
              declaration first), XML well-formedness, the document shape
              <unload> / exactly one <sys_remote_update_set> / at least one
              <sys_update_xml>, and header linkage -- every <sys_update_xml>
              carries a <remote_update_set> equal to the single
              <sys_remote_update_set>'s <sys_id>.
    gate G-2  nested per-record payload level: the text of each <payload>
              parsed as an independent document whose root is <record_update>
              carrying a non-empty table attribute, plus the update-name
              contract -- each <sys_update_xml>'s <name> names the record its
              payload carries, being either <table>_<sys_id> of the payload's
              primary record or that record's own <sys_update_name>. Every
              payload is examined whatever --max-errors is set to; the option
              caps only how many failure diagnostics are written, and the
              reported pass and failure counts stay complete.

The remaining pre-delivery gates of AAP section 0.11.1 -- G-3 referential
integrity across payload records (dictionary collections to table names,
reference targets, choice name and element pairs, ACL names, ACL-role joins,
operations to the REST definition), G-4 scope containment, G-5 secret hygiene,
G-6 field-list fidelity, G-7 deliverable completeness, G-8 deck structure and
G-9 governance completeness -- are outside this validator's scope. It checks
well-formedness, outer document shape and header linkage only; a file that
passes G-1 and G-2 is not thereby certified against G-3 through G-9.

Parser safety. Four structural defences are applied, the first of them before any
path is opened:

    parser gate           the runtime Expat must carry the disproportionate-
                          allocation defence, or the run is refused before a byte
                          is read. Two routes satisfy it: an Expat at or above
                          2.7.2, where the defence reached the upstream tree, or
                          an Expat at 2.7.1 that exposes both
                          XML_SetAllocTrackerActivationThreshold and
                          XML_SetAllocTrackerMaximumAmplification, which is how a
                          distribution ships the defence as a backport without
                          moving the reported version string. The gate is
                          fail-closed: an undetermined version, an unprobeable
                          library, and the entry points appearing on a base below
                          2.7.1 are all refused rather than assumed about.
                          There is no option to override it. The gate is
                          decision D-351.
    declaration hygiene   a document declaring a document type or an entity, or
                          referencing any entity other than the five predefined
                          names and numeric character references, is refused
                          before it reaches the parser.
    size ceilings         the source file is read through a byte cap and every
                          nested payload is measured against a payload cap.
    count ceiling         the number of update records is capped.

Every ceiling is adjustable from the command line; the parser gate is not. The
runtime parser version and its mitigation state are reported alongside the first
progress line, and --self-test reports the gate's verdict on the current runtime
and exercises the gate's own fixtures. The reasoning behind each defence is
recorded in docs/decisions/DECISION_LOG.md, per the Explainability rule.

Usage:
    validate_update_set_xml.py [-q | -v] [--max-errors N] [--max-bytes N]
                               [--max-payloads N] [--max-payload-bytes N] [PATH ...]

With no PATH, the sibling Update Set
update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml is resolved
relative to this script's own directory.

--max-errors caps how many gate G-2 failure diagnostics are written; every
update record and every one of its <payload> children is examined regardless of
the cap, and the reported pass and failure counts are always complete.

Exit codes:
    0   every validated file satisfied gate G-1 and gate G-2.
    1   at least one validation failure at either level, or a self-test fixture
        that did not behave as its label declares.
    2   usage error; a path that is missing, not a regular file, or unreadable;
        or a parser gate refusal, in which case no path was opened and no file
        was validated. Code 2 takes precedence over code 1 when both occur.

A parser gate refusal is reported as code 2, not code 1: it is a statement
about the runtime and not about the file.

When the parser gate refuses. The gate has no override, so the fallback is a
procedure rather than a flag, and the refusal prints it in three ordered steps:
run --self-test, which parses nothing and therefore runs on any runtime, and
record its report of this runtime's parser state; re-run on a runtime that
satisfies the gate, confirmed with --self-test first, which is the only route
that produces gate G-1 and G-2 evidence; and if no such runtime can be reached,
leave G-1 and G-2 unrecorded and treat delivery as blocked, recording the
refusal, the --self-test output and the decision taken. No substitute is
accepted -- not a parse by eye, not another tool on this same runtime, and not
an assumption carried from an earlier run. The same procedure is set out in
docs/deployment-runbook.md under "When the parser gate refuses".

Progress lines and the terminal verdict are written to stdout; failure detail is
written to stderr.
"""

from __future__ import annotations

import argparse
import codecs
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.parsers import expat

EXIT_OK = 0
EXIT_VALIDATION_FAILED = 1
EXIT_USAGE_OR_IO = 2

GATE_OUTER = "G-1"
GATE_PAYLOAD = "G-2"

ROOT_TAG = "unload"
HEADER_TAG = "sys_remote_update_set"
RECORD_TAG = "sys_update_xml"
PAYLOAD_TAG = "payload"
NESTED_ROOT_TAG = "record_update"
NESTED_TABLE_ATTR = "table"

RECORD_TYPE_TAG = "type"
RECORD_TARGET_TAG = "target_name"
RECORD_LINK_TAG = "remote_update_set"
RECORD_NAME_TAG = "name"
HEADER_ID_TAG = "sys_id"
PAYLOAD_ID_TAG = "sys_id"
PAYLOAD_UPDATE_NAME_TAG = "sys_update_name"
UNSET_FIELD = "<unset>"

# gate G-1: how many unlinked update records the linkage diagnostic names
LINKAGE_SAMPLE_LIMIT = 5

XML_DECLARATION_PREFIX = b"<?xml"
# gate G-1: one of these bytes must be the sixth byte of the file for the leading
# "<?xml" to be classified as the declaration; "<?xml-stylesheet ...?>" and "<?xmlfoo?>"
# are classified as processing instructions (decision D-154).
DECLARATION_DELIMITERS = frozenset({b" ", b"\t", b"\r", b"\n"})
DECLARATION_DELIMITER_BYTES = b" \t\r\n"
DECLARATION_CLOSE = b"?>"
DECLARATION_VERSION = b"version"
QUESTION_MARK = 0x3F
# gate G-1: how far into the file the declaration's closing "?>" is looked for
DECLARATION_SCAN_BYTES = 256
# gate G-1: how many bytes of a processing-instruction target a diagnostic names
TARGET_SAMPLE_BYTES = 32
PROCESSING_INSTRUCTION_OPEN = b"<?"

# gate G-1: byte-order marks rejected on the raw bytes (AAP section 0.8.1)
BYTE_ORDER_MARKS = (
    ("UTF-8", codecs.BOM_UTF8),
    ("UTF-16-LE", codecs.BOM_UTF16_LE),
    ("UTF-16-BE", codecs.BOM_UTF16_BE),
)

DEFAULT_UPDATE_SET_DIR = "update-set"
DEFAULT_UPDATE_SET_NAME = "x_bst_startuptrk_boston_startup_tracker_update_set.xml"

# Parser safety ceilings (decision D-153): the largest input document, the largest
# number of payloads and the largest single payload this validator will read. Each is
# a default that --max-bytes, --max-payloads and --max-payload-bytes override.
DEFAULT_MAX_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_PAYLOADS = 5000
DEFAULT_MAX_PAYLOAD_BYTES = 4 * 1024 * 1024
READ_CHUNK_BYTES = 1024 * 1024

# Declaration hygiene: the only entity references a well-formed XML document needs
# without a document type declaration.
PREDEFINED_ENTITIES = frozenset({"amp", "lt", "gt", "quot", "apos"})
ENTITY_REFERENCE = re.compile(r"&(#[0-9]+|#x[0-9A-Fa-f]+|[^;&\s]{1,64});")
DOCTYPE_TOKEN = "<!DOCTYPE"
ENTITY_TOKEN = "<!ENTITY"

# Parser gate: the release in which Expat's disproportionate-allocation defence
# reached the upstream tree, and the release immediately before it, which is the
# only base a backport of that defence is recognised on.
EXPAT_FIXED_VERSION = (2, 7, 2)
EXPAT_BACKPORT_FLOOR = (2, 7, 1)
# The two entry points that defence adds. Their presence is the observable
# signature of the mitigation, whatever version string the build reports.
ALLOC_TRACKER_SYMBOLS = (
    "XML_SetAllocTrackerActivationThreshold",
    "XML_SetAllocTrackerMaximumAmplification",
)
# Probed in order. None is the running process image, which is where the symbols
# live when the interpreter links Expat statically, as CPython commonly does.
EXPAT_LIBRARY_CANDIDATES: tuple[str | None, ...] = (
    None,
    "libexpat.so.1",
    "libexpat.so",
    "libexpat.1.dylib",
)
# Fallback when the module exposes no version tuple: "expat_2.7.1" and similar.
EXPAT_VERSION_TEXT = re.compile(r"(\d+)\.(\d+)\.(\d+)")

MITIGATION_UPSTREAM = "release carries the allocation-tracker defence upstream"
MITIGATION_BACKPORT = "allocation-tracker entry points present, backported"
MITIGATION_ABSENT = "no allocation-tracker entry point resolves"
MITIGATION_UNPROBEABLE = "the allocation-tracker entry points could not be probed"


class SourceUnavailable(Exception):
    """A path is missing, not a regular file, or unreadable (exit code 2)."""


class ParserGate:
    """The verdict on whether this runtime's Expat may be handed a document.

    ``allowed`` is the whole decision; every other member exists so a refusal
    names what was observed rather than only that it refused.
    """

    __slots__ = ("allowed", "mitigation", "reason", "version", "version_text")

    def __init__(
        self,
        allowed: bool,
        reason: str,
        version: tuple[int, ...] | None,
        version_text: str,
        mitigation: str,
    ) -> None:
        self.allowed = allowed
        self.reason = reason
        self.version = version
        self.version_text = version_text
        self.mitigation = mitigation

    def describe(self) -> str:
        """Return the one-line parser state written beside each progress line."""
        return f"{self.version_text}, {self.mitigation}"


def expat_version_tuple() -> tuple[int, ...] | None:
    """Return the runtime Expat version, or None when it cannot be established.

    The module's own tuple is preferred. Where a build omits it the reported
    version string is read instead. A runtime that yields neither is treated as
    undetermined, which the gate refuses rather than assumes about.
    """
    version = getattr(expat, "version_info", None)
    if isinstance(version, tuple) and version and all(
        isinstance(part, int) for part in version
    ):
        return version
    match = EXPAT_VERSION_TEXT.search(str(getattr(expat, "EXPAT_VERSION", "")))
    if match:
        return tuple(int(part) for part in match.groups())
    return None


def open_expat_library(ctypes_module, candidate: str | None):
    """Return an opened handle for one library candidate, or None if it will not open.

    A candidate that does not exist, or a platform that will not open the process
    image, is not an error here: the caller tries the next candidate and, having
    exhausted them, reports the probe as unavailable rather than as negative.
    """
    try:
        if candidate is None:
            return ctypes_module.CDLL(None)
        return ctypes_module.CDLL(candidate)
    except (OSError, TypeError, ValueError):
        return None


def library_exposes_alloc_tracker(library) -> bool:
    """Return True when one opened library exposes both tracker entry points."""
    try:
        return all(hasattr(library, symbol) for symbol in ALLOC_TRACKER_SYMBOLS)
    except (AttributeError, OSError, TypeError, ValueError):
        return False


def alloc_tracker_state() -> bool | None:
    """Return True if both allocation-tracker entry points resolve.

    False means the probe ran and no opened library exposed them. None means the
    probe could not run at all -- no ``ctypes``, or no candidate library that
    would open. Both False and None refuse the gate; they are returned as
    distinct values so the refusal reports which of the two occurred.
    """
    try:
        import ctypes
    except ImportError:
        return None
    probed = False
    for candidate in EXPAT_LIBRARY_CANDIDATES:
        library = open_expat_library(ctypes, candidate)
        if library is None:
            continue
        probed = True
        if library_exposes_alloc_tracker(library):
            return True
    return False if probed else None


def evaluate_parser_gate(
    version: tuple[int, ...] | None,
    tracker: bool | None,
    version_text: str = "",
) -> ParserGate:
    """Decide the gate from an Expat version and an allocation-tracker probe.

    Pure, so the fixtures exercise the same decision the runtime takes. Two
    routes pass: a release at or above the upstream fix, or the mitigation's
    entry points present on the release immediately preceding it, which is how a
    distribution ships the fix without moving the version string. Everything
    else refuses, including an undetermined version and an unprobeable library.
    """
    text = version_text or (
        ".".join(str(part) for part in version) if version else "version undetermined"
    )
    if tracker is True:
        mitigation = MITIGATION_BACKPORT
    elif tracker is False:
        mitigation = MITIGATION_ABSENT
    else:
        mitigation = MITIGATION_UNPROBEABLE
    fixed = ".".join(str(part) for part in EXPAT_FIXED_VERSION)
    floor = ".".join(str(part) for part in EXPAT_BACKPORT_FLOOR)
    if version is None:
        return ParserGate(
            False,
            "the runtime Expat version could not be established, so neither the "
            f"{fixed} floor nor a backport onto {floor} can be confirmed",
            None,
            text,
            mitigation,
        )
    if version >= EXPAT_FIXED_VERSION:
        return ParserGate(
            True,
            f"Expat {text} is at or above {fixed}",
            version,
            text,
            MITIGATION_UPSTREAM,
        )
    if tracker is True and version >= EXPAT_BACKPORT_FLOOR:
        return ParserGate(
            True,
            f"Expat {text} is below {fixed} but both allocation-tracker entry "
            "points resolve, so the defence is present as a backport",
            version,
            text,
            mitigation,
        )
    if tracker is True:
        reason = (
            f"Expat {text} exposes the allocation-tracker entry points but is "
            f"below {floor}; a backport is recognised only on {floor} or later, "
            "because on an older base the other allocation defences of the "
            f"{floor} series are not established by this probe"
        )
    elif tracker is False:
        reason = (
            f"Expat {text} is below {fixed} and exposes neither allocation-"
            "tracker entry point, so the disproportionate-allocation defence is "
            "absent"
        )
    else:
        reason = (
            f"Expat {text} is below {fixed} and the allocation-tracker entry "
            "points could not be probed, so the defence cannot be confirmed"
        )
    return ParserGate(False, reason, version, text, mitigation)


def parser_gate_state() -> ParserGate:
    """Evaluate the gate against this runtime."""
    return evaluate_parser_gate(
        expat_version_tuple(),
        alloc_tracker_state(),
        str(getattr(expat, "EXPAT_VERSION", "") or "version undetermined"),
    )


class Limits:
    """The parser safety ceilings applied to one validation run."""

    __slots__ = ("max_bytes", "max_payload_bytes", "max_payloads")

    def __init__(
        self,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_payloads: int = DEFAULT_MAX_PAYLOADS,
        max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES,
    ) -> None:
        self.max_bytes = max_bytes
        self.max_payloads = max_payloads
        self.max_payload_bytes = max_payload_bytes


class Failure:
    """One validation failure attributed to gate G-1 or gate G-2."""

    __slots__ = ("detail", "gate")

    def __init__(self, gate: str, detail: str) -> None:
        self.gate = gate
        self.detail = detail


class FileOutcome:
    """Per-file counters and failures produced by validate_file.

    payload_failure_count is the complete gate G-2 failure count; payload_failures
    holds only the diagnostics retained under --max-errors.
    """

    __slots__ = (
        "io_error",
        "outer_failures",
        "path",
        "payload_failure_count",
        "payload_failures",
        "payload_failures_suppressed",
        "payloads_passed",
        "payloads_total",
        "records_total",
    )

    def __init__(self, path: Path) -> None:
        self.path = path
        self.io_error: str | None = None
        self.outer_failures: list[Failure] = []
        self.payload_failures: list[Failure] = []
        self.payload_failure_count = 0
        self.payload_failures_suppressed = 0
        self.records_total = 0
        self.payloads_total = 0
        self.payloads_passed = 0

    @property
    def failures(self) -> list[Failure]:
        """Every retained failure diagnostic, gate G-1 first then gate G-2."""
        return self.outer_failures + self.payload_failures


class PayloadTally:
    """Complete gate G-2 counts plus the diagnostics retained under --max-errors.

    discovered counts every <payload> element visited, passed counts those that
    were well-formed, named counts those whose update record names the record the
    payload carries, and failure_count counts every failure whether or not its
    diagnostic was retained.
    """

    __slots__ = (
        "discovered",
        "failure_count",
        "failures",
        "max_errors",
        "named",
        "passed",
    )

    def __init__(self, max_errors: int = 0) -> None:
        self.max_errors = max_errors
        self.failures: list[Failure] = []
        self.failure_count = 0
        self.discovered = 0
        self.passed = 0
        self.named = 0

    def add_failure(self, detail: str) -> None:
        """Count one gate G-2 failure, retaining its diagnostic under the cap."""
        self.failure_count += 1
        if not self.max_errors or len(self.failures) < self.max_errors:
            self.failures.append(Failure(GATE_PAYLOAD, detail))

    @property
    def suppressed(self) -> int:
        """The number of counted gate G-2 failures whose diagnostic was withheld."""
        return self.failure_count - len(self.failures)


class Reporter:
    """Stream policy: progress and verdict to stdout, failure detail to stderr.

    Every write is flushed.
    """

    def __init__(self, quiet: bool = False, verbose: bool = False) -> None:
        self.quiet = quiet
        self.verbose = verbose

    @staticmethod
    def _write(stream, message: str) -> None:
        """Write one line to stream and flush it."""
        stream.write(message + "\n")
        stream.flush()

    def progress(self, message: str) -> None:
        """Write a stage line to stdout unless --quiet is set."""
        if not self.quiet:
            self._write(sys.stdout, message)

    def payload_line(self, message: str) -> None:
        """Write a per-payload line to stdout when --verbose is set."""
        if self.verbose:
            self._write(sys.stdout, message)

    def failure(self, message: str) -> None:
        """Write a failure line to stderr; never suppressed."""
        self._write(sys.stderr, message)

    def verdict(self, message: str) -> None:
        """Write the terminal verdict line to stdout; never suppressed."""
        self._write(sys.stdout, message)


def format_parse_error(exc: ET.ParseError) -> str:
    """Render a ParseError as its class name followed by the parser message."""
    return f"{type(exc).__name__}: {exc}"


def read_source_bytes(path: Path, max_bytes: int) -> tuple[bytes, bool]:
    """Return up to max_bytes of path plus a flag reporting that the cap was exceeded.

    Reading is chunked and stops one byte past the cap, so an oversized file is
    never loaded whole. SourceUnavailable is raised for the exit-2 cases.
    """
    try:
        if not path.exists():
            raise SourceUnavailable(f"path does not exist: {path}")
        if not path.is_file():
            raise SourceUnavailable(f"path is not a regular file: {path}")
        chunks: list[bytes] = []
        read = 0
        with path.open("rb") as handle:
            while read <= max_bytes:
                chunk = handle.read(min(READ_CHUNK_BYTES, max_bytes + 1 - read))
                if not chunk:
                    break
                chunks.append(chunk)
                read += len(chunk)
        data = b"".join(chunks)
    except OSError as exc:
        raise SourceUnavailable(
            f"path is not readable: {path} ({type(exc).__name__}: {exc})"
        ) from exc
    if len(data) > max_bytes:
        return data[:max_bytes], True
    return data, False


def check_declaration_hygiene(text: str, gate: str, subject: str) -> list[Failure]:
    """Refuse a document type declaration, an entity declaration or an unknown entity.

    Applied to both XML levels before either is parsed. The three refused forms are
    the DOCTYPE token, the ENTITY token, and any entity reference that is neither
    one of the five predefined names nor a numeric character reference.
    """
    upper = text.upper()
    for token in (DOCTYPE_TOKEN, ENTITY_TOKEN):
        index = upper.find(token)
        if index != -1:
            return [
                Failure(
                    gate,
                    f"{subject}: {token} declaration present at character "
                    f"{index}; document type and entity declarations are refused",
                )
            ]
    for match in ENTITY_REFERENCE.finditer(text):
        name = match.group(1)
        if name.startswith("#"):
            continue
        if name in PREDEFINED_ENTITIES:
            continue
        return [
            Failure(
                gate,
                f"{subject}: entity reference &{name}; at character "
                f"{match.start()} is not one of the five predefined entities or a "
                "numeric character reference",
            )
        ]
    return []


def first_mismatch_offset(data: bytes, expected: bytes) -> int:
    """Return the offset of the first byte of data that differs from expected."""
    limit = min(len(data), len(expected))
    for offset in range(limit):
        if data[offset] != expected[offset]:
            return offset
    return limit


def instruction_target(data: bytes) -> str:
    """Return the target of the processing instruction at offset 0, or an empty string.

    The target is the run of bytes after "<?" up to the first whitespace byte or
    question mark, capped at TARGET_SAMPLE_BYTES so a diagnostic naming it stays
    bounded.
    """
    if not data.startswith(PROCESSING_INSTRUCTION_OPEN):
        return ""
    target = bytearray()
    for byte in data[len(PROCESSING_INSTRUCTION_OPEN):]:
        if byte == QUESTION_MARK or byte in DECLARATION_DELIMITER_BYTES:
            break
        target.append(byte)
        if len(target) == TARGET_SAMPLE_BYTES:
            break
    return bytes(target).decode("ascii", "replace")


def check_byte_prologue(data: bytes) -> list[Failure]:
    """Gate G-1 byte checks: no byte-order mark, and a real XML declaration first.

    Four conditions, in order: no leading byte-order mark; nothing at all before
    the declaration, whitespace included; the first five bytes are "<?xml"
    followed by a whitespace byte, which is what distinguishes a declaration from
    a processing instruction whose target begins with those characters; and a
    "version" pseudo-attribute before the declaration's closing "?>".

    Diagnostics name the violated condition, byte counts, offsets and a bounded
    processing-instruction target only; no other input content is written to any
    stream, per the gate G-5 secret-hygiene requirement.
    """
    for label, mark in BYTE_ORDER_MARKS:
        if data.startswith(mark):
            return [
                Failure(
                    GATE_OUTER,
                    f"byte-order mark present: leading {label} BOM of "
                    f"{len(mark)} byte(s); the file must begin with the XML "
                    "declaration",
                )
            ]
    if data[:1] in DECLARATION_DELIMITERS:
        leading = len(data) - len(data.lstrip(DECLARATION_DELIMITER_BYTES))
        return [
            Failure(
                GATE_OUTER,
                f"whitespace before the XML declaration: {leading} leading "
                "whitespace byte(s); nothing may precede the declaration",
            )
        ]
    if not data.startswith(XML_DECLARATION_PREFIX):
        prefix = XML_DECLARATION_PREFIX.decode("ascii")
        offset = first_mismatch_offset(data, XML_DECLARATION_PREFIX)
        target = instruction_target(data)
        found = (
            f"; a processing instruction with target {target!r} is first"
            if target
            else ""
        )
        return [
            Failure(
                GATE_OUTER,
                "XML declaration is not first: the file must begin with "
                f"{prefix!r}; {len(data)} byte(s) read, first byte differing "
                f"from the declaration at offset {offset}{found}",
            )
        ]
    prefix_length = len(XML_DECLARATION_PREFIX)
    delimiter = data[prefix_length:prefix_length + 1]
    if delimiter not in DECLARATION_DELIMITERS:
        prefix = XML_DECLARATION_PREFIX.decode("ascii")
        target = instruction_target(data)
        return [
            Failure(
                GATE_OUTER,
                f"not an XML declaration: {prefix!r} must be followed by a "
                "whitespace byte; the file opens a processing instruction with "
                f"target {target!r}",
            )
        ]
    window = data[:DECLARATION_SCAN_BYTES]
    close = window.find(DECLARATION_CLOSE)
    if close == -1:
        return [
            Failure(
                GATE_OUTER,
                "XML declaration is unterminated: no "
                f"{DECLARATION_CLOSE.decode('ascii')!r} within the first "
                f"{DECLARATION_SCAN_BYTES} byte(s)",
            )
        ]
    body = window[prefix_length:close]
    if DECLARATION_VERSION not in body:
        return [
            Failure(
                GATE_OUTER,
                "XML declaration carries no "
                f"{DECLARATION_VERSION.decode('ascii')!r} pseudo-attribute; the "
                f"declaration ends at offset {close + len(DECLARATION_CLOSE)}",
            )
        ]
    return []


def check_header_linkage(
    header: ET.Element, records: list[ET.Element], reporter: Reporter
) -> list[Failure]:
    """Gate G-1 linkage check: every update record carries the header's <sys_id>.

    Each <sys_update_xml>'s <remote_update_set> is compared with the single
    <sys_remote_update_set>'s <sys_id>. A record whose element is absent, empty
    or unequal is unlinked. Every unlinked record is counted, the first
    LINKAGE_SAMPLE_LIMIT of them are named in one diagnostic, and the
    diagnostic states how many further ones were not named. Diagnostics name
    the violated condition and the header identifier only; no other input
    content is written to any stream, per the gate G-5 secret-hygiene
    requirement.
    """
    header_id = (header.findtext(HEADER_ID_TAG) or "").strip()
    if not header_id:
        return [
            Failure(
                GATE_OUTER,
                f"<{HEADER_TAG}> header record carries no non-empty "
                f"<{HEADER_ID_TAG}>, so no <{RECORD_TAG}> record can carry it",
            )
        ]

    total = len(records)
    unlinked = 0
    samples: list[str] = []
    for ordinal, record in enumerate(records, 1):
        element = record.find(RECORD_LINK_TAG)
        if element is None:
            condition = f"has no <{RECORD_LINK_TAG}> element"
        elif not (element.text or "").strip():
            condition = f"has an empty <{RECORD_LINK_TAG}> element"
        elif element.text.strip() != header_id:
            condition = (
                f"has a <{RECORD_LINK_TAG}> other than the header "
                f"<{HEADER_ID_TAG}>"
            )
        else:
            continue
        unlinked += 1
        if len(samples) < LINKAGE_SAMPLE_LIMIT:
            samples.append(f"{record_label(record, ordinal, total)} {condition}")

    reporter.progress(
        f"    {total - unlinked}/{total} update record(s) carry the header "
        f"<{HEADER_ID_TAG}> {header_id}"
    )
    if not unlinked:
        return []

    detail = (
        f"{unlinked} of {total} <{RECORD_TAG}> record(s) do not carry a "
        f"<{RECORD_LINK_TAG}> equal to the header <{HEADER_ID_TAG}> "
        f"{header_id}: " + "; ".join(samples)
    )
    withheld = unlinked - len(samples)
    if withheld:
        detail += f"; {withheld} further unlinked record(s) not named"
    return [Failure(GATE_OUTER, detail)]


def validate_outer(
    data: bytes, reporter: Reporter, limits: Limits, truncated: bool
) -> tuple[list[Failure], list[ET.Element]]:
    """Run gate G-1 over the outer document, returning failures and update records."""
    failures = check_byte_prologue(data)

    # gate G-1: the byte cap is a refusal, not a truncation to be parsed
    if truncated:
        failures.append(
            Failure(
                GATE_OUTER,
                f"source exceeds the {limits.max_bytes} byte ceiling; raise "
                "--max-bytes only for a source you trust",
            )
        )
        reporter.progress(
            f"    gate {GATE_OUTER} FAILED: source exceeds the byte ceiling"
        )
        return failures, []

    # gate G-1: declaration hygiene runs before the parser sees the document
    hygiene = check_declaration_hygiene(
        data.decode("utf-8", errors="replace"), GATE_OUTER, "outer document"
    )
    if hygiene:
        failures.extend(hygiene)
        reporter.progress(
            f"    gate {GATE_OUTER} FAILED: outer document declaration hygiene"
        )
        return failures, []

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        detail = format_parse_error(exc)
        failures.append(
            Failure(GATE_OUTER, f"outer document is not well-formed: {detail}")
        )
        reporter.progress(
            f"    gate {GATE_OUTER} FAILED: outer document is not well-formed XML"
        )
        return failures, []

    headers = root.findall(HEADER_TAG)
    records = root.findall(RECORD_TAG)
    reporter.progress(
        f"    root <{root.tag}>, {len(headers)} header record(s), "
        f"{len(records)} update record(s)"
    )

    if root.tag != ROOT_TAG:
        failures.append(
            Failure(
                GATE_OUTER,
                f"unexpected root element: expected <{ROOT_TAG}>, "
                f"found <{root.tag}>",
            )
        )
    if len(headers) != 1:
        failures.append(
            Failure(
                GATE_OUTER,
                f"expected exactly 1 <{HEADER_TAG}> header record, "
                f"found {len(headers)}",
            )
        )
    if not records:
        failures.append(
            Failure(
                GATE_OUTER,
                f"expected at least 1 <{RECORD_TAG}> update record, found 0",
            )
        )
    # gate G-1: a bounded number of nested parses
    if len(records) > limits.max_payloads:
        failures.append(
            Failure(
                GATE_OUTER,
                f"{len(records)} <{RECORD_TAG}> update records exceed the "
                f"{limits.max_payloads} record ceiling",
            )
        )
        records = []

    # gate G-1: every update record carries the one header record's <sys_id>
    if len(headers) == 1 and records:
        failures.extend(check_header_linkage(headers[0], records, reporter))

    outcome = f"FAILED: {len(failures)} failure(s)" if failures else "PASS"
    reporter.progress(f"    gate {GATE_OUTER} {outcome}")
    return failures, records


def record_label(record: ET.Element, ordinal: int, total: int) -> str:
    """Return the locatable prefix for a gate G-2 message: ordinal, type, target."""
    record_type = record.findtext(RECORD_TYPE_TAG) or UNSET_FIELD
    target_name = record.findtext(RECORD_TARGET_TAG) or UNSET_FIELD
    return (
        f"record {ordinal}/{total} [{RECORD_TYPE_TAG}={record_type} "
        f"{RECORD_TARGET_TAG}={target_name}]"
    )


def payload_label(prefix: str, index: int, siblings: int) -> str:
    """Return the gate G-2 message prefix for one <payload> child of a record."""
    return f"{prefix} payload {index}/{siblings}"


def accepted_update_names(primary: ET.Element, table: str) -> list[str]:
    """Return the update name(s) the platform accepts for one payload's record.

    Two forms are accepted: <table>_<sys_id> of the payload's primary record, and
    that record's own <sys_update_name> where the payload declares one. Implements
    the gate G-2 update-name contract.
    """
    accepted: list[str] = []
    sys_id = (primary.findtext(PAYLOAD_ID_TAG) or "").strip()
    if sys_id:
        accepted.append(f"{table}_{sys_id}")
    declared = (primary.findtext(PAYLOAD_UPDATE_NAME_TAG) or "").strip()
    if declared:
        accepted.append(declared)
    return accepted


def check_payload_update_name(
    nested: ET.Element, table: str, update_name: str, label: str, tally: PayloadTally
) -> None:
    """Gate G-2 naming check: the update record names the record it carries.

    The payload's primary record is its first child element whose tag is the
    <record_update> table attribute. Its absence, a missing <sys_id> on it and an
    update name that is neither accepted form are each one failure. Diagnostics
    name the offending update name, the table and the accepted forms only.
    """
    primary = next((child for child in nested if child.tag == table), None)
    if primary is None:
        tally.add_failure(
            f"{label}: nested <{NESTED_ROOT_TAG}> for table {table} carries no "
            f"<{table}> record element"
        )
        return

    accepted = accepted_update_names(primary, table)
    if not accepted:
        tally.add_failure(
            f"{label}: the <{table}> record carries neither a non-empty "
            f"<{PAYLOAD_ID_TAG}> nor a non-empty <{PAYLOAD_UPDATE_NAME_TAG}>, so "
            "no update name can name it"
        )
        return

    if update_name not in accepted:
        tally.add_failure(
            f"{label}: <{RECORD_NAME_TAG}> is {update_name or UNSET_FIELD}, which "
            f"does not name the record the payload carries; expected "
            f"{' or '.join(accepted)}"
        )
        return

    tally.named += 1


def validate_payload_document(
    payload: ET.Element,
    label: str,
    tally: PayloadTally,
    reporter: Reporter,
    limits: Limits,
) -> ET.Element | None:
    """Run gate G-2 well-formedness over one <payload> as an independent document.

    The payload text is measured against the payload ceiling and screened for
    declaration hygiene, then parsed directly with ET.fromstring; it is not
    un-escaped again. The parsed nested document is returned when every check
    passed, and None when any of them failed.
    """
    # gate G-2: an empty payload is a failure, never a TypeError
    if payload.text is None:
        tally.add_failure(f"{label}: <{PAYLOAD_TAG}> element carries no text")
        return None

    # gate G-2: a bounded nested document
    payload_bytes = len(payload.text.encode("utf-8", errors="replace"))
    if payload_bytes > limits.max_payload_bytes:
        tally.add_failure(
            f"{label}: nested document is {payload_bytes} bytes, above the "
            f"{limits.max_payload_bytes} byte payload ceiling"
        )
        return None

    # gate G-2: declaration hygiene runs before the nested parser
    hygiene = check_declaration_hygiene(payload.text, GATE_PAYLOAD, label)
    if hygiene:
        for failure in hygiene:
            tally.add_failure(failure.detail)
        return None

    try:
        nested = ET.fromstring(payload.text)
    except ET.ParseError as exc:
        detail = format_parse_error(exc)
        tally.add_failure(f"{label}: nested document is not well-formed: {detail}")
        return None

    # gate G-2: the nested document is a <record_update> naming its table
    table = nested.get(NESTED_TABLE_ATTR)
    if nested.tag != NESTED_ROOT_TAG:
        defect = (
            f"unexpected nested root element: expected <{NESTED_ROOT_TAG}>, "
            f"found <{nested.tag}>"
        )
    elif not table:
        defect = (
            f"nested <{NESTED_ROOT_TAG}> has no non-empty "
            f"{NESTED_TABLE_ATTR} attribute"
        )
    else:
        defect = ""
    if defect:
        tally.add_failure(f"{label}: {defect}")
        return None

    tally.passed += 1
    reporter.payload_line(
        f'    {label} -> <{NESTED_ROOT_TAG} {NESTED_TABLE_ATTR}="{table}">'
    )
    return nested


def validate_payloads(
    records: list[ET.Element], reporter: Reporter, max_errors: int, limits: Limits
) -> PayloadTally:
    """Run gate G-2 over every <payload> of every record in document order.

    Every record and every one of its direct <payload> children is examined;
    max_errors caps only the diagnostics the returned tally retains. Each payload
    is measured against the payload ceiling and screened for declaration hygiene
    before it is parsed, and each well-formed payload is checked against its
    record's update name.
    """
    tally = PayloadTally(max_errors)
    total = len(records)

    for ordinal, record in enumerate(records, 1):
        prefix = record_label(record, ordinal, total)
        update_name = (record.findtext(RECORD_NAME_TAG) or "").strip()
        payloads = record.findall(PAYLOAD_TAG)
        siblings = len(payloads)
        tally.discovered += siblings

        if not payloads:
            tally.add_failure(f"{prefix}: no <{PAYLOAD_TAG}> child element")
            continue
        # gate G-2: one bundled <record_update> payload per update record
        if siblings > 1:
            tally.add_failure(
                f"{prefix}: expected exactly 1 <{PAYLOAD_TAG}> child element, "
                f"found {siblings}; every one of them is validated"
            )

        for index, payload in enumerate(payloads, 1):
            label = payload_label(prefix, index, siblings)
            nested = validate_payload_document(
                payload, label, tally, reporter, limits
            )
            if nested is not None:
                check_payload_update_name(
                    nested,
                    nested.get(NESTED_TABLE_ATTR) or "",
                    update_name,
                    label,
                    tally,
                )

    return tally


def emit_failures(outcome: FileOutcome, reporter: Reporter) -> None:
    """Write one file's retained failures to stderr, gate G-1 first.

    A closing note states how many gate G-2 diagnostics --max-errors withheld and
    the complete failure count they were withheld from.
    """
    for failure in outcome.failures:
        reporter.failure(f"FAIL [{failure.gate}] {outcome.path}: {failure.detail}")
    if outcome.payload_failures_suppressed:
        reporter.failure(
            f"NOTE [{GATE_PAYLOAD}] {outcome.path}: "
            f"{outcome.payload_failures_suppressed} further failure "
            "diagnostic(s) suppressed by --max-errors; "
            f"{outcome.payload_failure_count} gate {GATE_PAYLOAD} failure(s) "
            f"detected across all {outcome.payloads_total} payload(s) examined"
        )


def validate_file(
    path: Path,
    reporter: Reporter,
    max_errors: int,
    limits: Limits,
    gate: ParserGate | None = None,
) -> FileOutcome:
    """Validate one file against gate G-1 then gate G-2 and return its outcome."""
    outcome = FileOutcome(path)
    state = gate or parser_gate_state()
    reporter.progress(f"Validating {path} (parser {state.describe()})")

    try:
        data, truncated = read_source_bytes(path, limits.max_bytes)
    except SourceUnavailable as exc:
        outcome.io_error = str(exc)
        reporter.failure(f"ERROR [IO] {exc}")
        return outcome

    reporter.progress(
        f"  stage 1 gate {GATE_OUTER}: outer update-set document "
        f"({len(data)} byte(s))"
    )
    outer_failures, records = validate_outer(data, reporter, limits, truncated)
    outcome.outer_failures = outer_failures
    outcome.records_total = len(records)

    if not records:
        reporter.progress(
            f"  stage 2 gate {GATE_PAYLOAD}: skipped, no <{RECORD_TAG}> record "
            "to examine"
        )
        emit_failures(outcome, reporter)
        return outcome

    reporter.progress(
        f"  stage 2 gate {GATE_PAYLOAD}: {outcome.records_total} update "
        "record(s) to examine"
    )
    tally = validate_payloads(records, reporter, max_errors, limits)
    outcome.payload_failures = tally.failures
    outcome.payload_failure_count = tally.failure_count
    outcome.payload_failures_suppressed = tally.suppressed
    outcome.payloads_total = tally.discovered
    outcome.payloads_passed = tally.passed

    reporter.progress(
        f"    {tally.passed}/{tally.discovered} payload(s) well-formed across "
        f"{outcome.records_total} record(s)"
    )
    reporter.progress(
        f"    {tally.named}/{tally.discovered} update record(s) name the record "
        "their payload carries"
    )
    label = (
        f"FAILED: {tally.failure_count} failure(s)" if tally.failure_count else "PASS"
    )
    reporter.progress(f"    gate {GATE_PAYLOAD} {label}")

    emit_failures(outcome, reporter)
    return outcome


def report_summary(outcomes: list[FileOutcome], reporter: Reporter) -> int:
    """Write the terminal verdict line and return the documented exit code.

    The reported counts are the complete failure counts, independent of the
    --max-errors reporting cap.
    """
    unreadable = [item for item in outcomes if item.io_error is not None]
    validated = len(outcomes) - len(unreadable)
    outer_failures = sum(len(item.outer_failures) for item in outcomes)
    payload_failures = sum(item.payload_failure_count for item in outcomes)
    counts = (
        f"gate {GATE_OUTER} failures: {outer_failures}, "
        f"gate {GATE_PAYLOAD} failures: {payload_failures}"
    )

    if unreadable:
        reporter.verdict(
            f"FAIL: {len(unreadable)} of {len(outcomes)} path(s) unreadable, "
            f"{validated} file(s) validated, {counts}"
        )
        return EXIT_USAGE_OR_IO
    if outer_failures or payload_failures:
        reporter.verdict(f"FAIL: {validated} file(s) validated, {counts}")
        return EXIT_VALIDATION_FAILED
    reporter.verdict(
        f"PASS: {validated} file(s) validated, gate {GATE_OUTER} and "
        f"gate {GATE_PAYLOAD} satisfied"
    )
    return EXIT_OK


def default_update_set_path() -> Path:
    """Return the sibling Update Set path resolved from this script's location."""
    package_root = Path(__file__).resolve().parent.parent
    return package_root / DEFAULT_UPDATE_SET_DIR / DEFAULT_UPDATE_SET_NAME


# gate G-1 byte-prologue fixtures exercised by --self-test. Each pair is a label and
# a byte string; a label beginning "accept" must produce no failure and every other
# label must produce exactly one.
BYTE_PROLOGUE_FIXTURES: tuple[tuple[str, bytes], ...] = (
    ("accept: minimal declaration", b'<?xml version="1.0"?><unload/>'),
    (
        "accept: declaration with encoding",
        b'<?xml version="1.0" encoding="UTF-8"?><unload/>',
    ),
    ("accept: tab after the target", b'<?xml\tversion="1.0"?><unload/>'),
    ("accept: newline after the target", b'<?xml\nversion="1.0"?><unload/>'),
    ("reject: no declaration at all", b"<unload/>"),
    (
        "reject: stylesheet-only prologue",
        b'<?xml-stylesheet href="s.xsl" type="text/xsl"?><unload/>',
    ),
    (
        "reject: stylesheet before the declaration",
        b'<?xml-stylesheet href="s.xsl"?><?xml version="1.0"?><unload/>',
    ),
    ("reject: target continues past xml", b"<?xmlfoo?><unload/>"),
    ("reject: no whitespace after the target", b'<?xmlversion="1.0"?><unload/>'),
    (
        "reject: UTF-8 byte-order mark then a valid declaration",
        codecs.BOM_UTF8 + b'<?xml version="1.0"?><unload/>',
    ),
    (
        "reject: UTF-16-LE byte-order mark",
        codecs.BOM_UTF16_LE + b'<?xml version="1.0"?><unload/>',
    ),
    (
        "reject: leading newline",
        b'\n<?xml version="1.0"?><unload/>',
    ),
    (
        "reject: leading spaces",
        b'   <?xml version="1.0"?><unload/>',
    ),
    ("reject: declaration with no version", b'<?xml encoding="UTF-8"?><unload/>'),
    ("reject: unterminated declaration", b'<?xml version="1.0" ' + b"x" * 400),
    ("reject: empty file", b""),
    ("reject: truncated target", b"<?xm"),
)

# Parser-gate fixtures exercised by --self-test. Each triple is a label, an Expat
# version tuple or None for undetectable, and whether the allocation-tracker entry
# points resolve -- True present, False probed and absent, None unprobeable. A
# label beginning "accept" must be allowed and every other label must be refused.
PARSER_GATE_FIXTURES: tuple[tuple[str, tuple[int, ...] | None, bool | None], ...] = (
    ("accept: 2.7.2, the upstream fix, tracker not probed for", (2, 7, 2), False),
    ("accept: 2.8.0, above the fix", (2, 8, 0), False),
    ("accept: 3.0.0, a future major", (3, 0, 0), None),
    ("accept: 2.7.1 with the tracker backported", (2, 7, 1), True),
    ("refuse: 2.7.1 with no tracker", (2, 7, 1), False),
    ("refuse: 2.7.1 with the tracker unprobeable", (2, 7, 1), None),
    ("refuse: 2.6.4 with the tracker present but below the floor", (2, 6, 4), True),
    ("refuse: 2.6.4 with no tracker", (2, 6, 4), False),
    ("refuse: 2.4.0 with no tracker", (2, 4, 0), False),
    ("refuse: version undetectable, tracker present", None, True),
    ("refuse: version undetectable, no tracker", None, False),
    ("refuse: version undetectable, tracker unprobeable", None, None),
)


def run_parser_gate_fixtures(reporter: Reporter) -> tuple[int, int]:
    """Exercise the parser-gate fixtures and return the passed and failed counts."""
    passed = 0
    failed = 0
    for label, version, tracker in PARSER_GATE_FIXTURES:
        wants_allowed = label.startswith("accept")
        state = evaluate_parser_gate(version, tracker)
        if state.allowed == wants_allowed:
            passed += 1
            reporter.payload_line(f"  self-test PASS {label}")
            continue
        failed += 1
        reporter.failure(
            f"self-test FAIL {label}: expected "
            f"{'allowed' if wants_allowed else 'refused'}, got "
            f"{'allowed' if state.allowed else 'refused'} -- {state.reason}"
        )
    return passed, failed


def run_self_test(reporter: Reporter) -> int:
    """Exercise the byte-prologue and parser-gate fixtures and return an exit code.

    Every fixture whose label begins "accept" must be accepted -- no byte-prologue
    failure, or an allowed parser gate -- and every other fixture must be
    rejected. Nothing on disk is read and no document is parsed, so this runs on a
    runtime the parser gate would refuse to validate a file on; the runtime's own
    gate state is reported for the record rather than acted on.
    """
    passed = 0
    failed = 0
    for label, data in BYTE_PROLOGUE_FIXTURES:
        failures = check_byte_prologue(data)
        wants_pass = label.startswith("accept")
        got_pass = not failures
        if wants_pass == got_pass and (wants_pass or len(failures) == 1):
            passed += 1
            reporter.payload_line(f"  self-test PASS {label}")
            continue
        failed += 1
        outcome = "no failure" if got_pass else f"{len(failures)} failure(s)"
        reporter.failure(
            f"self-test FAIL {label}: expected "
            f"{'no failure' if wants_pass else 'exactly 1 failure'}, got {outcome}"
        )
        for failure in failures:
            reporter.failure(f"  gate {failure.gate}: {failure.detail}")
    reporter.progress(
        f"self-test: {len(BYTE_PROLOGUE_FIXTURES)} byte-prologue fixture(s), "
        f"{passed} passed, {failed} failed"
    )

    gate_passed, gate_failed = run_parser_gate_fixtures(reporter)
    passed += gate_passed
    failed += gate_failed
    reporter.progress(
        f"self-test: {len(PARSER_GATE_FIXTURES)} parser-gate fixture(s), "
        f"{gate_passed} passed, {gate_failed} failed"
    )

    state = parser_gate_state()
    reporter.progress(
        f"self-test: this runtime's parser is {state.describe()}; the gate would "
        f"{'admit' if state.allowed else 'refuse'} it -- {state.reason}"
    )
    total = len(BYTE_PROLOGUE_FIXTURES) + len(PARSER_GATE_FIXTURES)
    reporter.progress(
        f"self-test: {total} fixture(s) in total, {passed} passed, {failed} failed"
    )
    if failed:
        reporter.verdict("FAIL: self-test")
        return EXIT_VALIDATION_FAILED
    reporter.verdict("PASS: self-test")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser for the documented contract."""
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        description=(
            "Validate Boston Startup Tracker Update Set XML at the outer "
            f"update-set level (gate {GATE_OUTER}: byte prologue, "
            "well-formedness, document shape, and every update record "
            f"carrying the header <{HEADER_ID_TAG}>) and the nested "
            f"per-record payload level (gate {GATE_PAYLOAD}: nested "
            "well-formedness and each record naming the record its payload "
            "carries)."
        ),
        epilog=(
            "Before any path is opened the runtime Expat is gated: it must be at "
            f"or above {'.'.join(str(part) for part in EXPAT_FIXED_VERSION)} or "
            "expose the allocation-tracker entry points as a backport on "
            f"{'.'.join(str(part) for part in EXPAT_BACKPORT_FLOOR)}. The gate is "
            "fail-closed and cannot be overridden. Exit codes: 0 every validated "
            "file passed both gates; 1 at least one validation failure; 2 usage "
            "error, an unreadable path, or a parser gate refusal, in which case "
            "no file was validated. Code 2 takes precedence over code 1."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        help=(
            "Update Set XML file(s) to validate. With no PATH, "
            f"{DEFAULT_UPDATE_SET_DIR}/{DEFAULT_UPDATE_SET_NAME} is resolved "
            "from this script's own location."
        ),
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help=(
            "suppress per-stage progress lines; emit only failures and the "
            "final verdict"
        ),
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=(
            "emit one line per payload with its ordinal, "
            f"{RECORD_TYPE_TAG}, {RECORD_TARGET_TAG} and nested "
            f"{NESTED_TABLE_ATTR}"
        ),
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=0,
        metavar="N",
        help=(
            f"write at most N gate {GATE_PAYLOAD} failure diagnostic(s), noting "
            "how many were suppressed; every payload is examined either way and "
            "the reported counts stay complete; 0 means unlimited"
        ),
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_MAX_BYTES,
        metavar="N",
        help=(
            "refuse a source file larger than N bytes "
            f"(default {DEFAULT_MAX_BYTES})"
        ),
    )
    parser.add_argument(
        "--max-payloads",
        type=int,
        default=DEFAULT_MAX_PAYLOADS,
        metavar="N",
        help=(
            f"refuse more than N <{RECORD_TAG}> update records "
            f"(default {DEFAULT_MAX_PAYLOADS})"
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            f"exercise the gate {GATE_OUTER} byte-prologue fixtures and the "
            "parser-gate fixtures in memory, report this runtime's parser state, "
            "and exit; reads no file, parses no document and validates no Update "
            "Set, so it runs even where the parser gate would refuse a file"
        ),
    )
    parser.add_argument(
        "--max-payload-bytes",
        type=int,
        default=DEFAULT_MAX_PAYLOAD_BYTES,
        metavar="N",
        help=(
            "refuse a nested payload larger than N bytes "
            f"(default {DEFAULT_MAX_PAYLOAD_BYTES})"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate every requested path and return the documented exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        if args.paths:
            parser.error("--self-test takes no PATH")
        return run_self_test(Reporter(quiet=args.quiet, verbose=args.verbose))
    if args.max_errors < 0:
        parser.error("--max-errors must be 0 or greater")
    for name, value in (
        ("--max-bytes", args.max_bytes),
        ("--max-payloads", args.max_payloads),
        ("--max-payload-bytes", args.max_payload_bytes),
    ):
        if value < 1:
            parser.error(f"{name} must be 1 or greater")

    limits = Limits(
        max_bytes=args.max_bytes,
        max_payloads=args.max_payloads,
        max_payload_bytes=args.max_payload_bytes,
    )
    requested = [Path(candidate) for candidate in args.paths]
    paths = requested or [default_update_set_path()]
    reporter = Reporter(quiet=args.quiet, verbose=args.verbose)

    # The parser gate is evaluated once, before any path is opened and before any
    # byte reaches Expat. A refusal ends the run and validates nothing. Decision
    # D-351.
    gate = parser_gate_state()
    if not gate.allowed:
        reporter.failure(
            f"parser gate: REFUSED before parsing -- {gate.reason}. Nothing was "
            "read and nothing was validated."
        )
        fixed_text = ".".join(str(part) for part in EXPAT_FIXED_VERSION)
        floor_text = ".".join(str(part) for part in EXPAT_BACKPORT_FLOOR)
        reporter.failure(
            "  Remedy, in order. There is no option to override this gate, and "
            "editing the Update Set does not answer a refusal: the refusal is a "
            "statement about this runtime, not about the file."
        )
        reporter.failure(
            "    1. Run --self-test. It parses nothing, so it runs on any "
            "runtime, and it reports this runtime's parser state and the gate's "
            "own fixtures. Record its output as the evidence of what was refused."
        )
        reporter.failure(
            f"    2. Re-run on a runtime whose Expat is at or above {fixed_text}, "
            f"or at {floor_text} with the allocation-tracker defence backported "
            "-- a newer distribution, a container image carrying one, or another "
            "host. Confirm the runtime with --self-test before the run. This is "
            "the only route that produces gate G-1 and G-2 evidence."
        )
        reporter.failure(
            "    3. If no such runtime can be reached, gates G-1 and G-2 stay "
            "UNRECORDED and delivery is blocked. Do not substitute a parse by "
            "eye, a parse on this runtime by another tool, or an assumption from "
            "a previous run: none of those is evidence of two-level "
            "well-formedness, and parsing here is the exposure this gate exists "
            "to prevent. Record the refusal, this runtime's --self-test output, "
            "and the decision taken. The procedure is in "
            "docs/deployment-runbook.md, 'When the parser gate refuses'."
        )
        reporter.verdict("REFUSED: parser gate, no file was validated")
        return EXIT_USAGE_OR_IO

    outcomes = [
        validate_file(path, reporter, args.max_errors, limits, gate) for path in paths
    ]
    return report_summary(outcomes, reporter)


if __name__ == "__main__":
    sys.exit(main())
