from mineru_script import parse_pdfs_with_mineru
import json
import csv
import argparse
from loguru import logger
import sys

# 删除默认的标准日志配置，添加带有颜色的标准输出及保存到文件
logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>")
logger.add("process.log", rotation="10 MB", encoding="utf-8", colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>")

from pathlib import Path
from rag_script import metrics_retrieval
from termcolor import colored
from fine_tune_data_script import generate_alpaca_data, generate_sharegpt_data
from utils import extract_clean_json, process_parsed_papers_multithread
from post_process_script import clean_text
from prompts import all_metrics
from english_prompts import english_all_metrics


def process_parsed_papers(input_dir: str, output_csv: str, paper_list: list = None):
    if not paper_list:
        # 获取所有子目录（每个论文一个目录）
        paper_dirs = [d for d in Path(input_dir).iterdir() if d.is_dir()]
        # 论文名字为目录名字中第一个'.pdf'之前的部分
        paper_list = set([d.name.split('.pdf')[0] for d in paper_dirs])

        if not paper_dirs:
            logger.error(f"在目录 {input_dir} 中未找到论文目录")
            return
        logger.info(f"找到 {len(paper_dirs)} 个论文目录")

    # 存储所有结果
    fieldnames = ["文献标题"]
    fieldnames.extend(all_metrics)
    fieldnames.append("处理备注")
    # 写入CSV文件
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 写入表头
        writer.writeheader()

    for i, paper_name in enumerate(paper_list):
        # 在input_dir下找到以paper_name开头的子目录
        paper_dir = list(Path(input_dir).glob(f"{paper_name}*"))
        if not paper_dir:
            logger.error(f"未找到论文目录: {paper_name}")
            continue
        if len(paper_dir) > 1:
            logger.warning(f"找到多个匹配的论文目录，使用第一个: {paper_name}")
        paper_dir = paper_dir[0]
        logger.info(f"正在处理: {i + 1}/{len(paper_list)} {paper_name}")

        # 查找MD文件
        md_files = list(paper_dir.rglob("*.md"))

        if not md_files:
            logger.error(f"在目录 {paper_dir} 中未找到MD文件")
            continue

        # 假设每个目录只有一个MD文件，取第一个
        md_file = md_files[0]
        try:
            # 对md文件进行后处理
            result = clean_text(md_file.read_text(encoding="utf-8"))
            # 将后处理结果保存到md文件同目录下的post_process.md文件中
            result_path = paper_dir / "post_process.md"
            result_path.write_text(result, encoding="utf-8")
            logger.info(f"后处理结果已保存到: {result_path}")
            # 调用RAG函数提取相关指标
            # TODO:设置函数运行时长限制，若超过限制则跳过
            ret_metrics = metrics_retrieval(result_path)
            # 检查是否提取了所有指标
            if len(ret_metrics) != len(all_metrics):
                logger.warning(
                    f"处理 {paper_dir.name} 时，提取的指标数量不等于预期 ({len(ret_metrics)}/{len(all_metrics)})"
                )
                message = f"部分指标提取失败，共提取 {len(ret_metrics)}/{len(all_metrics)}"
            else:
                message = "成功提取所有指标"
            # 将结果写入CSV文件
            row = {"文献标题": paper_name}
            for metric in all_metrics:
                row[metric] = "提取失败"
                for ret_metric in ret_metrics:
                    if metric.startswith(ret_metric):
                        row[metric] = str(ret_metrics[ret_metric])
                        break
            row["处理备注"] = message
            # 将metrics的值写入csv文件一行的对应位置
            with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)
            logger.success(f"提取结果已保存到: {output_csv}\n")
        except Exception as e:
            logger.error(f"处理 {paper_name} 时发生错误: {e}")
            row = {"文献标题": paper_name, "处理备注": f"处理时发生错误: {e}"}
            with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row.values())

    logger.success(f"所有结果已保存到: {output_csv}\n")


def process_parsed_english_papers(input_dir: str, output_csv: str, paper_list: list = None):
    if not paper_list:
        # 获取所有子目录（每个论文一个目录）
        paper_dirs = [d for d in Path(input_dir).iterdir() if d.is_dir()]
        # 论文名字为目录名字中第一个'.'之前的部分
        paper_list = [d.name.split('.')[0] for d in paper_dirs]

        if not paper_dirs:
            logger.error(f"在目录 {input_dir} 中未找到论文目录")
            return
        logger.info(f"找到 {len(paper_dirs)} 个论文目录")

    # 存储所有结果
    fieldnames = ["paper title"]
    fieldnames.extend(english_all_metrics)
    fieldnames.append("processing notes")
    # 写入CSV文件
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # 写入表头
        writer.writeheader()

    for i, paper_name in enumerate(paper_list):
        # 在input_dir下找到以paper_name开头的子目录
        paper_dir = list(Path(input_dir).glob(f"{paper_name}*"))
        if not paper_dir:
            logger.error(f"未找到论文目录: {paper_name}")
            continue
        if len(paper_dir) > 1:
            logger.warning(f"找到多个匹配的论文目录，使用第一个: {paper_name}")
        paper_dir = paper_dir[0]
        logger.info(f"正在处理: {i + 1}/{len(paper_list)} {paper_name}")

        # 查找MD文件
        md_files = list(paper_dir.rglob("*.md"))

        if not md_files:
            logger.error(f"在目录 {paper_dir} 中未找到MD文件")
            continue

        # 假设每个目录只有一个MD文件，取第一个
        md_file = md_files[0]
        try:
            # 对md文件进行后处理
            result = clean_text(md_file.read_text(encoding="utf-8"))
            # 将后处理结果保存到md文件同目录下的post_process.md文件中
            result_path = paper_dir / "post_process.md"
            result_path.write_text(result, encoding="utf-8")
            logger.info(f"后处理结果已保存到: {result_path}")
            # 调用RAG函数提取相关指标
            # TODO:设置函数运行时长限制，若超过限制则跳过
            ret_metrics = metrics_retrieval(result_path, english=True)
            # 检查是否提取了所有指标
            if len(ret_metrics) != len(english_all_metrics):
                logger.warning(
                    f"处理 {paper_dir.name} 时，提取的指标数量不等于预期 ({len(ret_metrics)}/{len(english_all_metrics)})"
                )
                message = f"failed to extract all the metrics, extract {len(ret_metrics)}/{len(english_all_metrics)} metrics"
            else:
                message = "successfully extract all the metrics"
            # 将结果写入CSV文件
            row = {"paper title": paper_name}
            for metric in english_all_metrics:
                row[metric] = "failed to extract"
                for ret_metric in ret_metrics:
                    if metric.startswith(ret_metric):
                        row[metric] = str(ret_metrics[ret_metric])
                        break
            row["processing notes"] = message
            # 将metrics的值写入csv文件一行的对应位置
            with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(row)
            logger.success(f"提取结果已保存到: {output_csv}\n")
        except Exception as e:
            logger.error(f"处理 {paper_name} 时发生错误: {e}")
            row = {"paper title": paper_name, "processing notes": f"error happened when processing: {e}"}
            with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row.values())

    logger.success(f"所有结果已保存到: {output_csv}\n")


if __name__ == "__main__":
    print (len(all_metrics))
    print (len(english_all_metrics))
    process_parsed_english_papers("../英文文献-解析后", "盐碱地改良英文文献指标汇总.csv")