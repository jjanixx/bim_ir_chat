from modules.llm.llm_settings import LLMSettings

from pandas import DataFrame

from pandasai import Agent


from abc import ABC

class Pandasai_Agent_Handler(ABC):

    """ class to handle and specify the behavior of the Pandasai Agent"""

    @staticmethod
    def setup_agent(df: DataFrame, settings: LLMSettings) -> Agent:
        """ setup the Pandasai Agent"""
        
        # get the correct llm from LLMSettings
        llm = settings.get_correct_pandasai_llm()

        # setup the agent (with according configurations)
        agent = Agent([df], memory_size=10, config={
            "llm": llm, 
            "verbose": False, 
            "conversational": True, 
            "enable_cache": False,
            "open_charts": True
            })
        
        return agent
    
    @staticmethod
    def return_verbose(agent: Agent):
        """ returns the step executed by the agent """
        last_logs = agent.logger._logs
        return last_logs
    
    @staticmethod
    def load_code(agent: Agent):
        """
        Extract the code that the PandasAI Agent has executed
        """
        # get the code from the agent
        logs = Pandasai_Agent_Handler.return_verbose(agent)
        print(logs)

        # iterate over the logs and extract the wanted output
        code = "No steps executed"
        print(logs)
        for log in logs:
            if log["source"]=="CodeManager" or log["source"]=="CodeCleaning":
                if "```" in log["msg"]:
                    code = log["msg"].split('```')[1]
                else:
                    # images have different formats
                    code = log["msg"]
                continue
        return code
    
    @staticmethod
    def load_prompt(agent: Agent):
        """
        Extract the prompt that the PandasAI Agent has executed
        """
        # get the code from the agent
        logs = Pandasai_Agent_Handler.return_verbose(agent)

        # iterate over the logs and extract the wanted output
        prompt = "No prompt generated"
        for log in logs:
            if log["source"]=="CodeGenerator":
                prompt = log["msg"]
                continue
        return prompt
    
    
    @staticmethod
    def load_log(self, agent: Agent):
        """
        Loads the log for the PandasAI Agent, not clean yet
        potentially to be removed
        """
        # get the code from the agent
        logs = self.return_verbose(agent)

        # transform code into the correct format
        log_list = []

        # iterate over the logs and extract the wanted output
        for log in logs:
            # only take the logs for the pipeline (we don't need CacheLookUps)
            if log["source"]=="Pipeline":
                title = log["msg"]
            if log["source"]=="CodeManager":
                code = log["msg"].split('```')[1]
                log_list.append(code)
            # take first line of the message as title
            title = log["msg"].split('\n')[0]
            dict = {"Step": f"{title}: "}
            entry_list = [title, ]
            # dict = {"Step": f"{log["msg"]}: ", "content": log, "code": log["message"]}
            # log_list.append(title)
        return log_list

