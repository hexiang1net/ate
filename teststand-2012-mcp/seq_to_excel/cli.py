"""CLI entry point for ATE test case generation agent."""
import sys
import argparse
from pathlib import Path

from .testcase_agent import TestCaseAgent
from ...exception.engine_exception import EngineException


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate ATE test case Excel report from NI TestStand sequence file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report for a sequence file
  python -m teststand.agents.testcase "D:\\TestSequences\\MySequence.seq"

  # Specify output path
  python -m teststand.agents.testcase "D:\\TestSequences\\MySequence.seq" -o "D:\\output\\report.xlsx"

  # Verbose output
  python -m teststand.agents.testcase "D:\\TestSequences\\MySequence.seq" -v
        """
    )
    parser.add_argument("sequence_file", type=str, help="Path to .seq file")
    parser.add_argument("-o", "--output", type=str,
                       help="Output Excel file path (default: <seq_file>_ATE_TestCases.xlsx)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose output")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    seq_file = Path(args.sequence_file)
    if not seq_file.exists():
        print(f"Error: Sequence file not found: {seq_file}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = seq_file.parent / f"{seq_file.stem}_ATE_TestCases.xlsx"

    if args.verbose:
        print(f"Opening sequence file: {seq_file}")
        print(f"Output will be saved to: {output_path}")

    try:
        agent = TestCaseAgent()
        report = agent.generate_report(str(seq_file), str(output_path))

        # Summary
        total_cases = len(report.test_cases)
        startup_count = sum(1 for tc in report.test_cases if tc.step == "startup")
        main_count = sum(1 for tc in report.test_cases if tc.step == "main")
        cleanup_count = sum(1 for tc in report.test_cases if tc.step == "cleanup")

        print(f"\nReport generated successfully!")
        print(f"  Sequence: {report.sequence_name}")
        print(f"  Total test cases: {total_cases}")
        print(f"    - Startup: {startup_count}")
        print(f"    - Main: {main_count}")
        print(f"    - Cleanup: {cleanup_count}")
        print(f"  Output: {output_path}")

        sys.exit(0)

    except EngineException as e:
        print(f"TestStand engine error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()