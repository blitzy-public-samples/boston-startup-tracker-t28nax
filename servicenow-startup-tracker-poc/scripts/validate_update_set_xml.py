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

Parser safety. The validator reads untrusted XML with the standard library's Expat
binding, so three structural defences bound the work it will do at both levels, in
place of trusting the parser to survive hostile input:

    declaration hygiene   a document declaring a document type or an entity, or
                          referencing any entity other than the five predefined
                          names and numeric character references, is refused
                          before it reaches the parser. Without a document type
                          declaration an internal entity cannot be declared, which
                          removes the entity expansion and external entity vectors
                          outright rather than relying on a patched Expat.
    size ceilings         the source file is read through a byte cap, and every
                          nested payload is measured against a payload cap, so no
                          single document can exhaust memory.
    count ceiling         the number of update records is capped, so a file cannot
                          force an unbounded number of nested parses.

Every ceiling is adjustable from the command line. The runtime Expat version is
reported alongside the first progress line so the posture is visible in the log.

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
    1   at least one validation failure at either level.
    2   usage error, or a path that is missing, not a regular file, or unreadable.
        Code 2 takes precedence over code 1 when both occur.

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

# gate G-1: byte-order marks rejected on the raw bytes (AAP section 0.8.1)
BYTE_ORDER_MARKS = (
    ("UTF-8", codecs.BOM_UTF8),
    ("UTF-16-LE", codecs.BOM_UTF16_LE),
    ("UTF-16-BE", codecs.BOM_UTF16_BE),
)

DEFAULT_UPDATE_SET_DIR = "update-set"
DEFAULT_UPDATE_SET_NAME = "x_bst_startuptrk_boston_startup_tracker_update_set.xml"

# Parser safety ceilings. The delivered Update Set is roughly 1.3 MB across about
# 300 records, so each default leaves ample headroom while bounding hostile input.
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


class SourceUnavailable(Exception):
    """A path is missing, not a regular file, or unreadable (exit code 2)."""


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

    Applied to both XML levels before either is parsed. Without a document type
    declaration no internal entity can be declared, so rejecting these three forms
    removes the entity expansion and external entity vectors at the source instead
    of relying on the parser to survive them.
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


def check_byte_prologue(data: bytes) -> list[Failure]:
    """Gate G-1 byte checks: no byte-order mark, and the XML declaration first.

    Diagnostics name the violated condition, the byte count and the offset of the
    first differing byte only; input content is never written to any stream, per
    the gate G-5 secret-hygiene requirement.
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
    if not data.startswith(XML_DECLARATION_PREFIX):
        prefix = XML_DECLARATION_PREFIX.decode("ascii")
        offset = first_mismatch_offset(data, XML_DECLARATION_PREFIX)
        return [
            Failure(
                GATE_OUTER,
                "XML declaration is not first: the file must begin with "
                f"{prefix!r}; {len(data)} byte(s) read, first byte differing "
                f"from the declaration at offset {offset}",
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
        reporter.progress(f"    gate {GATE_OUTER} FAILED: source exceeds the byte ceiling")
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

    A customer update is named after the record it carries: <table>_<sys_id> of
    the payload's primary record, or that record's own <sys_update_name> where the
    payload declares one. An update named anything else cannot be resolved by the
    platform when another record in the same update set references it.
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
    path: Path, reporter: Reporter, max_errors: int, limits: Limits
) -> FileOutcome:
    """Validate one file against gate G-1 then gate G-2 and return its outcome."""
    outcome = FileOutcome(path)
    reporter.progress(f"Validating {path} (parser {expat.EXPAT_VERSION})")

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
            "Exit codes: 0 every validated file passed both gates; 1 at least "
            "one validation failure; 2 usage error or an unreadable path. "
            "Code 2 takes precedence over code 1."
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
    outcomes = [
        validate_file(path, reporter, args.max_errors, limits) for path in paths
    ]
    return report_summary(outcomes, reporter)


if __name__ == "__main__":
    sys.exit(main())
