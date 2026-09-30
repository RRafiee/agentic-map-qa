"""
run_calendar_pipeline_agent.py

Single-entry pipeline for the EEECS MAP calendar visualisation workflow.

This wrapper deliberately keeps the specialist agents separate:
  1) calendar_visualisation_agent.py
  2) validate_calendar_visual_check.py
  3) compact_calendar_html_agent.py

Routine use:
    .\.venv\Scripts\python.exe src\agents\run_calendar_pipeline_agent.py --exclude-module ELE3030

Optional:
    .\.venv\Scripts\python.exe src\agents\run_calendar_pipeline_agent.py --exclude-module ELE3030 --open

Place this file in:
    src\agents\run_calendar_pipeline_agent.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Optional


DEFAULT_OUTPUT_DIR = Path("outputs") / "2026_27_readiness_03Sep" / "calendar_visual_check"
DEFAULT_COMPACT_HTML = DEFAULT_OUTPUT_DIR / "MAP_Calendar_2026_27.html"
DEFAULT_EVENTS_CSV = DEFAULT_OUTPUT_DIR / "MAP_Calendar_Visual_Check_Events.csv"


def project_root_from_this_file() -> Path:
    """Return the repository root when this file lives in src/agents/."""
    return Path(__file__).resolve().parents[2]


def run_step(
    label: str,
    command: List[str],
    cwd: Path,
    continue_on_error: bool = False,
) -> int:
    """Run one pipeline command and stream output to the terminal."""
    print("\n" + "=" * 78)
    print(f"STEP: {label}")
    print("COMMAND:")
    print(" ".join(command))
    print("=" * 78)

    completed = subprocess.run(command, cwd=str(cwd))

    if completed.returncode != 0:
        print(f"\nFAILED: {label} exited with code {completed.returncode}")
        if not continue_on_error:
            raise SystemExit(completed.returncode)

    print(f"\nDONE: {label}")
    return completed.returncode


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        raise SystemExit(
            f"\nERROR: Missing {description}:\n  {path}\n"
            "Check that you are running from the project root and that the file exists."
        )


def file_size_report(path: Path) -> str:
    size_bytes = path.stat().st_size
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    if size_mb >= 1:
        return f"{size_bytes:,} bytes ({size_mb:.2f} MB)"
    return f"{size_bytes:,} bytes ({size_kb:.1f} KB)"


def open_file(path: Path) -> None:
    """Open the output HTML using the OS default application."""
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full EEECS MAP calendar visualisation pipeline."
    )

    parser.add_argument(
        "--exclude-module",
        action="append",
        default=[],
        metavar="MODULE_CODE",
        help=(
            "Module code to exclude from the compact calendar HTML. "
            "Can be used more than once, e.g. --exclude-module ELE3030."
        ),
    )

    parser.add_argument(
        "--skip-visualisation",
        action="store_true",
        help="Skip calendar_visualisation_agent.py and reuse existing event CSV outputs.",
    )

    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validate_calendar_visual_check.py. Not recommended for final outputs.",
    )

    parser.add_argument(
        "--skip-compact",
        action="store_true",
        help="Skip compact_calendar_html_agent.py. Useful when testing only visualisation/validation.",
    )

    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated compact HTML after the pipeline completes.",
    )

    parser.add_argument(
        "--continue-on-validation-error",
        action="store_true",
        help=(
            "Continue to compact HTML generation even if the validation step returns a non-zero exit code. "
            "Use only for investigation, not final outputs."
        ),
    )

    parser.add_argument(
        "--output-html",
        default=str(DEFAULT_COMPACT_HTML),
        help=(
            "Expected compact HTML output path, relative to project root unless absolute. "
            f"Default: {DEFAULT_COMPACT_HTML}"
        ),
    )

    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)

    root = project_root_from_this_file()
    agents_dir = root / "src" / "agents"

    visualisation_agent = agents_dir / "calendar_visualisation_agent.py"
    validation_agent = agents_dir / "validate_calendar_visual_check.py"
    compact_agent = agents_dir / "compact_calendar_html_agent.py"

    output_html = Path(args.output_html)
    if not output_html.is_absolute():
        output_html = root / output_html

    print("EEECS MAP Calendar Pipeline")
    print("-" * 78)
    print(f"Project root:      {root}")
    print(f"Python executable: {sys.executable}")
    print(f"Output HTML:       {output_html}")
    if args.exclude_module:
        print(f"Excluded modules:  {', '.join(args.exclude_module)}")
    else:
        print("Excluded modules:  None")

    require_file(visualisation_agent, "calendar visualisation agent")
    require_file(validation_agent, "validation agent")
    require_file(compact_agent, "compact calendar HTML agent")

    if not args.skip_visualisation:
        run_step(
            "Generate visualisation CSV/HTML outputs",
            [sys.executable, str(visualisation_agent.relative_to(root))],
            cwd=root,
        )
    else:
        print("\nSKIPPED: Generate visualisation CSV/HTML outputs")

    if not args.skip_validation:
        run_step(
            "Validate visualisation outputs",
            [sys.executable, str(validation_agent.relative_to(root))],
            cwd=root,
            continue_on_error=args.continue_on_validation_error,
        )
    else:
        print("\nSKIPPED: Validate visualisation outputs")

    if not args.skip_compact:
        compact_cmd = [sys.executable, str(compact_agent.relative_to(root))]
        for module_code in args.exclude_module:
            compact_cmd.extend(["--exclude-module", module_code])

        run_step(
            "Generate compact standalone HTML",
            compact_cmd,
            cwd=root,
        )
    else:
        print("\nSKIPPED: Generate compact standalone HTML")

    if not args.skip_compact:
        require_file(output_html, "compact output HTML")
        print("\n" + "=" * 78)
        print("PIPELINE COMPLETE")
        print("=" * 78)
        print(f"Compact HTML: {output_html}")
        print(f"Actual size:  {file_size_report(output_html)}")

        if args.open:
            print("Opening compact HTML...")
            open_file(output_html)
    else:
        print("\nPIPELINE COMPLETE: compact HTML generation was skipped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
