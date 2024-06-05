from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.tools import create_retriever_tool, Tool
from langchain_openai import OpenAIEmbeddings


""" tools for Retrieval Augmented Generation """

class RAGToolInput(BaseModel):
    query: str = Field(description="The knowledge query to the agent")


@tool("document_retrieval", args_schema=RAGToolInput)
def rag_tool(query: str):
    """Search for information about the local building code.
    For any questions about the local building code, you must use this tool!
    """
    
    baybo_description = """Search for information about the local building code.
    For any questions about the local building code, you must use this tool!
    """

    # Get the PDF loader and load the document
    loader = PyMuPDFLoader("documents/BayBO.pdf")
    docs = loader.load()

    # split the documents into chunks
    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)

    # get the embeddings for the documents via FAISS
    vector_db = FAISS.from_documents(documents, OpenAIEmbeddings())
    # use vectors as retriever
    retriever = vector_db.as_retriever()

    # initialize the retriever tool
    tool = create_retriever_tool(retriever, "baybo_retrieval", baybo_description)

    return tool