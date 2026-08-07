#!/usr/bin/env python3
"""Two-level well-formedness validator for the Boston Startup Tracker Update Set XML.

Implements the prompt section 11.0 requirement to validate the deliverable at both
the outer update-set level and the nested per-record payload level before delivery,
expressed as pre-delivery gates G-1 and G-2 of AAP section 0.11.1:

    gate G-1  outer update-set level: byte prologue (no byte-order mark, XML
              declaration first), XML well-formedness, and the document shape
              <unload> / exactly one <sys_remote_update_set> / at least one
              <sys_update_xml>.
    gate G-2  nested per-record payload level: the text of every <payload> parsed
              as an independent document whose root is <record_update> carrying a
              non-empty table attribute.

Gates G-3 referential integrity, G-4 scope containment, G-5 secret hygiene and
G-6 field-list fidelity are outside this validator's scope (AAP section 0.3.1.1).

Usage:
    validate_update_set_xml.py [-q | -v] [--max-errors N] [PATH ...]

With no PATH, the sibling Update Set
update-set/x_bst_startuptrk_boston_startup_tracker_update_set.xml is resolved
relative to this script's own directory.

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
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

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
UNSET_FIELD = "<unset>"

XML_DECLARATION_PREFIX = b"<?xml"
PROLOGUE_SAMPLE_BYTES = 24

# gate G-1: byte-order marks rejected on the raw bytes (AAP section 0.8.1)
BYTE_ORDER_MARKS = (
    ("UTF-8", codecs.BOM_UTF8),
    ("UTF-16-LE", codecs.BOM_UTF16_LE),
    ("UTF-16-BE", codecs.BOM_UTF16_BE),
)

DEFAULT_UPDATE_SET_DIR = "update-set"
DEFAULT_UPDATE_SET_NAME = "x_bst_startuptrk_boston_startup_tracker_update_set.xml"


class SourceUnavailable(Exception):
    """A path is missing, not a regular file, or unreadable (exit code 2)."""


class Failure:
    """One validation failure attributed to gate G-1 or gate G-2."""

    __slots__ = ("detail", "gate")

    def __init__(self, gate: str, detail: str) -> None:
        self.gate = gate
        self.detail = detail


class FileOutcome:
    """Per-file counters and failures produced by validate_file."""

    __slots__ = (
        "io_error",
        "outer_failures",
        "path",
        "payload_failures",
        "payloads_examined",
        "payloads_passed",
        "payloads_total",
    )

    def __init__(self, path: Path) -> None:
        self.path = path
        self.io_error: str | None = None
        self.outer_failures: list[Failure] = []
        self.payload_failures: list[Failure] = []
        self.payloads_total = 0
        self.payloads_passed = 0
        self.payloads_examined = 0

    @property
    def failures(self) -> list[Failure]:
        """Every failure for this file, gate G-1 first then gate G-2."""
        return self.outer_failures + self.payload_failures


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


def read_source_bytes(path: Path) -> bytes:
    """Return the raw bytes of path, raising SourceUnavailable for exit-2 cases."""
    try:
        if not path.exists():
            raise SourceUnavailable(f"path does not exist: {path}")
        if not path.is_file():
            raise SourceUnavailable(f"path is not a regular file: {path}")
        return path.read_bytes()
    except OSError as exc:
        raise SourceUnavailable(
            f"path is not readable: {path} ({type(exc).__name__}: {exc})"
        ) from exc


def check_byte_prologue(data: bytes) -> list[Failure]:
    """Gate G-1 byte checks: no byte-order mark, and the XML declaration first."""
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
        sample = data[:PROLOGUE_SAMPLE_BYTES]
        return [
            Failure(
                GATE_OUTER,
                "XML declaration is not first: the file must begin with "
                f"{prefix!r}, found {sample!r}",
            )
        ]
    return []


def validate_outer(
    data: bytes, reporter: Reporter
) -> tuple[list[Failure], list[ET.Element]]:
    """Run gate G-1 over the outer document, returning failures and update records."""
    failures = check_byte_prologue(data)

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
    # gate G-1: exactly one header record
    if len(headers) != 1:
        failures.append(
            Failure(
                GATE_OUTER,
                f"expected exactly 1 <{HEADER_TAG}> header record, "
                f"found {len(headers)}",
            )
        )
    # gate G-1: at least one update record
    if not records:
        failures.append(
            Failure(
                GATE_OUTER,
                f"expected at least 1 <{RECORD_TAG}> update record, found 0",
            )
        )

    outcome = f"FAILED: {len(failures)} failure(s)" if failures else "PASS"
    reporter.progress(f"    gate {GATE_OUTER} {outcome}")
    return failures, records


def payload_label(record: ET.Element, ordinal: int, total: int) -> str:
    """Return the locatable prefix for a gate G-2 message: ordinal, type, target."""
    record_type = record.findtext(RECORD_TYPE_TAG) or UNSET_FIELD
    target_name = record.findtext(RECORD_TARGET_TAG) or UNSET_FIELD
    return (
        f"payload {ordinal}/{total} [{RECORD_TYPE_TAG}={record_type} "
        f"{RECORD_TARGET_TAG}={target_name}]"
    )


def validate_payloads(
    records: list[ET.Element], reporter: Reporter, max_errors: int
) -> tuple[list[Failure], int, int]:
    """Run gate G-2 over every record in document order.

    Each <payload> text is parsed directly with ET.fromstring and is not
    un-escaped again. Returns the failures, the number of payloads that passed,
    and the number examined.
    """
    failures: list[Failure] = []
    total = len(records)
    passed = 0
    examined = 0

    for ordinal, record in enumerate(records, 1):
        if max_errors and len(failures) >= max_errors:
            break
        examined += 1
        label = payload_label(record, ordinal, total)

        payload = record.find(PAYLOAD_TAG)
        if payload is None:
            failures.append(
                Failure(GATE_PAYLOAD, f"{label}: no <{PAYLOAD_TAG}> child element")
            )
            continue
        # gate G-2: an empty payload is a failure, never a TypeError
        if payload.text is None:
            failures.append(
                Failure(
                    GATE_PAYLOAD,
                    f"{label}: <{PAYLOAD_TAG}> element carries no text",
                )
            )
            continue

        try:
            nested = ET.fromstring(payload.text)
        except ET.ParseError as exc:
            detail = format_parse_error(exc)
            failures.append(
                Failure(
                    GATE_PAYLOAD,
                    f"{label}: nested document is not well-formed: {detail}",
                )
            )
            continue

        if nested.tag != NESTED_ROOT_TAG:
            failures.append(
                Failure(
                    GATE_PAYLOAD,
                    f"{label}: unexpected nested root element: expected "
                    f"<{NESTED_ROOT_TAG}>, found <{nested.tag}>",
                )
            )
            continue

        table = nested.get(NESTED_TABLE_ATTR)
        if not table:
            failures.append(
                Failure(
                    GATE_PAYLOAD,
                    f"{label}: nested <{NESTED_ROOT_TAG}> has no non-empty "
                    f"{NESTED_TABLE_ATTR} attribute",
                )
            )
            continue

        passed += 1
        reporter.payload_line(
            f'    {label} -> <{NESTED_ROOT_TAG} {NESTED_TABLE_ATTR}="{table}">'
        )

    return failures, passed, examined


def emit_failures(outcome: FileOutcome, reporter: Reporter) -> None:
    """Write every collected failure for one file to stderr, gate G-1 first."""
    for failure in outcome.failures:
        reporter.failure(f"FAIL [{failure.gate}] {outcome.path}: {failure.detail}")


def validate_file(path: Path, reporter: Reporter, max_errors: int) -> FileOutcome:
    """Validate one file against gate G-1 then gate G-2 and return its outcome."""
    outcome = FileOutcome(path)
    reporter.progress(f"Validating {path}")

    try:
        data = read_source_bytes(path)
    except SourceUnavailable as exc:
        outcome.io_error = str(exc)
        reporter.failure(f"ERROR [IO] {exc}")
        return outcome

    reporter.progress(
        f"  stage 1 gate {GATE_OUTER}: outer update-set document "
        f"({len(data)} byte(s))"
    )
    outer_failures, records = validate_outer(data, reporter)
    outcome.outer_failures = outer_failures
    outcome.payloads_total = len(records)

    if not records:
        reporter.progress(
            f"  stage 2 gate {GATE_PAYLOAD}: skipped, no <{RECORD_TAG}> record "
            "to examine"
        )
        emit_failures(outcome, reporter)
        return outcome

    reporter.progress(
        f"  stage 2 gate {GATE_PAYLOAD}: {outcome.payloads_total} nested "
        "payload document(s)"
    )
    payload_failures, passed, examined = validate_payloads(
        records, reporter, max_errors
    )
    outcome.payload_failures = payload_failures
    outcome.payloads_passed = passed
    outcome.payloads_examined = examined

    reporter.progress(f"    {passed}/{outcome.payloads_total} payload(s) well-formed")
    if examined < outcome.payloads_total:
        reporter.progress(
            f"    stopped after {len(payload_failures)} failure(s) per "
            f"--max-errors; examined {examined} of {outcome.payloads_total} "
            "payload(s)"
        )
    label = (
        f"FAILED: {len(payload_failures)} failure(s)" if payload_failures else "PASS"
    )
    reporter.progress(f"    gate {GATE_PAYLOAD} {label}")

    emit_failures(outcome, reporter)
    return outcome


def report_summary(outcomes: list[FileOutcome], reporter: Reporter) -> int:
    """Write the terminal verdict line and return the documented exit code."""
    unreadable = [item for item in outcomes if item.io_error is not None]
    validated = len(outcomes) - len(unreadable)
    outer_failures = sum(len(item.outer_failures) for item in outcomes)
    payload_failures = sum(len(item.payload_failures) for item in outcomes)
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
            f"update-set level (gate {GATE_OUTER}) and the nested per-record "
            f"payload level (gate {GATE_PAYLOAD})."
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
        help="stop collecting payload failures after N; 0 means unlimited",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Validate every requested path and return the documented exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.max_errors < 0:
        parser.error("--max-errors must be 0 or greater")

    requested = [Path(candidate) for candidate in args.paths]
    paths = requested or [default_update_set_path()]
    reporter = Reporter(quiet=args.quiet, verbose=args.verbose)
    outcomes = [validate_file(path, reporter, args.max_errors) for path in paths]
    return report_summary(outcomes, reporter)


if __name__ == "__main__":
    sys.exit(main())
