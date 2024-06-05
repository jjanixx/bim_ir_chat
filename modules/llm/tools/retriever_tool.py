from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.tools import create_retriever_tool, Tool
from langchain_openai import OpenAIEmbeddings


def get_retriever_tool(file_path: str, tool_name: str, tool_description: str) -> Tool:
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)
    vector = FAISS.from_documents(documents, OpenAIEmbeddings())
    retriever = vector.as_retriever()
    return create_retriever_tool(retriever, tool_name, tool_description)
