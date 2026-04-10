# 在你的Python脚本最开头添加这些行
__import__('pysqlite3')
import sys
from xml.parsers.expat import model
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import json
import re
import os
import chromadb
from openai import OpenAI
from termcolor import colored
from utils import extract_clean_json
from model_clients import get_ali_model_client
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from model_clients import *
from prompts import *
from langchain.retrievers import ContextualCompressionRetriever
from utils import extract_clean_json
from termcolor import colored
from langchain_core.runnables import chain


# 设置持久化目录
PERSIST_DIRECTORY = "../db"  # 指定保存目录
embeddings_model = get_local_bge_embedding_model()

# 读取saline_alkali_soil_alpaca_processed.json文件构建知识库
with open("saline_alkali_soil_alpaca_processed.json", "r", encoding="utf-8") as f:
    alpaca_data = json.load(f)
database = []
for sample in alpaca_data:
    doc = sample["instruction"] + "\n" + sample["output"]
    database.append(Document(page_content=doc, metadata={"instruction": sample["instruction"], "output": sample["output"], "paper": sample["paper"]}))
print(f"已加载 {len(database)} 条数据用于构建知识库。")

# # 构建向量数据库
# vectorstore = Chroma.from_documents(
#     documents=database, embedding=embeddings_model, persist_directory=PERSIST_DIRECTORY, collection_name="saline_alkali_land_alpaca"
# )
# print(f"向量数据库已保存到: {PERSIST_DIRECTORY}")

# 加载已有的向量数据库
vectorstore = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings_model,
    collection_name="saline_alkali_land_alpaca"
)

# 检查数据库中的文档数量
print(f"数据库中的文档数量: {vectorstore._collection.count()}")

# 向量检索
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# 关键词检索
BM25_retriever = BM25Retriever.from_documents(database)
BM25Retriever.k = 10

# 混合检索EnsembleRetriever是Langchain集合多个检索器的检索器。
ensembleRetriever = EnsembleRetriever(
    retrievers=[BM25_retriever, vector_retriever], weights=[0.5, 0.5]
)

local_client = OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8080/v1",
)

