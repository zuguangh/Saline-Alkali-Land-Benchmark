import json
import hashlib
import faiss
from simhash import Simhash
from termcolor import colored
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm


def alpaca_to_text(data):
    """
    将Alpaca格式的数据转换为纯文本格式，方便相似度计算
    :param data: Alpaca格式的数据，包含'instruction'、'input'、'output'
    :return: 纯文本字符串
    """
    instruction = data.get("instruction", "")
    input_text = data.get("input", "")
    output = data.get("output", "")
    return f"Instruction: {instruction}\nInput: {input_text}\nOutput: {output}"


def simhash_filter(samples, distance_threshold=5):
    """
    使用Simhash进行去重，保留相似度低于distance_threshold的样本
    :param samples: Alpaca格式的数据列表
    :param distance_threshold: Simhash距离阈值
    :return: 去重后的数据列表
    """
    if not samples:
        return []

    unique_data = []
    duplicate_count = 0
    seen_hashes = {}  # 使用字典存储，key为样本索引
    
    for i, sample in enumerate(samples):
        sample_text = alpaca_to_text(sample)
        sample_hash = Simhash(sample_text)
        duplicate = False
        
        # 检查是否与已有hash相似
        for idx, existing_hash in seen_hashes.items():
            if sample_hash.distance(existing_hash) <= distance_threshold:
                duplicate = True
                duplicate_count += 1
                break
        if not duplicate:
            unique_data.append(sample)
            seen_hashes[i] = sample_hash  # 存储到字典

    print(colored(f"Simhash去重完成，去除 {duplicate_count} 个重复样本，保留 {len(unique_data)} 个样本", "green"))
    return unique_data


def similarity_filter(samples, threshold=0.9,
                      model_name="../models/paraphrase-multilingual-MiniLM-L12-v2"):
    """
    使用 Sentence-BERT + FAISS 去除语义重复样本。
    参数：
        samples: 样本列表
        threshold: 相似度阈值 (0~1)，高于此值即认为内容重复
        model_name: 句向量模型（支持多语言）
    返回：
        unique_samples: 过滤后的样本列表
    """
    print(colored("🔹 正在加载 Sentence-BERT 模型（用于相似度计算）...", "blue"))
    model = SentenceTransformer(model_name)   # 加载语义编码模型

    # 提取每条样本的文本（此处取所有 messages 内容拼接）
    texts = [alpaca_to_text(s) for s in samples]

    print(colored(f"🔹 正在编码 {len(texts)} 条样本...", "blue"))
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True   # ✅ 向量归一化，使内积等价于余弦相似度
    )

    # 创建 FAISS 向量索引
    dim = embeddings.shape[1]       # 向量维度
    index = faiss.IndexFlatIP(dim)  # 内积相似度索引
    index.add(embeddings)           # 加入所有样本向量

    unique_samples = []             # 存放唯一样本
    seen = set()                    # 已被判定为重复的样本索引

    print(colored("🔹 正在进行相似度过滤...", "blue"))
    for i, emb in enumerate(tqdm(embeddings, desc="相似度检测")):
        if i in seen:
            continue  # 若已标记为重复则跳过
        unique_samples.append(samples[i])

        # 在索引中搜索相似样本
        sim, idx = index.search(np.array([emb]), len(samples))
        for j, score in zip(idx[0], sim[0]):
            if score >= threshold:
                seen.add(j)  # 标记为重复
    print(colored(f"相似度过滤完成，去除 {len(samples) - len(unique_samples)} 个重复样本，保留 {len(unique_samples)} 个样本", "green"))
    return unique_samples


if __name__ == "__main__":
    input_path = "盐碱地改良文献2153篇-数据集.json"
    output_path = "盐碱地改良文献2153篇-数据集去重.json"

    # 读取Alpaca格式的数据
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 进行去重
    filtered_data = similarity_filter(data)

    # 将去重后的数据写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
