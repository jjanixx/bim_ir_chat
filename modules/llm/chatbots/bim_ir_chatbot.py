from operator import itemgetter

from langchain.output_parsers.pandas_dataframe import PandasDataFrameOutputParser
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, Runnable
from langchain.callbacks.tracers import ConsoleCallbackHandler

from pandasai import Agent

from pandas import DataFrame

from modules.llm.llm_settings import LLMSettings
from modules.llm.prompt_library import PromptLibrary
from modules.speckle.projects import SpeckleProject
from modules.llm.agent_handler import Pandasai_Agent_Handler

class BIMIRChatBot:

    def __init__(self, speckle_project: SpeckleProject, llm_settings: LLMSettings):
        self.project = speckle_project
        self.llm_settings = llm_settings
        self.llm = self.llm_settings.get_correct_langchain_llm()

    def conversational_chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        # # Get the categories from the project
        # categories_str = self.table_classification().invoke({"question":query}, config={'callbacks': [ConsoleCallbackHandler()]})
        # print("Categories: ", categories_str)

        # # Extract the pandas dataframes from the Speckle project
        # df_dict = self.extract_pandas_from_speckle(categories_str)
        # print("Extracted dataframe")

        answer = self.create_langchain_pandas_agent().invoke({"question": query}, config={'callbacks': [ConsoleCallbackHandler()]})

        # # Start the pandasai agent
        # agent = self.start_pandasai_agent(df)

        # # Start the chat with the agent
        # pandas_answer = agent.chat(query)

        return answer
    
    def create_whole_chain(self) -> Runnable:
        chain = (self.table_classification() | self.extract_pandas())
        chain2 = (self.table_classification() | self.extract_pandas() | RunnableLambda(self.create_langchain_pandas_agent))
        return chain
    
    def table_classification(self) -> Runnable:
        """Classify the query to find the correct Speckle table"""
        prompt = PromptLibrary.get_from_langchain_hub("janix/speckle_table_classification")
        chain = (
            {
                "categories": RunnableLambda(self.extract_categories), 
                "question": RunnablePassthrough()
            }
            | prompt 
            | self.llm
            | StrOutputParser()
        )
        return chain
    
    def extract_categories(self, question) -> str:
        """ Extracts the categories from the project"""
        categories = self.project.get_categories()
        # transform the list to a string
        categories_str = str(categories)
        return categories_str

    def extract_pandas_from_speckle(self, category_str: str) -> DataFrame:
        """ Extracts the pandas dataframe corresponding to the given category from the commit data"""
        if category_str[0] is not "@":
            category_str = "@" + category_str
        # split the categories for the string
        basehandler = self.project.get_basehandler()
        # extract the data from the commit
        df = basehandler.get_category_dataframe(category_str)
        return df
    
    def extract_pandas(self) -> Runnable:
        """ Extracts the pandas dataframe corresponding to the given category from the commit data"""
        chain = (RunnableLambda(self.extract_pandas_from_speckle) | PandasDataFrameOutputParser())
        chain2 = (RunnableLambda(self.extract_pandas_from_speckle))
        return chain2
    
    def create_langchain_pandas_agent(self, pd) -> Runnable:
        agent = Pandasai_Agent_Handler.create_agent(self.llm_settings, pd)
        return agent

    def start_pandasai_agent(self, df: DataFrame):
        agent = Agent([df], config={"llm": self.llm, "verbose": True, "conversational": True}, memory_size=10)
        return agent
    