from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool


from modules.speckle.projects import SpeckleProject

import streamlit as st

class Information_ToolInput(BaseModel):
    question: str = Field(description="should be the question")


@tool("Information_Tool", args_schema=Information_ToolInput)
def information_tool(question: str) -> str:
    """This tool can answer basic information about the project. 
    
    Following things are given in the Project Information: Author, Name, Adresse, Latitude, Organization Name of the Software, and other similar ones.

    Potentially some of the information can be missing, but the tool will try to provide as much information as possible.

    It returns the answer to the question."""

    template = """In the following I provide you with information about the project. Please ask me a question about the project.

    Project Information: {information}
    
    Question: {question}"""

    # get the correct project
    project = SpeckleProject(name=st.session_state.get("project_name"))

    # get the project information
    project_information_obj = project.get_project_information()

    # convert Base object into a string
    project_information = ""
    entries = project_information_obj.get_dynamic_member_names()
    for entry in entries:
        project_information += f"{entry}: {project_information_obj[entry]}"

    # build up LLM
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI()
    output_parser = StrOutputParser()

    chain = (
            prompt
            | model
            | output_parser
    )

    return chain.invoke({"question": question, "information": project_information},
                           config={'callbacks': [ConsoleCallbackHandler()]})
