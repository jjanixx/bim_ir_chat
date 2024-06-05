import backoff  # for exponential backoff
import openai
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from pandasai.llm import OpenAI


# from pandasai.llm import OpenAI

client = OpenAI()  

@backoff.on_exception(backoff.expo, openai.RateLimitError)
def completions_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)


class LLMSettings():

    """class to handle the settings of the LLMs over all prototypes"""

    # possible models
    MODEL_OPTIONS = ["gpt-4", "gpt-3.5-turbo", "claude-3-opus-20240229"]

    # min, max and default values for the temperature
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    def __init__(self, model=None, temperature = None) -> None:
        """initialize the LLM settings, set default values if not given"""
        self.model = model if model else self.MODEL_OPTIONS[0]
        self.temperature = temperature if temperature else 0.0

    def get_possible_models(self):
        """return the possible models"""
        return self.MODEL_OPTIONS
    
    def use_claude_as_model(self):
        """ get the current claude model """
        self.model = "claude-3-opus-20240229"

    def get_correct_api_key(self):
        """ retrieves the correct API key for the model choosen """
        load_dotenv()
        if "gpt" in self.model:
            return os.getenv("OPENAI_API_KEY")
        else:
            return os.getenv("ANTHROPIC_API_KEY")
        
    def get_correct_langchain_llm(self):
        """ provide the correct LLM for the langchain chatbots"""
        if "gpt" in self.model:
            return ChatOpenAI(model=self.model, temperature=self.temperature)
        elif "claude" in self.model:
            return ChatAnthropic(model=self.model, temperature=self.temperature)
        else:
            raise ValueError("Model not supported")
        
    def get_correct_pandasai_llm(self):
        """ provide the correct LLM for the pandasai agent
        
        PandasAI allows Langchain model as input"""
        if "gpt" in self.model:
            return OpenAI(model=self.model, temperature=self.temperature, openai_api_key=self.get_correct_api_key())
        # Anthropic currently not supported
        # elif "claude" in self.model:
        #     return Anthropic(model=self.model, temperature=self.temperature, anthropic_api_key=self.get_correct_api_key())
        else:
            raise ValueError("Model not supported")
