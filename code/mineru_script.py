import os
import subprocess
import argparse
import shutil
from pathlib import Path
from termcolor import colored


def parse_pdfs_with_mineru(input_base_dir, output_base_dir):
    """
    解析指定目录中的所有PDF文件, 并将结果保存到输出目录中
    input_base_dir: 包含PDF文件的输入目录
    output_base_dir: 输出基础目录
    """
    # 查找所有PDF文件
    pdf_files = list(Path(input_base_dir).rglob("*.pdf"))

    if not pdf_files:
        print(colored(f"在目录 {input_base_dir} 中未找到PDF文件", "red"))
        return

    print(colored(f"找到 {len(pdf_files)} 个PDF文件", "green"))

    # 创建输出目录
    os.makedirs(output_base_dir, exist_ok=True)

    # 处理每个PDF文件
    for i, pdf_path in enumerate(pdf_files):
        # 获取不带扩展名的文件名
        paper_name = pdf_path.stem
        print(colored(f"正在处理: {i + 1}/{len(pdf_files)} {paper_name}", "blue"))

        try:
            # 调用minerU进行解析
            cmd = [
                "mineru",
                "-p",
                str(pdf_path),
                "-o",
                str(output_base_dir),
                # "-b",
                # "vlm-vllm-engine",
            ]

            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # 检查执行结果
            if result.returncode == 0:
                print(colored(f"成功解析: {paper_name}", "green"))

                # 复制原始PDF到输出目录（可选）
                # shutil.copy2(pdf_path, output_dir / pdf_path.name)
            else:
                print(colored(f"解析失败: {paper_name}", "red"))
                print(colored(f"错误信息: {result.stderr}", "red"))

        except subprocess.CalledProcessError as e:
            print(colored(f"处理 {paper_name} 时发生错误: {e}", "red"))
        except Exception as e:
            print(colored(f"处理 {paper_name} 时发生未知错误: {e}", "red"))
    print(colored("所有文件处理完成", "green"))


if __name__ == "__main__":
    parse_pdfs_with_mineru(
        input_base_dir="/home/hezg/saline-alkali-soil_llm/盐碱地论文-12篇/不同改良措施对卤阳湖盐碱地土壤性质及玉米产量的影响_徐国凤",
        output_base_dir="../test_mineru",
    )