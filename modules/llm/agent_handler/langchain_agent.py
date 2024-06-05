from typing import Callable, Any

from modules.llm.llm_settings import LLMSettings
from modules.llm.tools import information_tool, bim_ir_tool, rag_tool

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import hub

from abc import ABC
import ast


class Langchain_Agent_Handler(ABC):
    """ class to handle and specify the behavior of the Langchain Agent"""

    @staticmethod
    def setup_agent(settings: LLMSettings) -> AgentExecutor:
        """ set up the LangChain Agent"""

        # Get the correct LLM model
        llm = settings.get_correct_langchain_llm()

        # Get the prompt
        # prompt = hub.pull("hwchase17/openai-functions-agent")
        prompt = hub.pull("janix/central_agent_ma")

        tools = [bim_ir_tool, rag_tool, information_tool]

        # Set up the agent
        agent = create_tool_calling_agent(llm, tools, prompt)

        # Create an agent executor by passing in the agent and tools
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True,
                                       return_intermediate_steps=True
                                       )

        return agent_executor

    @staticmethod
    def setup_tool_tester(settings: LLMSettings) -> AgentExecutor:
        """ set up the LangChain Agent for the tool tester"""

        # Specify the tools
        tool = bim_ir_tool

        return tool
    
    @staticmethod
    def recursive_intermediate_parser(output: dict, max_depth = 2) -> dict[str, Any]:
        if "intermediate_steps" in output:
            print("Intermediate Steps: ")
            steps = output["intermediate_steps"]
            for step in steps:
                output["intermediate_steps"] = Langchain_Agent_Handler.recursive_intermediate_parser(step[0], max_depth = max_depth - 1)
        elif isinstance(output, str):
            if output.startswith("tool"):
                output = Langchain_Agent_Handler.parse_toolagentaction(output)
        return output
    
    @staticmethod
    def parse_toolagentaction(output: str) -> dict[str, Any]:
        """ parse the tool agent action"""
        print("Hello")
        
        # Find the boundaries of the main components
        tool_start = output.find("tool='") + len("tool='")
        tool_end = output.find("'", tool_start)
        tool = output[tool_start:tool_end]

        tool_input_start = output.find("tool_input=") + len("tool_input=")
        tool_input_end = output.find("},", tool_input_start) + 1
        tool_input_str = output[tool_input_start:tool_input_end]
        tool_input = ast.literal_eval(tool_input_str)
        
        log_start = output.find("log='") + len("log='")
        log_end = output.find("',", log_start)
        log = output[log_start:log_end]

        message_log_start = output.find("message_log=[") + len("message_log=[")
        message_log_end = output.find("]", message_log_start) + 1
        message_log_str = output[message_log_start:message_log_end]
        message_log = ast.literal_eval(message_log_str)
        
        tool_call_id_start = output.find("tool_call_id='") + len("tool_call_id='")
        tool_call_id_end = output.find("'", tool_call_id_start)
        tool_call_id = output[tool_call_id_start:tool_call_id_end]
        
        return {
            'tool': tool,
            'tool_input': tool_input,
            'log': log,
            'message_log': message_log,
            'tool_call_id': tool_call_id
        }
