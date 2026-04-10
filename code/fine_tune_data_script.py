import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Any

import chardet
import openai
import time
import re
import json
import os
from prompts import *
from english_prompts import *
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain.text_splitter import RecursiveCharacterTextSplitter
from model_clients import get_local_deepseek_model_client, get_deepseek_model_client
from utils import extract_clean_json
from termcolor import colored
import pandas as pd


"""将单个问答对保存到文件"""
def save_to_file(qa_pair, output_path):
    try:
        # 读取现有数据或初始化空列表
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []
        
        # 确保是列表
        if not isinstance(existing_data, list):
            existing_data = [existing_data]
        
        # 追加新数据
        existing_data.append(qa_pair)
        
        # 写回文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(colored(f"保存文件时出错: {e}"))


def validate_alpaca_data_format(data):
    """
    验证数据是否符合Alpaca格式要求
    """
    if not isinstance(data, dict):
        return False
    if not "instruction" in data.keys():
        return False
    if not "input" in data.keys():
        return False
    if not "reason" in data.keys():
        return False
    if not "output" in data.keys():
        return False
    return True


def validate_sharegpt_data_format(data):
    """
    验证数据是否符合ShareGPT格式要求
    """
    # 1. 检查顶层结构
    if not isinstance(data, dict):
        print("数据必须是字典类型")
        return False
        
    # 2. 检查conversations字段
    if "conversations" not in data:
        print("缺少必需的 'conversations' 字段")
        return False
        
    conversations = data["conversations"]
    
    if not isinstance(conversations, list):
        print("'conversations' 必须是列表类型")
        return False

    # 3. 检查每个对话项的结构
    expected_speakers = ["human", "gpt"]

    for i, conv in enumerate(conversations):
        if not isinstance(conv, dict):
            print(f"第 {i+1} 轮对话必须是字典类型")
            return False

        # 检查必需的字段
        if "from" not in conv:
            print(f"第 {i+1} 轮对话缺少 'from' 字段")
            return False
        elif conv["from"] != expected_speakers[i % 2]:
            print(f"第 {i+1} 轮对话的说话者应该是 '{expected_speakers[i % 2]}'，但实际是 '{conv.get('from')}'")
            return False

        if "value" not in conv:
            print(f"第 {i+1} 轮对话缺少 'value' 字段")
            return False
        elif not isinstance(conv.get("value"), str):
            print(f"第 {i+1} 轮对话的 'value' 字段必须是字符串类型")
            return False
    return True


