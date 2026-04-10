import json
from openai import OpenAI
import concurrent.futures
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain_core.output_parsers import StrOutputParser
from termcolor import colored
from utils import extract_clean_json
from model_clients import get_ali_model_client
import time
import os


single_choice_prompt = """
请根据以下数据生成一道有四个选项的单项选择题：问题为instruction域的内容，根据output域中的治理措施和效果提炼生成一项正确答案。并根据你的知识生成其它的混淆选项。返回格式为json，question域为问题，answer域为答案， 注意不要包含敏感信息和文字。
数据如下：{sample}
问题示例：
{{
    "question": "
    针对东营市的滨海盐碱地，已知总盐分含量为1%~10%，土壤质地为砂质土，地下水埋深1.14米，气象条件为冬冷夏热、降雨稀少而蒸发量大，矿化度高，平均含盐量14.3g/L。请选择最适合的治理措施，只返回选项即可。
    选项：
    A. 暗管排盐结合耐盐植物种植
    B. 灌溉洗盐配合生物炭施用
    C. 深耕翻土结合地膜覆盖
    D. 暗管排盐、灌溉洗盐、施用石膏改良剂和耐盐植物种植",
    "answer": "D"
}},
"""

single_choice_instruction_prompt = """
\n请严格按照要求回答：仅返回选项字母，不要任何额外内容，不要思考过程，不要表格。你的回答只能是：A、B、C或D中的一个字母
"""

multi_choice_prompt = """
请根据以下数据生成一道有四个选项的多项选择题：题目为instruction域的内容，根据output域中的治理措施和效果提炼生成一项或多项正确答案。并根据你的知识生成其它的混淆选项。返回格式为json，question域为问题，answer域为答案字符串，注意不要包含敏感信息和文字。
数据如下：{sample}
问题示例：
    {{
    "question": "
    针对辽宁盘锦新生农场的滨海盐碱土（氯化物硫酸盐型），其土壤pH为7.8~8.5，全盐量0.1%~0.8%，地势低洼、地下水位高，春季干旱导致盐分上返，且初始有机质含量仅为1%。请选择所有适用于该地区并已被验证有效的盐碱地治理措施。
    选项：
    A. 采用台田高床结合排水渠系统降低地下水位，并配合高畦栽植促进自然淋盐
    B. 在育苗阶段设置秸秆隔离层以阻隔下层盐分上升并提升地温
    C. 连续多年大量施用有机肥并配合适量磷肥，以提升有机质、降低pH并增强作物抗逆性
    D. 单纯依靠深翻耕作而不进行排水或覆盖，以期通过物理扰动降低盐分",
    "answer": "ABC"
}},
"""

multi_choice_instruction_prompt = """
\n请严格按照要求回答：仅返回选项字母组合，不要任何额外内容，不要思考过程，不要表格。你的回答只能是：A、B、C或D中的一个或多个字母组合，如：ACD
"""


def generate_question(sample, raw_prompt):
    llm = get_ali_model_client()
    prompt = ChatPromptTemplate.from_template(raw_prompt)
    chain = (
        RunnableMap({"sample": lambda x: x["sample"]})
        | prompt
        | llm
        | StrOutputParser()
    )
    max_retry = 5
    last_result = {}
    for _try in range(max_retry):
        try:
            result = chain.invoke({"sample": sample})
            result = json.loads(extract_clean_json(result))
            if 'answer' in result and 'question' in result:
                if raw_prompt == single_choice_prompt:
                    result["question"] += single_choice_instruction_prompt
                else:
                    result["question"] += multi_choice_instruction_prompt
                for key, value in sample.items():
                    result[key] = value.strip()
                return result
            else:
                last_result = result.copy()
                print(colored(f"重新调用模型以获取所有指标 {_try + 1} / {max_retry}", "red"))
        except json.JSONDecodeError:
            print(colored(f"返回的不是有效JSON, 重新调用模型 {_try + 1} / {max_retry}", "red"))
        except Exception as e:
            print(colored(f"处理结果时发生错误: {e}, 重新调用模型 {_try + 1} / {max_retry}", "red"))
    print (colored(f"多次尝试失败，返回部分指标", "yellow"))
    return last_result