qwen_client = OpenAI(
    api_key="EMPTY",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

uiui_client = OpenAI(
    api_key="EMPTY",
    base_url="https://sg.uiuiapi.com/v1",
)

# 判断字符串中是否有汉字连续出现min_repeat次以上
def has_repeated_chinese(text, min_repeat=5):
    """
    判断字符串中是否有汉字连续出现min_repeat次以上
    """
    # 匹配连续的中文字符
    pattern = r'([\u4e00-\u9fa5])\1{' + str(min_repeat-1) + ',}'
    return bool(re.search(pattern, text))


# 调用本地模型生成治理措施建议
def generate_answer(input, client=local_client, model="wenyao"):
    print (colored("正在使用大模型生成初步答案...", "blue"))
    legal = False
    while not legal:
        response = ""
        completion = client.chat.completions.create(
            model=model,
            messages=[
            {"role": "user", "content": input},
            ],
            stream=True
        )
        for chunk in completion:
            delta = chunk.choices[0].delta
            # 收到content，开始进行回复
            if hasattr(delta, "content") and delta.content:
                print(delta.content, end="", flush=True)
                response += delta.content
        print("\n")
        # 判断回答是否异常，一般异常情况为输出中有一个字连续重复出现5次以上
        if not has_repeated_chinese(response, min_repeat=5):
            legal = True
        else:
            legal = False
            print(colored("回答内容异常，重新调用模型生成答案...", "red"))
    return response


def call_llm(input, client, model):
    max_retry = 5
    for retry_count in range(max_retry):
        response = ""
        try:
            completion = client.chat.completions.create(
            model=model,
            messages=[
                    {"role": "user", "content": input},
                ],
            stream=True
            )
            for chunk in completion:
                if hasattr(chunk, 'choices') and chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        response += delta.content
                        print (delta.content, end="", flush=True)
            break
        except Exception as e:
            print(colored(f"{model}模型调用出错: {e}, 重新尝试 {retry_count + 1} / {max_retry}", "red"))
            continue
    # 截取</think>之后的内容
    if "</think>" in response:
        response = response.split("</think>", 1)[1]
    return response


# 使用大模型的搜索功能提取治理方案中提到的所有治理措施的成本信息
def generate_cost(input, client, model):
    print (colored("正在使用大模型的搜索功能提取治理措施成本信息...", "blue"))
    prompt = "请分析提取下面盐碱地治理方案中提到的所有治理措施，然后通过调用工具联网搜索每种治理措施的大致成本（单位为：元/亩）。对于找不到成本的治理措施，请你根据专业经验设定一个大致的成本，要求一定要符合常识。直接返回所有的成本信息，不要包括输入的信息和推理过程。治理方案如下:\n" + input
    # cost_info = ""
    # completion = client.chat.completions.create(
    #     model=model,
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "你是一个搜索助手。",
    #         },        
    #         {
    #             "role": "user",
    #             "content": 
    #         },
    #     ],
    #     stream=True,
    #     extra_body = {"enable_search": True}
    # )
    # for chunk in completion:
    #     delta = chunk.choices[0].delta
    #     # 收到content，开始进行回复
    #     if hasattr(delta, "content") and delta.content:
    #         print(delta.content, end="", flush=True)
    #         cost_info += delta.content
    # print("\n")
    # return cost_info
    return call_llm(prompt, client, model)


# 根据输入的盐碱地情况和大模型生成的结果，去知识库中查找其它相似的治理措施和效果
def generate_treatments(input, client=qwen_client, model="qwen3-max"):
    response = generate_answer(input, client, model)
    print (colored("正在检索相关治理措施和效果...", "blue"))
    related_docs = ensembleRetriever.invoke(input + response)
    print (colored(f"共检索到 {len(related_docs)} 条相关记录。", "green"))
    related_treatments = input + "\n"
    for doc in related_docs:
        print ([doc.metadata["output"]])
        related_treatments += doc.metadata["output"] + '\n'
    related_cost = generate_cost(related_treatments, client, model)
    related_paper = ''.join([('\n- ' + doc.metadata['paper']) for doc in related_docs])
    return related_treatments, related_cost, related_paper


# 对于给定的成本需求，生成符合要求的治理方案
def generate_plan(treatments, cost_info, budget, client=qwen_client, model="qwen3-max"):
    print (colored("正在使用大模型生成符合预算要求的综合治理方案...", "blue"))
    prompt = f"""请根据以下盐碱地治理措施和对应的成本信息，根据土地情况分析生成一个符合成本需求的综合治理方案。要求如下：
                1. 综合考虑治理效果和成本效益，选择合适的治理措施组合。
                2. 确保在尽量充分利用资金的情况下不超过指定的预算，并在返回方案中体现总成本和分配方案。
                3. 提供每种治理措施的具体实施建议和预期效果。
                4. 严格从下面给定的治理措施和治理效果中进行选择和估计预期效果，严禁任何虚构和不合理的推断, 但是返回的表述应自然，不要在返回中表明是引用的。

                治理措施和成本信息如下：
                治理措施:
                {treatments}
                成本信息:
                {cost_info}
                预算要求: {budget}元/亩
    """
    return call_llm(prompt, client, model)


def generate_direct_plan(input, budget, client, model):
    prompt = input + f"请基于以上盐碱地信息，生成一个预算为{budget}元/亩的综合治理方案"
    return call_llm(prompt, client, model)


def compare_plans(model1, model2, comparison_model="gpt-5"):
    # 创建比较结果文件夹
    os.makedirs(f"./{comparison_model}比较结果-{model1}-{model2}/", exist_ok=True)
    # 读取验证点数据.json
    with open("验证点数据.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)
    # 对每条验证点数据，比较./验证点治理建议-{model1}/和./验证点治理建议-{model2}/中的治理方案
    for key, value in test_data.items():
        print (colored(f"正在比较验证点: {key}", "blue"))
        for budget in [1000, 3000, 5000]:
            with open(f"./验证点治理建议-{model1}/{key}_{budget}_治理建议.md", "r", encoding="utf-8") as f:
                plan_1 = f.read()
            with open(f"./验证点治理建议-{model2}/{key}_{budget}_治理建议.md", "r", encoding="utf-8") as f:
                plan_2 = f.read()
            # 通过调用大模型在正确性，专业性，实用性，创新性等方面进行比较
            comparison_prompt = f"""请比较以下两份盐碱地治理方案，分别为方案A和方案B。在正确性，专业性，实用性，创新性等方面进行比较，并给出你的评价和推荐意见。请给出详细的分析过程和结论。
            方案A:{plan_1}
            方案B:{plan_2}
            """
            result = call_llm(comparison_prompt, uiui_client, model=comparison_model)
            # 通过调用大模型提取比较结果中推荐的方案是方案A还是方案B，直接返回一个字母'A'或'B'
            answer_prompt = f"""请从以下比较结果中提取出推荐的方案是方案A还是方案B，直接返回一个字母'A'或'B'。比较结果如下:
            {result}
            """
            answer = ""
            while answer not in ['A', 'B']:
                answer = call_llm(answer_prompt, uiui_client, model=comparison_model)
            # 保存比较结果到文件
            with open(f"./{comparison_model}比较结果-{model1}-{model2}/{key}_{budget}_比较结果_{answer}.md", "w", encoding="utf-8") as f:
                f.write(result)
            print (colored(f"已保存比较结果至 ./{comparison_model}比较结果-{model1}-{model2}/{key}_{budget}_比较结果_{answer}.md", "green"))


def generate_plans():
    # 读取验证点数据.json
    with open("验证点数据.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)
    # 对每条验证点数据，调用本地模型生成治理措施建议，并去知识库中查找相关治理措施和效果
    # 创建验证点治理建议文件夹
    client = qwen_client
    model = "qwen3-max"
    os.makedirs(f"./验证点治理建议-{model}-{model}/", exist_ok=True)
    # os.makedirs(f"./验证点治理建议-{model}/", exist_ok=True)
    for key, value in test_data.items():
        print (colored(f"正在处理验证点: {key}", "blue"))
        question = key
        for k, v in value.items():
            question += f"{k}为{v}，"
        question += "请建议适合该盐碱地的治理措施，并说明治理效果。"
        related_treatments,  related_cost, related_paper = generate_treatments(question, client, model)
        for budget in [1000, 3000, 5000]:
            print (colored(f"正在生成预算为 {budget} 元/亩 的治理方案...", "blue"))
            plan = generate_plan(related_treatments, related_cost, budget, client, model)
            # 保存结果到文件
            with open(f"./验证点治理建议-{model}-{model}/{key}_{budget}_治理建议.md", "w", encoding="utf-8") as f:
                f.write(f"## 验证点名称: {key}\n")
                for k, v in value.items():
                    f.write(f"{k}: {v}\n")
                f.write(plan + '\n' + related_paper + "\n\n")
            # plan = generate_direct_plan(question, budget, client, model)
            # # 保存结果到文件
            # with open(f"./验证点治理建议-{model}/{key}_{budget}_治理建议.md", "w", encoding="utf-8") as f:
            #     f.write(f"## 验证点名称: {key}\n")
            #     for k, v in value.items():
            #         f.write(f"{k}: {v}\n")
            #     f.write(plan + "\n\n")
    print (colored("所有验证点处理完成！", "green"))


# 计算输入目录下的总文件数和以'_A.md'结尾的文件数
def count_comparison_results(path):
    count = 0
    count_A = 0
    for file in os.listdir(path):
        if file.endswith("_A.md"):
            count_A += 1
        count += 1
    print (colored(f"{path} 目录下总文件数: {count}，以'_A.md'结尾的文件数: {count_A}", "green"))


if __name__ == "__main__":
    # for model in ["deepseek-v3", "deepseek-r1", "gemini-2.5-pro"]:
    #     compare_plans(model1="wenyao-" + model, model2=model)
    # compare_plans(model1="qwen3-max-qwen3-max", model2="qwen3-max")
    # print (colored("所有验证点比较完成！", "green"))