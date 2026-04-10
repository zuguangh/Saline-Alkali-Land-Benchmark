import re
import os
import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List, Any
import importlib.util
from termcolor import colored
import concurrent.futures
from post_process_script import clean_text
from openai import OpenAI


def extract_clean_json(response_text):
    """
    从 DeepSeek 模型的响应中提取纯净的 JSON。
    移除 </think> 标签、```json 和 ``` 标记。

    参数:
    response_text: 模型返回的完整文本

    返回:
    纯净的 JSON 字符串，如果无法找到有效 JSON 则返回 None
    """
    # 1. 使用正则表达式移除从开头到第一个</think>标签的内容
    no_think = re.sub(r'^.*?</think>\s*', '', response_text, flags=re.DOTALL).strip()

    # 2. 移除代码块标记
    # 移除开头的 ```json 或 ```
    text = re.sub(r'^\s*```(?:json)?\s*', '', no_think, flags=re.IGNORECASE)
    # 移除结尾的 ```
    text = re.sub(r'\s*```\s*$', '', text, flags=re.IGNORECASE)
    
    # 3. 清理格式
    text = re.sub(r'\n\s*\n', '\n\n', text)  # 合并多余空行
    text = text.strip()
    return text

    # # 4. 尝试找到 JSON 对象或数组的开始和结束位置
    # # 查找第一个 { 或 [ 的位置
    # start_bracket = cleaned_text.find("{")
    # start_square = cleaned_text.find("[")

    # start_index = -1
    # if start_bracket != -1 and start_square != -1:
    #     # 两者都存在，取最靠前的那个
    #     start_index = min(start_bracket, start_square)
    # elif start_bracket != -1:
    #     start_index = start_bracket
    # elif start_square != -1:
    #     start_index = start_square

    # if start_index == -1:
    #     # 没有找到 JSON 的开始标记
    #     print(colored("未找到有效的 JSON 起始标记（{ 或 [）。", "red"))
    #     return None

    # 从找到的开始位置提取子字符串
    # potential_json = cleaned_text[start_index:]

    # # 5. （可选）尝试验证并解析 JSON，确保其有效性
    # try:
    #     parsed_json = json.loads(potential_json)
    #     # 如果解析成功，返回格式化后的 JSON 字符串
    #     return json.dumps(parsed_json, ensure_ascii=False, indent=2)
    # except json.JSONDecodeError as e:
    #     print(colored(f"提取后的文本不是有效的 JSON: {e}", "red"))
    #     # 即使无效，也返回提取到的文本，用户可能想自行处理
    #     return potential_json


def process_single_paper(paper_name, input_dir, output_csv, requested_metrics):
    """
    处理单个论文的函数，用于多线程环境
    """
    try:
        # 在input_dir下找到以paper_name开头的子目录
        paper_dir = list(Path(input_dir).glob(f"{paper_name}*"))
        if not paper_dir:
            print(colored(f"未找到论文目录: {paper_name}", "red"))
            return None
        if len(paper_dir) > 1:
            print(colored(f"找到多个匹配的论文目录，使用第一个: {paper_name}", "yellow"))
        paper_dir = paper_dir[0]
        print(colored(f"正在处理: {paper_name}", "blue"))

        # 查找MD文件
        md_files = list(paper_dir.rglob("*.md"))

        if not md_files:
            print(colored(f"在目录 {paper_dir} 中未找到MD文件", "red"))
            return {"文档名字": paper_name, "处理备注": "未找到MD文件"}

        # 假设每个目录只有一个MD文件，取第一个
        md_file = md_files[0]
        
        # 对md文件进行后处理
        result = clean_text(md_file.read_text(encoding="utf-8"))
        # 将后处理结果保存到md文件同目录下的post_process.md文件中
        result_path = paper_dir / "post_process.md"
        result_path.write_text(result, encoding="utf-8")
        print(colored(f"后处理结果已保存到: {result_path}", "white"))

        from rag_script import treatment_metrics_retrieval
        # 调用RAG函数提取相关指标
        metrics = treatment_metrics_retrieval(result_path, requested_metrics)

        # 构建结果行
        row = {"文档名字": paper_name}
        for metric in metrics:
            row[metric] = metrics[metric]
        row["处理备注"] = "成功提取治理措施相关指标"
        print(colored(f"成功提取 {paper_name} 的治理措施相关指标", "green"))
        return row

    except Exception as e:
        print(colored(f"处理 {paper_name} 时发生错误: {e}", "red"))
        row = {"文档名字": paper_name, "处理备注": f"处理时发生错误: {e}"}
        return row