def create_dataset(input, raw_prompt, output_file, num=None):
    # 如果input是字符串则读取文件内容，否则直接使用input作为数据
    if isinstance(input, str):
        with open(input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = input
    # 随机选取其中num条数据生成测试集
    import random
    if num is not None and num < len(data):
        data = random.sample(data, num)
    generated_data = []
    count = 0
    print (f"开始生成数据集，共 {len(data)} 条数据...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        generate_questions = [executor.submit(generate_question, item, raw_prompt) for item in data]
        for future in concurrent.futures.as_completed(generate_questions):
            res = future.result()
            generated_data.append(res)
            count += 1
            print (f"已生成 {count}/{len(data)} 条数据...")
    # 保存生成的数据到output_file文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(generated_data, f, ensure_ascii=False, indent=4)
    print(f"生成的数据已保存至 {output_file}\n")


def generate_answer(client, name, item, error_record_file=None):
    question = item["question"]
    answer = item["answer"]
    # 获取生成答案所需的时间
    max_retry = 5
    start_time = time.time()
    for _try in range(max_retry):
        response = ""
        try:
            completion = client.chat.completions.create(
            model=name,
            messages=[
                    {"role": "user", "content": question},
                ],
            stream=True
            )
            for chunk in completion:
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        response += delta.content
                        if len(response.strip()) > 4:
                            break
        except Exception as e:
            print(colored(f"{name}模型调用出错: {e}, 重新尝试 {_try + 1} / {max_retry}", "red"))
            continue
        if any(c not in ['A', 'B', 'C', 'D'] for c in response.strip()):
            print(colored(f"{name}模型回答不符合要求，重新尝试 {_try + 1} / {max_retry}", "red"))
        else:
            break
    end_time = time.time()
    elapsed_time = end_time - start_time
    if response.strip() != answer and error_record_file is not None:
        # 将错误回答记录到文件中，文件格式是一个json列表，将item添加到列表末尾
        item['model'] = name
        item['response'] = response.strip()
        with open(error_record_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return response.strip() == answer, elapsed_time


def test_dataset(client, name, input, output=None, error_record_file=None):
    # 读取测试集文件中的数据
    with open(input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    correct_count = 0
    total_count = len(data)
    total_time = 0.0
    num = 0
    print (f"正在使用{input}测试{name}模型, 共 {total_count} 条数据...")
    # if error_record_file is not None:
    #     with open(error_record_file, 'a', encoding='utf-8') as f:
    #         f.write(f"开始测试{name}模型在数据集{input}上的表现。\n")
    #         f.write("====================================\n\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        generate_answers = [executor.submit(generate_answer, client, name, item, error_record_file) for item in data]
        for future in concurrent.futures.as_completed(generate_answers):
            correct, elapsed_time = future.result()
            total_time += elapsed_time
            if correct:
                correct_count += 1
            num += 1
            print(colored(f"已测试 {num}/{total_count} 条数据...", "blue"))
    print(f"{name}模型在数据集{input}上的准确率: {correct_count}/{total_count} = {correct_count/total_count:.2%}, 总用时: {total_time:.2f}秒, 平均每题用时: {total_time/total_count:.2f}秒")
    # 保存结果到文件
    if output is not None:
        with open(output, 'a', encoding='utf-8') as f:
            f.write(f"{name}模型在数据集{input}上的准确率: {correct_count}/{total_count} = {correct_count/total_count:.2%}\n总用时: {total_time:.2f}秒, 平均每题用时: {total_time/total_count:.2f}秒\n")
    return correct_count, total_count, total_time


if __name__ == "__main__":
    # create_dataset("./saline_alkali_soil_alpaca_categorized_test.json", single_choice_prompt, "./test_datasets/test_dataset.json")
    local_client = OpenAI(
        api_key="EMPTY",
        base_url="http://localhost:8080/v1",
    )

    qwen_client = OpenAI(
        api_key="sk-a5e301543bff417f890ebb31962cac09",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    uiui_client = OpenAI(
        api_key="sk-D2bxFyiKlX4YdxFbX7ll6bf8jhsM3KJhT9tly7nySG36SPjX",
        base_url="https://sg.uiuiapi.com/v1",
    )

    chat_response = local_client.chat.completions.create(
        model="qwq-32b", #指定要使用的模型名称 
        #"system"、"user" 或 "assistant"，分别代表系统消息、用户消息和助手消息。通常至少需要一个用户消息。  
        messages=[
            {"role": "user", "content": '你好，你是谁？'},
        ],
        #生成文本的随机性0-2。值越高越随机
        temperature = 0.5,
    )
    message_text = chat_response.choices[0].message.content
    print("本地模型回答:")
    print(message_text)

    # 指定实验结论文件
    conclusion_file = 'experiment_conclusions_3.txt'
    # with open(conclusion_file, 'w', encoding='utf-8') as f:
    #     f.write("实验结论：\n")
    # 创建错误回答记录文件
    error_record_file = 'error_records_3.txt'
    # with open(error_record_file, 'w', encoding='utf-8') as f:
    #     f.write("错误回答记录：\n")

    models = ["wenyao", "qwen3-max", "deepseek-v3", "qwq-32b", "deepseek-r1", "gpt-5", "gemini-2.5-pro"]
    # # "qwen2.5-vl-32b-instruct", "qwen2.5-32b-instruct", "qwen2.5-coder-32b-instruct"]
    # 遍历./test_datasets/目录下的所有数据集文件，使用不同模型进行测试
    # for dataset in os.listdir('./test_datasets/'):
    #     if dataset.endswith('dataset.json'):
    #         dataset_path = os.path.join('./test_datasets/', dataset)
    dataset_path = "./test_datasets/test_dataset.json"
    for model_name in models:
        if model_name == "wenyao":
            test_dataset(local_client, model_name, dataset_path, conclusion_file, error_record_file)
        elif model_name in ["gpt-5", "gemini-2.5-pro"]:
            test_dataset(uiui_client, model_name, dataset_path, conclusion_file, error_record_file)
        else:
            test_dataset(qwen_client, model_name, dataset_path, conclusion_file, error_record_file)

    print(f"所有测试完成，结果已保存至{conclusion_file}和{error_record_file}文件中。")