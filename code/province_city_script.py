import pandas as pd

df = pd.read_excel('盐碱地改良中国知网文献汇总_0813-ZC.xlsx')
# 输出df的行数
print (f"共读取 {len(df)} 条数据")

# 合并'盐碱地改良中国知网文献(500分类版)-0929-指标.csv'，'盐碱地文献3501-6727-指标.csv', '盐碱地论文501-3500-指标.csv'三个文件中的指标内容
df1 = pd.read_csv('盐碱地改良中国知网文献(500分类版)-0929-指标.csv')
df2 = pd.read_csv('盐碱地文献3501-6727-指标.csv')
df3 = pd.read_csv('盐碱地论文501-3500-指标.csv')

df_merged = pd.concat([df1, df2, df3], ignore_index=True)

# 先为df添加所有需要的列
for col in df_merged.columns:
    if col not in df.columns:
        df[col] = None

# 对于df中的每个title，查找df_merged中'文献标题'列，若找到匹配，则添加对应的指标信息
for index, row in df.iterrows():
    title = row['Title-题名']
    # 在合并后的DataFrame中查找第一篇论文，使得title是文献标题的子串
    matched_row = df_merged[df_merged['文献标题'].str.contains(title, na=False, regex=False)]
    # 将matched_row中的所有列添加到row中
    if not matched_row.empty:
        # 取第一个匹配的结果
        first_match = matched_row.iloc[0]
        for col in first_match.index:
            # 将文档中形如两个整数比值的单元格转化为实数的形式防止显示错误，如12:34转化为12.0:34.0
            if isinstance(first_match[col], str) and ':' in first_match[col]:
                parts = first_match[col].split(':')
                if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                    first_match[col] = f"{parts[0].strip()}.0:{parts[1].strip()}.0"
            df.at[index, col] = first_match[col]
        # 使用pd.concat将row和first_match合并为一个Series
        # combined = pd.concat([row, first_match])
        # df.loc[index] = combined
        print (f"找到匹配: {title} -> {first_match['文献标题']}")
    else:
        print (f"未找到匹配: {title}")
        # 在df中删除该行
        df.drop(index, inplace=True)
# 将文献标题列名重命名为文档名字
df.rename(columns={'文献标题': '文档名字'}, inplace=True)
df.to_excel('盐碱地改良中国知网指标汇总.xlsx', index=False, engine='openpyxl')


df = pd.read_csv('盐碱地改良文献2153篇-省市解析.csv')
# 将文档中形如两个整数比值的单元格转化为实数的形式防止显示错误，如12:34转化为12.0:34.0
for col in df.columns:
    for index, value in df[col].items():
        if isinstance(value, str) and ':' in value:
            parts = value.split(':')
            if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                df.at[index, col] = f"{parts[0].strip()}.0:{parts[1].strip()}.0"
# 保存结果
df.to_csv('盐碱地改良文献2153篇-省市解析.csv', index=False)

import os
from openai import OpenAI
import re

prompts = """请分析以下地点信息，然后转化为XX省XX市的表示形式，如将‘云南昭通’转化为‘云南省昭通市’，返回一行表示转化后的地点信息，仅返回转化后为省市信息，不需要包括输入的信息和推理过程，转化后的地点信息只精确到市级即可。只有城市没有省份的地点请使用地理查询功能得到其对应的省然后输出为XX省XX市，只有省份没有城市的地点则直接输出XX省即可。如果输入包括多个地点，则将每个地点按上述要求表示为XX省XX市的形式，地点之间以逗号分隔。若地点信息为未提供，则也返回未提供即可。对于少数民族自治区，自治州等地区，保留其惯用的地点表示方式，返回同级别信息即可。直辖市则直接返回直辖市信息。若提供的地点信息无法分析出属于哪个省和哪个市，则也返回未提供。请严格遵循事实依据，严禁伪造。地点信息： {location}"""

client = OpenAI(
    api_key="sk-a5e301543bff417f890ebb31962cac09",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 读取盐碱地改良文献2153篇-指标.csv，添加一省市列，从地点信息中解析出省市
paper_info = pd.read_csv('盐碱地改良中国知网指标汇总.csv')
paper_info['省市'] = None

for index, row in paper_info.iterrows():
    print (f"处理第 {index+1}/{len(paper_info)} 篇论文")
    completion = client.chat.completions.create(
        model="qwen-max" if index < 3200 else "qwen-plus",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的地理信息处理助手，擅长将模糊的地点信息转化为标准的省市格式。",
            },        
            {
                "role": "user",
                "content": prompts.format(location=row['地点']),
            },
        ],
        extra_body = {"enable_search": True}
    )
    response = re.sub(r'^.*?</think>\s*', '', completion.choices[0].message.content, flags=re.DOTALL).strip()
    paper_info.at[index, '省市'] = response
    print (f"地点信息: {row['地点']} -> 省市: {response}")

# 保存结果到新的CSV文件
paper_info.to_csv('盐碱地改良中国知网指标汇总.csv', index=False)

# 读取盐碱地改良中国知网指标汇总.xlsx
df = pd.read_excel('盐碱地改良中国知网指标汇总.xlsx', engine='openpyxl')
# 读取盐碱地改良中国知网治理措施汇总.csv
measures = pd.read_csv('盐碱地改良中国知网治理措施汇总.csv')
# 对于measures每一行，找到文档名字与df中文档名字对应的一行，将measures中的治理措施内容添加到df中
for index, row in measures.iterrows():
    doc_name = row['文档名字']
    measure = row['治理措施']
    matched_rows = df[df['文档名字'] == doc_name]
    if not matched_rows.empty:
        df.loc[matched_rows.index, '治理措施'] = measure
# 读取saline_alkali_soil_alpaca_categorized.json
import json
with open('saline_alkali_soil_alpaca_categorized.json', 'r', encoding='utf-8') as f:
    categorized = json.load(f)
# 在df中添加一列'治理措施类型'
df['治理措施类型'] = None
# 对于categorized中每一行，找到paper域与df中文档名字对应的一行，将treatment_category内容添加到df的'治理措施类型'列中
for item in categorized:
    doc_name = item['paper']
    treatment_category = item['treatment_category']
    matched_rows = df[df['文档名字'] == doc_name]
    if not matched_rows.empty:
        df.loc[matched_rows.index, '治理措施类型'] = treatment_category
        print (f"文档: {doc_name} -> 治理措施类型: {treatment_category}")
df['治理措施类型'] = df['治理措施类型'].fillna('未提供')
# 保存结果到新的Excel文件
df.to_excel('盐碱地改良中国知网指标汇总_含治理措施类型.xlsx', index=False, engine='openpyxl')
