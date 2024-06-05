from typing import Any, Dict

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI

from modules.llm.tools import pandas_extraction


class BIMIR_ToolInput(BaseModel):
    question: str = Field(description="should be the question")


@tool("BIM_IR_Tool", args_schema=BIMIR_ToolInput, return_direct=False)
def bim_ir_tool(question: str) -> dict[str, Any]:
    """This tool can answer questions based on project data. It returns the answer to the question."""

    # get the correct project categories
    # returns list of dataframes, see category_extraction tool
    df_list = pandas_extraction(question)

    # take only the first dataframe
    if len(df_list) >= 1:
        df_list = df_list[0]

    # assign LLM
    llm = ChatOpenAI()

    # use the pandas dataframe agent
    agent_executor = create_pandas_dataframe_agent(
        llm,
        df_list,
        agent_type="openai-tools",
        return_intermediate_steps=True,
        verbose=True
    )

    return agent_executor.invoke({"input": question})
