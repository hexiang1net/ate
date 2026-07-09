"""CLI 入口 - 从文档生成测试计划。"""
import sys
import argparse
from pathlib import Path

from .testplan_generator import TestPlanGenerator


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="从测试文档生成 ATE 测试计划 Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 从 Word 文档生成
  python -m teststand.agents.doc_to_testplan.cli "D:\\docs\\test_spec.docx"

  # 从 PDF 生成，指定输出路径
  python -m teststand.agents.doc_to_testplan.cli "D:\\docs\\spec.pdf" -o "D:\\output\\testplan.xlsx"

  # 使用 OpenAI API
  python -m teststand.agents.doc_to_testplan.cli "D:\\docs\\spec.md" --provider openai --api-key sk-xxx

  # 使用自定义 base_url（OpenAI 兼容接口）
  python -m teststand.agents.doc_to_testplan.cli "D:\\docs\\spec.docx" --provider openai --base-url http://localhost:8080/v1 --api-key test

  # 禁用图片提取（纯文本模式，节省成本）
  python -m teststand.agents.doc_to_testplan.cli "D:\\docs\\spec.pdf" --no-images
        """,
    )
    parser.add_argument("document", type=str, help="输入文档路径 (.docx, .doc, .xlsx, .xls, .pdf, .html, .htm, .md, .txt)")
    parser.add_argument("-o", "--output", type=str, help="输出 Excel 路径 (默认: <文档名>_TestPlan.xlsx)")
    parser.add_argument("--provider", type=str, choices=["claude", "openai"],
                        help="LLM 提供商 (默认: 从环境变量或自动检测)")
    parser.add_argument("--api-key", type=str, help="API Key (默认: 从环境变量 LLM_API_KEY 读取)")
    parser.add_argument("--model", type=str, help="模型名称 (默认: 使用提供商默认模型)")
    parser.add_argument("--base-url", type=str, help="OpenAI 兼接接口的 base URL")
    parser.add_argument("--no-images", action="store_true",
                        help="禁用图片提取，使用纯文本模式（节省 API 成本）")
    parser.add_argument("-v", "--verbose", action="store_true", help="输出详细信息")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    doc_path = Path(args.document)
    if not doc_path.exists():
        print(f"Error: 文件不存在: {doc_path}")
        sys.exit(1)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = doc_path.parent / f"{doc_path.stem}_TestPlan.xlsx"

    try:
        generator = TestPlanGenerator()
        report = generator.generate(
            doc_path=str(doc_path),
            output_xlsx=str(output_path),
            provider=args.provider,
            api_key=args.api_key,
            model=args.model,
            base_url=args.base_url,
            verbose=args.verbose,
            use_images=not args.no_images,
        )

        # 输出摘要
        total = len(report.test_cases)
        startup = sum(1 for tc in report.test_cases if tc.step == "startup")
        main_count = sum(1 for tc in report.test_cases if tc.step == "main")
        cleanup = sum(1 for tc in report.test_cases if tc.step == "cleanup")

        print(f"\n测试计划生成成功!")
        print(f"  文档: {doc_path.name}")
        print(f"  总测试项: {total}")
        print(f"    - Startup: {startup}")
        print(f"    - Main: {main_count}")
        print(f"    - Cleanup: {cleanup}")
        print(f"  变量数: {len(report.variables)}")
        print(f"  输出: {output_path}")

    except ImportError as e:
        print(f"缺少依赖: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"参数错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
