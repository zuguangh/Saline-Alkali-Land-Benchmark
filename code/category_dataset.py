from openai import OpenAI
import json
import concurrent.futures
from test_choices_script import create_dataset, single_choice_prompt


local_client = OpenAI(
    api_key="EMPTY",
    base_url="http://localhost:8080/v1",
)

qwen_client = OpenAI(
    api_key="sk-a5e301543bff417f890ebb31962cac09",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def generate_category(prompt, sample):
    completion = qwen_client.chat.completions.create(
        model="qwen3-max",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的土壤科学专家，擅长分析盐碱地的类型。",
            },
            {
                "role": "user",
                "content": prompt,
            },  
        ]
    )
    response = completion.choices[0].message.content.strip()
    return response, sample


def generate_ph_category(input_file, output_file="saline_alkali_soil_alpaca_categorized.json"):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prompt = """请根据以下土壤信息判断该盐碱地属于轻度盐碱地（pH值在7.1到8.5之间），中度盐碱地（pH值在8.6到9.5之间），还是重度盐碱地（pH值大于9.5），若提供信息无法判断盐碱地类型，则返回“未提供”。仅返回“轻度盐碱地”、“中度盐碱地”、“重度盐碱地”或“未提供”中的一个，不要包含任何其他解释或文字，不要进行任何假设和推断。土壤信息为：{information}"""
    # 对于每组数据，调用大模型判断其属于轻度盐碱地，中度盐碱地还是重度盐碱地
    count = 0
    print ("开始分离数据集，根据盐碱地类型进行分类...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        generate_answers = [executor.submit(generate_category, prompt.format(information=sample['instruction']), sample) for sample in data]
        for future in concurrent.futures.as_completed(generate_answers):
            response, sample = future.result()
            sample['ph_category'] = response
            count += 1
            print(f"已处理 {count}/{len(data)} 条数据，当前样本盐碱地类型判断结果为: {response}")
    # 保存结果到新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"分类后的数据已保存至 {output_file}\n")
    return


def generate_dataset_by_ph(input_file='saline_alkali_soil_alpaca_categorized.json'):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    ph_categories = ['轻度盐碱地', '中度盐碱地', '重度盐碱地']
    for ph_category in ph_categories:
        # 随机选取100条程度为{ph_category}的数据生成新的数据集
        filtered_data = [sample for sample in data if sample['ph_category'] == ph_category]
        import random
        selected_data = random.sample(filtered_data, min(100, len(filtered_data)))
        create_dataset(
            input=selected_data,
            raw_prompt=single_choice_prompt,
            output_file=f'./test_datasets/{ph_category}_dataset.json',
            num=len(selected_data)
        )


def generate_soil_category(input_file, output_file="saline_alkali_soil_alpaca_categorized.json"):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prompt = """请根据以下土壤中的盐分组成信息判断该盐碱地属于哪种类型：
    1.氯化物盐土：- 以氯化物为主要盐分，其中氯化钠（NaCl）占相当大的比例。土壤溶液中氯离子含量高，具有很强的腐蚀性。- 这种土壤在干旱和半干旱地区较为常见。例如在滨海地区，海水入侵或含盐地下水的蒸发，容易形成氯化物盐土。- 氯化物盐土的盐分溶解度大，在土壤中移动性较强，所以在春季返盐时，地表容易迅速积盐，对作物危害较大。
    2.硫酸盐盐土：- 主要盐分是硫酸根离子与钙、镁等阳离子结合形成的盐类，如硫酸钠（Na₂SO₄）。- 它的溶解度随温度变化有明显差异。在干旱炎热的夏季，硫酸钠的溶解度增大，土壤溶液中的盐分浓度可能升高；而在温度降低时，溶解度减小，可能会有芒硝（Na₂SO₄·10H₂O）晶体析出。- 硫酸盐盐土对植物的危害主要是通过渗透压的改变影响植物对水分和养分的吸收，而且硫酸根离子在土壤中积累过多时，可能对土壤结构产生不良影响。
    3.苏打盐土（碱土）：- 其主要特征是含有碳酸钠（Na₂CO₃）和碳酸氢钠（NaHCO₃）等碱性盐类。土壤呈强碱性，pH值一般在8.5 - 11之间。- 苏打盐土的不良物理性质非常明显，如土壤胶体高度分散，土壤结构差，通透性不良。这是因为碳酸钠等碱性盐类使土壤胶体吸附大量的钠离子，发生代换吸附作用，导致土壤颗粒分散。- 这种土壤上植物生长困难，除了高碱度对植物根系有毒害作用外，不良的土壤物理性质也阻碍了植物根系的生长和对养分的吸收。
    若提供信息无法判断盐碱地类型，则返回“未提供”。仅返回“氯化物盐土”、“硫酸盐盐土”、“苏打盐土”或“未提供”中的一个，不要包含任何其他解释或文字，不要进行任何假设和推断。
    土壤信息为：{information}"""
    # 对于每组数据，调用大模型判断其属于氯化物盐土，硫酸盐盐土还是苏打盐土
    count = 0
    print ("开始分离数据集，根据盐碱地类型进行分类...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        generate_answers = [executor.submit(generate_category, prompt.format(information=sample['instruction']), sample) for sample in data]
        for future in concurrent.futures.as_completed(generate_answers):
            response, sample = future.result()
            sample['soil_category'] = response
            count += 1
            print(f"已处理 {count}/{len(data)} 条数据，当前样本盐碱地类型判断结果为: {response}")
    # 保存结果到新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"分类后的数据已保存至 {output_file}\n")
    return


def generate_dataset_by_soil(input_file='saline_alkali_soil_alpaca_categorized.json'):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    soil_categories = ['氯化物盐土', '硫酸盐盐土', '苏打盐土']
    for soil_category in soil_categories:
        # 随机选取100条程度为{soil_category}的数据生成新的数据集
        filtered_data = [sample for sample in data if sample['soil_category'] == soil_category]
        import random
        selected_data = random.sample(filtered_data, min(100, len(filtered_data)))
        create_dataset(
            input=selected_data,
            raw_prompt=single_choice_prompt,
            output_file=f'./test_datasets/{soil_category}_dataset.json',
            num=len(selected_data)
        )
    return


def generate_geology_category(input_file, output_file="saline_alkali_soil_alpaca_categorized.json"):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prompt = """请根据以下土壤的形成原因和地理分布判断该盐碱地属于哪种类型：
    1.滨海盐碱地：- 形成原因 - 位于沿海地区，主要是由于海水浸渍形成的。海水含有大量的盐分，在潮汐涨落过程中，海水不断淹没沿海陆地，盐分逐渐在土壤中积累。- 滨海地区的地下水水位较高，且含盐量也高，在蒸发作用下，盐分随毛管水上升到地表，进一步加重了土壤的盐碱化程度。- 分布区域 - 广泛分布于世界各大洲的沿海地带，如我国的辽东湾、渤海湾、莱州湾、苏北沿海以及东南沿海等地。
    2.内陆盐碱地：- 形成原因 - 主要是由于内陆干旱或半干旱地区的气候条件导致的。在这些地区，降水量少，蒸发量大，土壤中的盐分不能被淋溶，而是随着水分蒸发不断在土壤表层积累。- 一些封闭或半封闭的内陆盆地，如塔里木盆地、准噶尔盆地等，其河流带来的盐分没有出路，在盆地内部不断积聚。此外，不合理的灌溉方式（如大水漫灌），导致地下水位上升，盐分也随之上升到地表，也是内陆盐碱地形成的重要原因。- 分布区域 - 分布于各大洲的内陆干旱和半干旱地区，在我国主要分布在西北的新疆、甘肃、宁夏以及内蒙古等地。
    3.次生盐碱地：- 形成原因 - 是人类活动引起的盐碱化现象。最常见的原因是不合理的灌溉。例如，在干旱和半干旱地区，如果灌溉时没有配套的排水设施，大量灌溉水会使地下水位迅速上升，地下水中的盐分随着毛管水上升到地表，当水分蒸发后，盐分就留在了土壤表层。- 此外，开垦荒地时破坏了原有的植被和土壤结构，也可能加速土壤的盐碱化过程。比如，过度开垦草原，破坏了草原植被对土壤水分和盐分的调节作用，导致盐分在土壤中积累。- 分布区域- 多分布在原本非盐碱地但进行了大规模农业开发或其他人类活动影响较大的区域，在世界上许多农业灌溉区都有次生盐碱地出现，如中亚地区的一些灌溉农业区以及我国北方的一些灌溉农田周围。
    若提供信息无法判断盐碱地类型，则返回“未提供”。仅返回“滨海盐碱地”、“内陆盐碱地”、“次生盐碱地”或“未提供”中的一个，不要包含任何其他解释或文字，不要进行任何假设和推断。
    土壤信息为：{information}"""
    # 对于每组数据，调用大模型判断其属于滨海盐碱地，内陆盐碱地还是次生盐碱地
    count = 0
    print ("开始分离数据集，根据盐碱地类型进行分类...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        generate_answers = [executor.submit(generate_category, prompt.format(information=sample['instruction']), sample) for sample in data]
        for future in concurrent.futures.as_completed(generate_answers):
            response, sample = future.result()
            sample['geology_category'] = response
            count += 1
            print(f"已处理 {count}/{len(data)} 条数据，当前样本盐碱地类型判断结果为: {response}")
    # 保存结果到新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"分类后的数据已保存至 {output_file}\n")
    return


def generate_dataset_by_geology(input_file='saline_alkali_soil_alpaca_categorized.json'):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    geology_categories = ['滨海盐碱地', '内陆盐碱地', '次生盐碱地']
    for geology_category in geology_categories:
        # 随机选取100条程度为{geology_category}的数据生成新的数据集
        filtered_data = [sample for sample in data if sample['geology_category'] == geology_category]
        import random
        selected_data = random.sample(filtered_data, min(100, len(filtered_data)))
        create_dataset(
            input=selected_data,
            raw_prompt=single_choice_prompt,
            output_file=f'./test_datasets/{geology_category}_dataset.json',
            num=len(selected_data)
        )
    return


def generate_treatment_category(input_file, output_file="saline_alkali_soil_alpaca_categorized.json"):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prompt = """请根据以下土地治理信息判断该盐碱地的治理措施属于哪种类型：
    1.工程措施：工程措施的核心依据是物理排盐和水位控制。它直接作用于水盐运动的通道，例如通过挖沟渠将含盐地下水排走，或者通过竖井抽提降低地下水位，是从根源上切断盐分来源的强力手段。
    2.农艺措施：农艺措施的核心依据是改良耕层和抑制蒸发。它侧重于通过改善土壤自身的物理性状（如通透性、有机质含量）来应对盐分问题，例如通过覆盖地膜减少水分蒸发，从而抑制盐分随水上升到地表。
    3.化学措施：化学措施的核心依据是离子反应和pH调节。它通过发生化学反应来改变土壤的化学性质，例如用石膏（主要成分硫酸钙）中的钙离子去置换土壤胶体上有害的钠离子，或者直接加入酸性物质来降低土壤的pH值。
    4.生物措施：生物措施的核心依据是生命活动和生态修复。它依赖于生物自身的生长和代谢功能，例如耐盐植物通过根系改善土壤结构，并通过庞大的生物量将土壤中的盐分带走；微生物则可能通过代谢产物来活化土壤养分。
    若提供信息无法判断盐碱地治理措施类型，则返回“未提供”。仅返回“工程措施”、“农艺措施”、“化学措施”、“生物措施”或“未提供”中的一个，不要包含任何其他解释或文字，不要进行任何假设和推断。
    土地治理信息为：{information}"""
    # 对于每组数据，调用大模型判断其属于哪种治理措施类型
    count = 0
    print ("开始分离数据集，根据盐碱地治理措施类型进行分类...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        generate_answers = [executor.submit(generate_category, prompt.format(information=sample['output']), sample) for sample in data]
        for future in concurrent.futures.as_completed(generate_answers):
            response, sample = future.result()
            sample['treatment_category'] = response
            count += 1
            print(f"已处理 {count}/{len(data)} 条数据，当前样本盐碱地治理措施类型判断结果为: {response}")
    # 保存结果到新的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"分类后的数据已保存至 {output_file}\n")
    return


def generate_dataset_by_treatment(input_file='saline_alkali_soil_alpaca_categorized.json'):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    treatment_categories = ['工程措施', '农艺措施', '化学措施', '生物措施']
    for treatment_category in treatment_categories:
        # 随机选取100条程度为{treatment_category}的数据生成新的数据集
        filtered_data = [sample for sample in data if sample['treatment_category'] == treatment_category]
        import random
        selected_data = random.sample(filtered_data, min(100, len(filtered_data)))
        create_dataset(
            input=selected_data,
            raw_prompt=single_choice_prompt,
            output_file=f'./test_datasets/{treatment_category}_dataset.json',
            num=len(selected_data)
        )
    return


if __name__ == "__main__":
    # generate_ph_category('saline_alkali_soil_alpaca_categorized.json')
    generate_dataset_by_ph('saline_alkali_soil_alpaca_categorized.json')
    # generate_soil_category('saline_alkali_soil_alpaca_categorized.json')
    generate_dataset_by_soil('saline_alkali_soil_alpaca_categorized.json')
    # generate_geology_category('saline_alkali_soil_alpaca_categorized.json')
    generate_dataset_by_geology('saline_alkali_soil_alpaca_categorized.json')
    # generate_treatment_category('saline_alkali_soil_alpaca_categorized.json')
    generate_dataset_by_treatment('saline_alkali_soil_alpaca_categorized.json')