# 将指定的文件转换为Alpaca数据集格式
def generate_alpaca_data(
    input_path: str,
    output_path: str,
    english: bool = False,
):
    """
    将CSV数据转换为Alpaca数据集的格式
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(input_path, encoding="utf-8")
        # 将DataFrame转换为字典列表
        # orient='records'表示每行作为一个字典
        csv_data = df.to_dict("records")
    except FileNotFoundError:
        print(colored(f"错误: 文件 '{input_path}' 不存在", "red"))
        return []
    except Exception as e:
        print(colored(f"读取CSV文件时出错: {e}", "red"))
        return []

    alpaca_data = []
    llm = get_local_deepseek_model_client()
    # llm = get_deepseek_model_client()
    # 由模板生成prompt
    prompt = ChatPromptTemplate.from_template(alpaca_prompt_template if not english else english_alpaca_prompt_template)
    # 创建chain
    chain = (
        RunnableMap(
            {
                # 使用检索后的文档内容作为上下文
                "paper_info_str": lambda x: x["paper_info_str"],
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    for i, paper in enumerate(csv_data):
        print(
            colored(
                f"处理第 {i+1}/{len(csv_data)} 篇论文: {list(paper.values())[0]}",
                "blue",
            )
        )

        # 构建论文信息字符串
        paper_info = []
        for key, value in paper.items():
            # 过滤掉未提及的值
            if re.search(r"未提及|未提供|无|未知|nan", str(value), re.IGNORECASE):
                continue
            paper_info.append(f"{key}: {value}")
        # 判断paper_info中value不为空和未提及的值需多于5个再进行处理
        if len(paper_info) <= 5:
            print(colored(f"跳过该论文, 因为有效信息少于5个", "yellow"))
            continue
        paper_info_str = "\n".join(paper_info)

        # 解析响应
        max_retry = 5
        for _try in range(max_retry):
            try:
                results = chain.invoke({"paper_info_str": paper_info_str})
                # 尝试解析为JSON
                qa_pair = json.loads(extract_clean_json(results))

                # 确保包含必需字段
                if validate_alpaca_data_format(qa_pair):
                    # 添加论文信息
                    qa_pair["paper"] = list(paper.values())[0]
                    # 添加推理信息到output中
                    qa_pair["output"] = f"\n ```{qa_pair['reason']}```\n\n{qa_pair['output']}"
                    # 删除reason字段
                    del qa_pair["reason"]
                    alpaca_data.append(qa_pair)
                    save_to_file(qa_pair, output_path)
                    print(colored(f"成功生成并保存问答对", "green"))
                    break
                else:
                    print(colored(f"{results}\n 响应缺少必需字段，重新尝试 {_try + 1} / {max_retry}", "red"))

            except json.JSONDecodeError:
                print(colored(f"{results}\n 无法解析响应为JSON, 重新尝试 {_try + 1} / {max_retry}", "red"))
            except Exception as e:
                print(colored(f"处理响应时发生错误: {e}, 重新尝试 {_try + 1} / {max_retry}", "red"))

    print(
        colored(f"已保存 {len(alpaca_data)} 个问答对到 {output_path}", "green")
    )


# 将指定的文件转换为ShareGPT数据集格式
def generate_sharegpt_data(
    input_path: str,
    output_path: str,
    english: bool = False,
):
    """
    将CSV数据转换为ShareGPT数据集的格式
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(input_path, encoding="utf-8")
        # 将DataFrame转换为字典列表
        # orient='records'表示每行作为一个字典
        csv_data = df.to_dict("records")
    except FileNotFoundError:
        print(colored(f"错误: 文件 '{input_path}' 不存在", "red"))
        return []
    except Exception as e:
        print(colored(f"读取CSV文件时出错: {e}", "red"))
        return []

    sharegpt_data = []
    llm = get_local_deepseek_model_client()
    # llm = get_deepseek_model_client()
    # 由模板生成prompt
    prompt = ChatPromptTemplate.from_template(sharegpt_prompt_template if not english else english_sharegpt_prompt_template)
    # 创建chain
    chain = (
        RunnableMap(
            {
                # 使用检索后的文档内容作为上下文
                "paper_info_str": lambda x: x["paper_info_str"],
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    for i, paper in enumerate(csv_data):
        print(
            colored(
                f"处理第 {i+1}/{len(csv_data)} 篇论文: {list(paper.values())[0]}",
                "blue",
            )
        )

        # 构建论文信息字符串
        paper_info = []
        for key, value in paper.items():
            # 过滤掉未提及的值
            if re.search(r"未提及|未提供|无|未知|nan", str(value), re.IGNORECASE):
                continue
            paper_info.append(f"{key}: {value}")
        # 判断paper_info中value不为空和未提及的值需多于10个再进行处理
        if len(paper_info) <= 10:
            print(colored(f"跳过该论文, 因为有效信息少于10个", "yellow"))
            continue
        paper_info_str = "\n".join(paper_info)

        # 解析响应
        max_retry = 5
        for _try in range(max_retry):
            try:
                results = chain.invoke({"paper_info_str": paper_info_str})
                # 尝试解析为JSON
                qa_pair = json.loads(extract_clean_json(results))
                if validate_sharegpt_data_format(qa_pair):
                    sharegpt_data.append(qa_pair)
                    save_to_file(qa_pair, output_path)
                    print(colored(f"成功生成并保存问答对", "green"))
                    break
                else:
                    print(colored(f"{results}\n 响应格式不正确，重新尝试 {_try + 1} / {max_retry}", "red"))
            except json.JSONDecodeError:
                print(colored(f"{results}\n 无法解析响应为JSON, 重新尝试 {_try + 1} / {max_retry}", "red"))
            except Exception as e:
                print(colored(f"处理响应时发生错误: {e}, 重新尝试 {_try + 1} / {max_retry}", "red"))

    print(
        colored(f"已保存 {len(sharegpt_data)} 个问答对到 {output_path}", "green")
    )


if __name__ == "__main__":
    generate_sharegpt_data("知网论文200篇-指标.csv", "知网论文200篇-数据集.json")