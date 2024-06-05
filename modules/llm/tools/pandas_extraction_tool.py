from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from modules.speckle.projects import SpeckleProject

from pandas import DataFrame
import streamlit as st


class ExtractionInput(BaseModel):
    question: str = Field(description="should be the question")


# most agents run best with tools that only need one string as an input
@tool("pandas-extraction-tool", args_schema=ExtractionInput)
def pandas_extraction(question: str) -> list[DataFrame]:
    """This tool can extract data from a project based on a search query. It returns a dictionary with the dataframes which contain the data that was searched for in the search query."""

    # prompt template for category classification
    template = """In the following I provide you a list with categories. Please take the following question "{question}" and understand about which category it is.
    
    The category does not have to mentioned in the exact form, but it has to be clear that the question is about this category.
    
    The categories are given in form of a Python list. For every entry in the list, search whether it is given in the question.
    
    Please just return the categories that are mentioned in the question, separated with a comma, without any other text.
    
    Please mention the category that is most likely to be the correct one at the beginning. 
    
    -----
    -----
    Categories: {categories}
    """

    project = SpeckleProject(name=st.session_state.get("project_name"))
    categories = str(project.get_categories())

    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI()
    output_parser = StrOutputParser()

    # classification chain
    category_chain = (
            prompt
            | model
            | output_parser
    )

    # data extraction chain
    df_chain = (
            category_chain
            | RunnableLambda(extract_pandas_from_speckle)
    )

    return df_chain.invoke({"question": question, "categories": categories},
                           config={'callbacks': [ConsoleCallbackHandler()]})


def extract_pandas_from_speckle(category_str: str) -> list[DataFrame]:
    """ Extracts the pandas dataframe corresponding to the given category from the commit data"""
    
    # Extract the data for the category from the data
    project = SpeckleProject(st.session_state.get("project_name"))

    # initialize the basehandler
    basehandler = project.get_basehandler()

    # split the categories for the string
    category_list = category_str.split(", ")

    # check if categories are found
    assert len(category_list) >= 1, "No categories found"

    # initialize the data list
    data = []

    # iterate over extracted categories
    for category in category_list:
        # check if category is correct
        if category not in basehandler.categories:
            # check if the @ is missing
            if "@" + category in basehandler.categories:
                # append the @ to the category
                category = "@" + category
            else:
                # category not in categories
                continue

        # append the DataFrame to the list
        data.append(basehandler.get_category_dataframe(category))
    
    return data
