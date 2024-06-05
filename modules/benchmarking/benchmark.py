from langchain.agents import AgentExecutor
from langchain_core.runnables import Runnable

from langsmith import Client
from langsmith.schemas import Example, Run
from langsmith.evaluation import evaluate

from modules.llm.llm_settings import LLMSettings
from modules.llm.agent_library import AgentLibrary

""" create benchmark for testing BIM IR with Langsmith """

DATASET = [
    ["Was ist der größte Raum im 2.Stock?", ["Bibliothek"]],
    ["Was ist der größte Raum im 1.Stock?", ["Aula"]],
]


class BenchmarkTesting:

    def __init__(self, name, dataset: None):
        """ Initialize the BenchmarkTesting object"""
        self.name = name
        if dataset is None:
            self.benchmark = DATASET
        else:
            self.dataset = benchmark
    
    def run_runnable_evaluation(self, dataset_name: str, runnable: Runnable, description = None):
        """ run the evaluation of the benchmark with Langsmith """

        # evaluate the correctness of the label
        results = evaluate(
            runnable.invoke,
            data=dataset_name,
            evaluators=[self.correct_label],
            experiment_prefix=self.name,
            description=description,  # optional
        )

        return results

    
    def correct_label(root_run: Run, example: Example) -> dict:
        """ eval_test: evaluate the correctness of the label """
        # check if the output is the correct label
        score = root_run.outputs.get("output") == example.outputs.get("label")

        return {"score": int(score), "key": "correct_label"}

    def test_different_models(self):
        settings = LLMSettings()
        agentlibrary = AgentLibrary(settings)
        for model in LLMSettings.MODEL_OPTIONS:
            settings.model = model
            agentlibrary.settings = settings
            agent = agentlibrary.setup_OpenAI_agent([], None)
            agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
            score = self.run_benchmark(agent_executor)
            print(f"Model: {model}: {score}")

    def create_langsmith_client(self):
        """ create a Langsmith client and dataset with the benchmark"""
        # initialize the client
        client = Client()
        
        # create a dataset
        dataset = client.create_dataset(
            dataset_name=self.name,
            description = "BIM IR Benchmark",
        )
        
        # convert the benchmark into two lists
        dataset_inputs, dataset_outputs = self._convert_benchmark_in_splitted_lists()
        
        # create examples
        client.create_examples(
            inputs=[{"question": q} for q in dataset_inputs],
            outputs=dataset_outputs,
            dataset_id=dataset.id,
        )

        return client
    
    def _convert_benchmark_in_splitted_lists(self):
        """ converts the benchmark into two lists, one for inputs and one for outputs 
        this is needed for creating the Langsmith dataset"""
        
        inputs = [x[0] for x in self.benchmark]
        outputs = [{"must_mention": x[1]} for x in self.benchmark]
        return inputs, outputs