def process_parsed_papers_multithread(input_dir: str, output_csv: str, paper_list: list = None, max_workers: int = 10):
    """
    多线程版本的论文处理函数
    
    Args:
        input_dir: 输入目录
        output_csv: 输出CSV文件路径
        paper_list: 论文列表，如果为None则自动从目录中获取
        max_workers: 最大线程数，如果为None则使用系统默认值
    """
    if not paper_list:
        # 获取所有子目录（每个论文一个目录）
        paper_dirs = [d for d in Path(input_dir).iterdir() if d.is_dir()]
        if not paper_dirs:
            print(colored(f"在目录 {input_dir} 中未找到论文目录", "red"))
            return

        # 论文名字为目录名字中第一个'.pdf'之前的部分
        paper_list = set([d.name.split('.pdf')[0] for d in paper_dirs])
        print(colored(f"找到 {len(paper_dirs)} 个论文目录", "green"))

    # 存储所有结果
    fieldnames = ["文档名字"]
    requested_metrics = ["土地信息", "治理措施", "治理效果", "原因分析", "推理过程"]
    fieldnames.extend(requested_metrics)
    fieldnames.append("处理备注")

    # 先创建CSV文件并写入表头
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # 使用线程池处理论文
    successful_count = 0
    total_count = len(paper_list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_paper = {
            executor.submit(process_single_paper, paper_name, input_dir, output_csv, requested_metrics): paper_name
            for paper_name in paper_list
        }
        
        # 处理完成的任务
        for future in concurrent.futures.as_completed(future_to_paper):
            paper_name = future_to_paper[future]
            try:
                row = future.result()
                if row:
                    # 将结果写入CSV文件
                    with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writerow(row)
                    if row["处理备注"] == "成功提取治理措施相关指标":
                        successful_count += 1
                        print(colored(f"处理成功: {successful_count}/{total_count} - {paper_name}", "green"))
                    else:
                        print(colored(f"处理失败: {paper_name} {row['处理备注']}", "red"))
                else:
                    print(colored(f"处理失败: {paper_name}", "red"))
            except Exception as exc:
                print(colored(f"处理 {paper_name} 时生成异常: {exc}", "red"))
                # 写入错误行
                error_row = {"文档名字": paper_name, "处理备注": f"处理时发生异常: {exc}"}
                with open(output_csv, "a", newline="", encoding="utf-8") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(error_row)

    print(colored(f"处理完成! 成功处理 {successful_count}/{total_count} 篇论文", "green"))
    print(colored(f"所有结果已保存到: {output_csv}", "green"))


def generate_single_delecamation_type(client, input):
    if input == "未提供":
        return "未提供"
    prompt = """
你是一个盐碱地治理专家，请根据以下治理措施的描述，判断其属于哪种治理措施类型：物理措施（指通过物理方法直接改善土壤结构和性质的措施，如耕作、翻土、覆盖等）、生物措施（指利用植物、微生物等生物手段改善土壤环境的措施，如种植耐盐碱植物、施用有机肥等）、化学措施（指通过施用化学物质调整土壤性质的措施，如施用石灰、硫酸铵等）、工程措施（指通过建设工程改变土地形态或水文条件的措施，如修建排水系统、筑堤等）还是组合措施（指同时采用两种或以上不同类型的治理措施）。请仅根据提供的治理措施描述进行判断，并只返回以下五个选项之一：物理措施
、生物措施、化学措施、工程措施和组合措施。只需要返回其中一个类型，不要返回其他任何内容。
治理措施描述: {context} 
    """.format(context=input)
    
    response = ""
    while response not in ["物理措施", "生物措施", "化学措施", "工程措施", "组合措施"]:
        response = client.chat.completions.create(
            model="qwen3-max",
            messages=[{"role": "system", "content": prompt}],
            stream=False
        )
        response = extract_clean_json(response.choices[0].message.content.strip())
        if response not in ["物理措施", "生物措施", "化学措施", "工程措施", "组合措施"]:
            print(colored(f"模型返回了无效的治理措施类型: {response}，正在重新生成...", "red"))
    return response


def generate_declamation_type_multithread(doc_path: str, max_workers: int = 10):
    qwen_client = OpenAI(
        api_key="sk-a5e301543bff417f890ebb31962cac09",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    # 读取doc_path下的xlsx类型的文档
    import pandas as pd
    df = pd.read_excel(doc_path)
    # 对于每一行数据，根据‘治理措施’列的信息，调用generate_single_delecamation_type判断其属于哪种治理措施类型，并将结果保存到新添加的‘治理措施类型’列中，使用多线程加速处理并在终端打印处理进度和结果，最后将处理结果保存到新的xlsx文件中，文件名为原文件名加上_declamation_type.xlsx
    df["治理措施类型"] = ""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(generate_single_delecamation_type, qwen_client, row["措施: (如施用石膏、暗管排盐等。如文章有不同处理,则按照对照,处理1,处理2...多行列出)"]): index
            for index, row in df.iterrows()
        }
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                declamation_type = future.result()
                df.at[index, "治理措施类型"] = declamation_type
                print(colored(f"处理完成: {index + 1}/{len(df)} - 治理措施类型: {declamation_type}", "green"))
            except Exception as exc:
                print(colored(f"处理第 {index + 1} 行时生成异常: {exc}", "red"))
                df.at[index, "治理措施类型"] = "处理失败"
                print(colored(f"处理完成: {index + 1}/{len(df)} - 治理措施类型: 处理失败", "red"))
    # 将处理结果保存到新的xlsx文件中，文件名为原文件名加上_declamation_type.xlsx
    output_path = doc_path.replace(".xlsx", "_declamation_type.xlsx")
    df.to_excel(output_path, index=False)
    print(colored(f"处理完成! 结果已保存到: {output_path}", "green"))

# 判断给定的经纬度数据格式，如果是度分秒的格式则转化为十进制表示：如37°11'N, 119°21'E转化为37.18°N, 119.35°E；北纬 45°34′∼45°39′, 东经 126°17′∼126°21′转化为45.57°N∼45.65°N, 126.28°E∼126.35°E。如果是十进制格式则直接返回。如果通过~和，符号分隔包含多个经纬度信息则分别进行转化。最后所有结果统一保留两位小数并以度为单位表示。如果无法识别则返回错误信息，并在终端以红色字体打印给定的经纬度数据。
def transform_coordinates(coordinate_str):
    if coordinate_str == "未提供":
        return "未提供"
    if not isinstance(coordinate_str, str):
        return str(coordinate_str)
    try:
        # 将中文的指示词转换为带有特殊标记的前缀，方便分配至整个区间
        s = coordinate_str.replace("北纬", "PREFIX_N ").replace("南纬", "PREFIX_S ")
        s = s.replace("东经", "PREFIX_E ").replace("西经", "PREFIX_W ")
        
        # 统一区间连接符号为波浪号（处理中文破折号、长横线、特殊波浪号、至等），这一步确保最后输出统一为~
        s = s.replace("—", "~").replace("–", "~").replace("∼", "~").replace("至", "~")
        
        # 将直接附在数字前方的英文方向标识（如 E106°，即位于开头或逗号、波浪号之后的字母）也转换为 PREFIX 统一处理
        def convert_to_prefix(match):
            return f"{match.group(1)}PREFIX_{match.group(2).upper()} "
        s = re.sub(r'(^|[,;，；~\-]\s*)([NSEW])\s*(?=\d)', convert_to_prefix, s, flags=re.IGNORECASE)
        
        # 统一符号（处理全角和各种引号以及连续的单引号，并将中文“度”替换为°）
        s = s.replace("’", "′").replace('”', "″").replace("''", '"').replace("度", "°")
        
        # 将前置方向标记分配到后面的数值（包括区间中的每个数值）
        # 示例："PREFIX_N 45°34′~45°39′" 会被转换为 "45°34′N ~45°39′N"
        def assign_prefix(match):
            direction = match.group(1)
            content = match.group(2)
            parts = re.split(r'([~\-]+)', content)
            res = ""
            for part in parts:
                if re.search(r'\d', part):
                    res += part.strip() + direction
                else:
                    res += part
            return res
            
        s = re.sub(r'PREFIX_([NSEW])\s*([\d°′″\'\"\.\s~\-]+)', assign_prefix, s)
        
        # 清除可能残留的未匹配的前缀标记
        s = s.replace("PREFIX_N", "N").replace("PREFIX_S", "S").replace("PREFIX_E", "E").replace("PREFIX_W", "W")
        
        # 将后置方向标记分配到前面的数值（处理例如 34°37′~35°06′N 这种格式）
        def assign_suffix(match):
            part1 = match.group(1).strip()
            sep = match.group(2)
            part2 = match.group(3).strip()
            direction = match.group(4)
            if not re.search(r'[NSEW]$', part1):
                part1 += direction
            return f"{part1}{sep}{part2}{direction}"
            
        s = re.sub(r'([\d][\d°′″\'\"\.\s]*)\s*([~\-])\s*([\d][\d°′″\'\"\.\s]*)([NSEW])', assign_suffix, s)
        
        # 定义正则表达式：
        # 分为两种情况兼容：
        # 1. 包含度数符号°的正常度分秒结构（分、秒可选，妥协错误格式：允许分和秒混用单双引号）
        # 2. 纯十进制数字直接跟方向字母（如 106.8E）
        dms_pattern = re.compile(r'(?:(\d{1,3}(?:\.\d+)?)[°\s]+(?:(\d{1,2}(?:\.\d+)?)[\'′\"″\s]+)?(?:(\d{1,2}(?:\.\d+)?)[\'′\"″\s]*)?|(\d{1,3}(?:\.\d+)?)\s*)([NSEW])')
        
        def dms_to_decimal(match):
            if match.group(4): # 匹配到了纯十进制没有°的情况
                degrees = float(match.group(4))
                minutes = 0.0
                seconds = 0.0
            else:
                degrees = float(match.group(1))
                minutes = float(match.group(2)) if match.group(2) else 0.0
                seconds = float(match.group(3)) if match.group(3) else 0.0
                
            direction = match.group(5)
            decimal = degrees + minutes / 60 + seconds / 3600
            if direction in ['S', 'W']:
                decimal = -decimal
            return f"{decimal:.2f}°{direction}"
        
        # 替换所有度分秒格式为十进制格式
        transformed_str = dms_pattern.sub(dms_to_decimal, s)
        
        # 处理范围格式，统一转化为标准的波浪号格式~
        transformed_str = re.sub(r'(\d+\.\d+°[NSEW])\s*[~\-]\s*(\d+\.\d+°[NSEW])', r'\1~\2', transformed_str)
        
        return transformed_str
    except Exception as e:
        print(colored(f"无法识别的经纬度数据: {coordinate_str}. 错误信息: {e}", "red"))
        return f"无法识别的经纬度数据: {coordinate_str}"

# 读取盐碱地改良中国知网指标汇总1027入库-去重.xlsx，并将每行的经纬度列信息调用transform_coordinates函数进行转换，并将转换结果保存到新添加的经纬度_十进制列中，最后将处理结果保存到新的xlsx文件中，文件名为原文件名加上_coordinates.xlsx
def transform_coordinates_multithread(doc_path: str, max_workers: int = 10):
    # 读取xlsx文件
    import pandas as pd
    df = pd.read_excel(doc_path)
    # 对于每一行数据，根据经纬度列的信息，调用transform_coordinates函数进行转换，并将结果保存到新添加的经纬度_十进制列中，使用多线程加速处理并在终端打印处理进度和结果，最后将处理结果保存到新的xlsx文件中，文件名为原文件名加上_coordinates.xlsx
    df["经纬度_十进制"] = ""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(transform_coordinates, row["经纬度"]): index
            for index, row in df.iterrows()
        }
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                transformed_coordinates = future.result()
                df.at[index, "经纬度_十进制"] = transformed_coordinates
                # print(colored(f"处理完成: {index + 1}/{len(df)} - 转换结果: {transformed_coordinates}", "green"))
            except Exception as exc:
                print(colored(f"处理第 {index + 1} 行时生成异常: {exc}", "red"))
                df.at[index, "经纬度_十进制"] = "处理失败"
                print(colored(f"处理完成: {index + 1}/{len(df)} - 转换结果: 处理失败", "red"))
    # 将处理结果保存到新的xlsx文件中，文件名为原文件名加上_coordinates.xlsx
    output_path = doc_path.replace(".xlsx", "_coordinates.xlsx")
    df.to_excel(output_path, index=False)
    print(colored(f"处理完成! 结果已保存到: {output_path}", "green"))


