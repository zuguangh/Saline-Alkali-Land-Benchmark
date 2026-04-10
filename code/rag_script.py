from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
import json
from sentence_transformers import CrossEncoder
from model_clients import *
from prompts import *
from langchain.retrievers import ContextualCompressionRetriever

from utils import extract_clean_json
from termcolor import colored
from langchain_core.runnables import chain
from english_prompts import english_metrics_list, english_rag_prompt_template

# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

# 获得大模型客户端
# llm = get_local_deepseek_model_client()
llm = get_ali_model_client(model="qwen3-max")
# 获得嵌入模型客户端
embeddings_model = get_local_bge_embedding_model()
# 获得重排模型客户端
reranker_model = get_local_bge_reranker_model()
# 获取tokenizer
tokenizer = get_model_tokenizer()


# 格式化输出内容
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )


def include_all_metrics(requested_metrics, result):
    # 返回的指标应该是请求的指标一一对应的前缀
    keys = list(result.keys())
    for i, metric in enumerate(requested_metrics.strip().split("\n")):
        if not metric.startswith(keys[i]):
            print(colored(f"缺少指标: {metric}", "red"))
            return False
    return True


@chain
def call_llm(input: dict, english=False):
    # 由模板生成prompt
    prompt = ChatPromptTemplate.from_template(rag_prompt_template if not english else english_rag_prompt_template)
    # 创建chain
    chain = (
        RunnableMap(
            {
                "context": lambda x: x["context"],
                "metrics": lambda x: x["metrics"],
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    max_retry = 5
    last_result = {}
    for _try in range(max_retry):
        try:
            result = chain.invoke(input)
            result = json.loads(extract_clean_json(result))
            if include_all_metrics(input["metrics"], result):
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


# 从给定的文档中解析相关指标
def metrics_retrieval(doc_path, english=False, max_tokens=30000):
    # 加载文档
    loader = TextLoader(
        doc_path,
        encoding="utf-8",
    )
    docs = loader.load()
    # 输出文档长度
    doc_length = len(tokenizer.encode(docs[0].page_content))
    print(f"文档长度: {doc_length} tokens")
    # 分割文档
    # text_splitter = RecursiveCharacterTextSplitter(
    #     separators=["# ", "\n\n", "\n", " ", ""],
    #     chunk_size=512,
    #     chunk_overlap=64,
    # )
    # 生成context
    if doc_length < max_tokens:
        print("-------------------使用原始文档内容作为上下文-------------------------")
    else:
        print("-------------------使用向量检索生成上下文-------------------------")
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,  # 是否保留标题文本
        )
        # 执行分割
        split_docs = markdown_splitter.split_text(docs[0].page_content)
        print(f"分割后文档块数量: {len(split_docs)} 块")
        # print("-------------------分割后文档块-------------------------")
        # pretty_print_docs(split_docs)

        # 创建Chroma向量存储
        vectorstore = Chroma.from_documents(
            documents=split_docs, embedding=embeddings_model
        )

        # 向量检索
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        # doc_vector_retriever = vector_retriever.invoke(question)
        # print("-------------------向量检索-------------------------")
        # pretty_print_docs(doc_vector_retriever)

        # 关键词检索
        BM25_retriever = BM25Retriever.from_documents(split_docs)
        BM25Retriever.k = 10
        # doc_BM25Retriever = BM25_retriever.invoke(question)
        # print("-------------------BM25检索-------------------------")
        # pretty_print_docs(doc_BM25Retriever)

        # 混合检索EnsembleRetriever是Langchain集合多个检索器的检索器。
        ensembleRetriever = EnsembleRetriever(
            retrievers=[BM25_retriever, vector_retriever], weights=[0.5, 0.5]
        )
        # retriever_doc = ensembleRetriever.invoke(question)
        # print("-------------------混合检索-------------------------")
        # 创建上下文压缩检索器
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=reranker_model,
            base_retriever=ensembleRetriever,
        )

    # 批量处理所有指标
    all_metrics = [{"metrics": metrics, "context": docs if doc_length < max_tokens else compression_retriever.invoke(metrics)} for metrics in (metrics_list if not english else english_metrics_list)]
    results = call_llm.batch(all_metrics, english=english)
    
    # 检索完成后清理Chroma向量库
    if doc_length >= max_tokens:
        try:
            vectorstore.delete_collection()
        except Exception as e:
            print(f"清理向量数据库时发生错误: {e}")

    # 合并结果
    result_dict = {}
    for result in results:
        try:
            result_dict.update(result)
        except Exception as e:
            print(colored(f"处理{doc_path.stem}结果时发生错误: {e}", "red"))
    return result_dict


def include_all_treatment_metrics(requested_metrics, result):
    # 检查返回的结果是否包含了所有请求的指标
    keys = list(result.keys())
    for metric in requested_metrics:
        if not metric in keys:
            print(colored(f"缺少指标: {metric}", "red"))
            return False
    return True


def treatment_call_llm(input: dict):
    # 获得访问大模型客户端
    llm = get_ali_model_client()
    # 由模板生成prompt
    prompt = ChatPromptTemplate.from_template(new_treatment_prompt_template)
    # 创建chain
    chain = (
        RunnableMap(
            {
                "context": lambda x: x["context"],
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    max_retry = 5
    last_result = {}
    for _try in range(max_retry):
        try:
            result = chain.invoke(input)
            result = json.loads(extract_clean_json(result))
            if include_all_treatment_metrics(input["metrics"], result):
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


def treatment_metrics_retrieval(doc_path, requested_metrics, max_tokens=30000):
    # 加载文档
    loader = TextLoader(
        doc_path,
        encoding="utf-8",
    )
    docs = loader.load()
    doc_length = len(tokenizer.encode(docs[0].page_content))
    print(f"文档长度: {doc_length} tokens")
    
    if doc_length < max_tokens:
        print("-------------------使用原始文档内容作为上下文-------------------------")
        context_source = docs
    else:
        print("-------------------使用向量检索生成上下文-------------------------")
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,
        )
        
        split_docs = markdown_splitter.split_text(docs[0].page_content)
        print(f"分割后文档块数量: {len(split_docs)} 块")

        # 创建Chroma向量存储
        vectorstore = Chroma.from_documents(
            documents=split_docs, embedding=embeddings_model
        )

        # 向量检索
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        # doc_vector_retriever = vector_retriever.invoke(question)
        # print("-------------------向量检索-------------------------")
        # pretty_print_docs(doc_vector_retriever)

        # 关键词检索
        BM25_retriever = BM25Retriever.from_documents(split_docs)
        BM25Retriever.k = 10
        # doc_BM25Retriever = BM25_retriever.invoke(question)
        # print("-------------------BM25检索-------------------------")
        # pretty_print_docs(doc_BM25Retriever)

        # 混合检索EnsembleRetriever是Langchain集合多个检索器的检索器。
        ensembleRetriever = EnsembleRetriever(
            retrievers=[BM25_retriever, vector_retriever], weights=[0.5, 0.5]
        )
        # retriever_doc = ensembleRetriever.invoke(question)
        # print("-------------------混合检索-------------------------")
        # 创建上下文压缩检索器
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=reranker_model,
            base_retriever=ensembleRetriever,
        )
        context_source = compression_retriever.invoke('\n'.join(requested_metrics))
    results = treatment_call_llm({
        "metrics": requested_metrics, 
        "context": context_source
    })
    
    # 检索完成后清理Chroma向量库
    if doc_length >= max_tokens:
        try:
            vectorstore.delete_collection()
        except Exception as e:
            print(f"清理向量数据库时发生错误: {e}")
            
    return results


if __name__ == "__main__":
    doc_path = "/home/hezg/saline-alkali-soil_llm/英文文献-解析后/12932-Plant height, stem diameter and production of jatropha irrigated under different salinity levels/post_process.md"
    results = metrics_retrieval(doc_path, english=True)
    print("------------模型回复所有指标------------------------")
    print(results)
