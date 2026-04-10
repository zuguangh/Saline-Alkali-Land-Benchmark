from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import (
    DashScopeEmbeddings,
)
from langchain_community.cross_encoders import (
    HuggingFaceCrossEncoder,
)  # 导入社区提供的包装器
from langchain.retrievers.document_compressors import CrossEncoderReranker
from transformers import AutoTokenizer


# 使用本地向量模型
ALI_TONGYI_EMBEDDING = "text-embedding-v3"


def get_ali_embedding_model(model=ALI_TONGYI_EMBEDDING):
    """
    通过LangChain获得一个阿里通义千问嵌入模型的实例
    :return: 阿里通义千问嵌入模型的实例, 目前为text-embedding-v3
    """
    return DashScopeEmbeddings(
        model=model,
        dashscope_api_key="sk-a5e301543bff417f890ebb31962cac09",
    )


def get_local_bge_embedding_model(model_path = "/home/hezg/.cache/modelscope/hub/models/BAAI/bge-m3"):
    """
    通过LangChain获得一个本地BGE嵌入模型的实例
    :return: 本地BGE嵌入模型的实例
    """

    model_kwargs = {'device': 'cuda'}
    encode_kwargs = {'normalize_embeddings': True}

    embeddings = HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings


def get_local_bge_reranker_model(model_path = "/home/hezg/.cache/modelscope/hub/models/BAAI/bge-reranker-v2-m3"):
    """
    通过LangChain获得一个本地BGE Reranker模型的实例
    :return: 本地BGE Reranker模型的实例
    """
    # 加载本地交叉编码器 (CrossEncoder) 模型
    huggingface_cross_encoder = HuggingFaceCrossEncoder(
        model_name=model_path,
        # device='cuda' if torch.cuda.is_available() else 'cpu',  # 通常会自动检测，也可手动指定
    )
    # 创建基于本地模型的重排压缩器
    local_reranker = CrossEncoderReranker(
        model=huggingface_cross_encoder,
        top_n=10,  # top_n 指定返回前几个文档
    )
    return local_reranker


def get_local_deepseek_model_client(model="DeepSeek-R1-Distill-Qwen-32B-local"):
    return ChatOpenAI(
        api_key="EMPTY", base_url="http://10.0.9.111:8081/v1", model=model
    )


def get_openai_model_client(model="gpt-4o"):
    return ChatOpenAI(
        api_key="EMPTY",
        base_url="https://api.openai.com/v1",
        model=model,
    )


def get_ali_model_client(model="qwen3-max"):
    return ChatOpenAI(
        api_key="EMPTY",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=model,
    )


def get_deepseek_model_client(model="deepseek-r1"):
    return ChatOpenAI(
        api_key="EMPTY",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=model,
    )


def get_model_clients():
    """
    产生大模型客户端和嵌入模型的客户端
    """
    return get_local_deepseek_model_client(), get_local_bge_embedding_model()


def get_model_tokenizer(model_name="DeepSeek-R1-Distill-Qwen-32B"):
    """
    根据模型名称获取对应的tokenizer
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained("../models/" + model_name)
    except:
        tokenizer = AutoTokenizer.from_pretrained(
            "../models/DeepSeek-R1-Distill-Qwen-32B"
        )
    return tokenizer