# 随机抽取saline_alkali_soil_alpaca_categorized.json中4/5的数据做为训练数据，其它为测试数据
def generate_train_test_split(json_path: str, train_ratio: float = 0.8):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    total_count = len(data)
    train_count = int(total_count * train_ratio)
    # 随机打乱数据
    import random
    random.shuffle(data)
    train_data = data[:train_count]
    test_data = data[train_count:]
    # 保存训练数据和测试数据到新的json文件中
    with open(json_path.replace(".json", "_train.json"), "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    with open(json_path.replace(".json", "_test.json"), "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    print(colored(f"生成完成! 训练数据: {len(train_data)} 条, 测试数据: {len(test_data)} 条", "green"))


# 读取json文件，统计其中各个sample的"geology_category", "treatment_category"，"ph_category"和"soil_category"这几个字段中每个种类出现的次数
def count_categories(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    geology_category_count = {}
    treatment_category_count = {}
    ph_category_count = {}
    soil_category_count = {}
    for sample in data:
        geology_category = sample.get("geology_category", "未提供")
        treatment_category = sample.get("treatment_category", "未提供")
        ph_category = sample.get("ph_category", "未提供")
        soil_category = sample.get("soil_category", "未提供")
        geology_category_count[geology_category] = geology_category_count.get(geology_category, 0) + 1
        treatment_category_count[treatment_category] = treatment_category_count.get(treatment_category, 0) + 1
        ph_category_count[ph_category] = ph_category_count.get(ph_category, 0) + 1
        soil_category_count[soil_category] = soil_category_count.get(soil_category, 0) + 1
    print(colored(f"地质类型统计: {geology_category_count}", "green"))
    print(colored(f"治理措施类型统计: {treatment_category_count}", "green"))
    print(colored(f"pH类型统计: {ph_category_count}", "green"))
    print(colored(f"土壤类型统计: {soil_category_count}", "green"))
    return geology_category_count, treatment_category_count, ph_category_count, soil_category_count


# 读取输入的json文件，其中每个json对象记录了一个model打错的一道题，其中‘model’字段为模型名称，统计每个模型在‘geology_category', 'treatment_category', 'ph_category'和'soil_category'这几个字段中每个种类出现的次数，并将统计结果打印出来。
def calculate_auto_test_accuracy(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    model_category_count = {}
    for record in data:
        model = record.get("model", "未知模型")
        geology_category = record.get("geology_category", "未提供")
        treatment_category = record.get("treatment_category", "未提供")
        ph_category = record.get("ph_category", "未提供")
        soil_category = record.get("soil_category", "未提供")
        if model not in model_category_count:
            model_category_count[model] = {
                "geology_category": {},
                "treatment_category": {},
                "ph_category": {},
                "soil_category": {}
            }
        model_category_count[model]["geology_category"][geology_category] = model_category_count[model]["geology_category"].get(geology_category, 0) + 1
        model_category_count[model]["treatment_category"][treatment_category] = model_category_count[model]["treatment_category"].get(treatment_category, 0) + 1
        model_category_count[model]["ph_category"][ph_category] = model_category_count[model]["ph_category"].get(ph_category, 0) + 1
        model_category_count[model]["soil_category"][soil_category] = model_category_count[model]["soil_category"].get(soil_category, 0) + 1
    print(colored(f"模型分类统计: {model_category_count}", "green"))
    # 调用count_categories，根据返回的总的category统计结果计算每个模型在每个category种类上的正确率，并打印返回。
    geology_category_count, treatment_category_count, ph_category_count, soil_category_count = count_categories("saline_alkali_soil_alpaca_categorized_test.json")
    for model in model_category_count:
        print(colored(f"模型: {model}", "blue"))
        for category in ["geology_category", "treatment_category", "ph_category", "soil_category"]:
            print(colored(f"  分类: {category}", "cyan"))
            for category_type in model_category_count[model][category]:
                count = model_category_count[model][category][category_type]
                total = 0
                if category == "geology_category":
                    total = geology_category_count.get(category_type, 0)
                elif category == "treatment_category":
                    total = treatment_category_count.get(category_type, 0)
                elif category == "ph_category":
                    total = ph_category_count.get(category_type, 0)
                elif category == "soil_category":
                    total = soil_category_count.get(category_type, 0)
                accuracy = 1.0 - count / total if total > 0 else 0
                print(colored(f"    类型: {category_type}, 错误数: {count}, 总数: {total}, 正确率: {accuracy:.2%}", "yellow"))
    return model_category_count


if __name__ == "__main__":
    # doc_path = "盐碱地改良中国知网指标汇总1027入库-去重.xlsx"
    # transform_coordinates_multithread(doc_path, max_workers=10)
    # json_path = "saline_alkali_soil_alpaca_categorized.json"
    # generate_train_test_split(json_path, train_ratio=0.8)
    # count_categories("saline_alkali_soil_alpaca_categorized_test.json")
    calculate_auto_test_accuracy("error_records_3.json")