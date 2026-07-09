"""CLI entry point for Excel to TestStand sequence file converter."""
import sys
import argparse
from pathlib import Path

from .excel_parser import ExcelParser
from .seq_generator import SeqGenerator


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert ATETestPlan Excel template to NI TestStand sequence file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert Excel template to sequence file
  python -m teststand.agents.excel_to_seq "D:\\Templates\\ATETestPlan.xlsx"

  # Specify output path
  python -m teststand.agents.excel_to_seq "D:\\Templates\\ATETestPlan.xlsx" -o "D:\\Output\\Test.seq"

  # Verbose output
  python -m teststand.agents.excel_to_seq "D:\\Templates\\ATETestPlan.xlsx" -v
        """
    )
    parser.add_argument("excel_file", type=str, help="Path to ATETestPlan Excel file")
    parser.add_argument("-o", "--output", type=str,
                       help="Output .seq file path (default: <excel_file>.seq)")
    parser.add_argument("-s", "--sequence-name", type=str, default="MainSequence",
                       help="Main sequence name (default: MainSequence)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose output")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    excel_file = Path(args.excel_file)
    if not excel_file.exists():
        print(f"Error: Excel file not found: {excel_file}")
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = excel_file.with_suffix('.seq')

    if args.verbose:
        print(f"Parsing Excel file: {excel_file}")
        print(f"Output will be saved to: {output_path}")

    try:
        # Parse Excel
        parser = ExcelParser()
        test_cases, vi_params, variables = parser.parse(str(excel_file))

        if args.verbose:
            print(f"Parsed {len(test_cases)} test cases")
            print(f"Parsed {len(vi_params)} VI parameter entries")
            print(f"Parsed {len(variables)} variables")

        # Generate sequence file
        generator = SeqGenerator()
        generator.generate(test_cases, vi_params, str(output_path), args.sequence_name,
                          variables=variables)

        print(f"\nSequence file generated successfully!")
        print(f"  Sequence name: {args.sequence_name}")
        print(f"  Test cases: {len(test_cases)}")
        print(f"  Output: {output_path}")

        sys.exit(0)

    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()