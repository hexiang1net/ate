"""文档解析生成测试计划 - 主入口。"""
import logging
from typing import Optional

from ..seq_to_excel.testcase_model import TestCaseReport
from ..seq_to_excel.excel_generator import ExcelGenerator
from .doc_reader import read_document
from .llm_client import create_llm_client
from .prompt_builder import build_prompt, build_multimodal_prompt, parse_llm_response
from .testcase_extractor import extract_test_cases

logger = logging.getLogger(__name__)


class TestPlanGenerator:
    """从文档生成测试计划 Excel。"""

    def generate(
        self,
        doc_path: str,
        output_xlsx: str,
        provider: str = None,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        verbose: bool = False,
        use_images: bool = True,
    ) -> TestCaseReport:
        """从文档生成测试计划。

        Args:
            doc_path: 输入文档路径（支持 .docx, .xlsx, .xls, .pdf, .md, .txt）
            output_xlsx: 输出 Excel 路径
            provider: LLM 提供商（claude/openai），默认从环境变量读取
            api_key: API Key，默认从环境变量读取
            model: 模型名称，默认使用提供商默认模型
            base_url: OpenAI 兼容接口的 base URL
            verbose: 是否输出详细信息
            use_images: 是否提取和分析图片（禁用可节省成本）

        Returns:
            TestCaseReport 生成的测试计划报告
        """
        # 1. 读取文档
        if verbose:
            print(f"读取文档: {doc_path}")
        content = read_document(doc_path, extract_images=use_images)
        if verbose:
            print(f"文档内容长度: {len(content.text)} 字符")
            print(f"提取到图片数量: {len(content.images)} 张")

        # 2. 创建 LLM 客户端
        if verbose:
            print(f"创建 LLM 客户端...")
        llm = create_llm_client(provider=provider, api_key=api_key, model=model, base_url=base_url)

        # 3. 构建提示词（根据是否有多模态支持和图片选择模式）
        use_multimodal = use_images and content.images and llm.supports_images
        if use_multimodal:
            if verbose:
                print(f"使用多模态模式，{len(content.images)} 张图片将发送给 LLM")
            # 确定 provider 格式
            from .llm_client import ClaudeClient
            provider_format = "claude" if isinstance(llm, ClaudeClient) else "openai"
            messages = build_multimodal_prompt(content.text, content.images, provider_format)
        else:
            if verbose:
                if content.images and not llm.supports_images:
                    print(f"LLM 不支持图片，回退到纯文本模式")
                elif not content.images:
                    print(f"文档中未提取到图片，使用纯文本模式")
                else:
                    print(f"图片提取已禁用，使用纯文本模式")
            messages = build_prompt(content.text)

        if verbose:
            print(f"提示词消息数: {len(messages)}")

        # 4. 调用 LLM
        if verbose:
            print(f"调用 LLM 解析文档...")
        response = llm.chat(messages)
        if verbose:
            print(f"LLM 响应长度: {len(response)} 字符")

        # 5. 解析响应
        data = parse_llm_response(response)
        report = extract_test_cases(data, doc_path)
        if verbose:
            print(f"提取到 {len(report.test_cases)} 个测试项, {len(report.variables)} 个变量")

        # 6. 生成 Excel
        ExcelGenerator().generate(report, output_xlsx)
        if verbose:
            print(f"Excel 已保存: {output_xlsx}")

        return report
