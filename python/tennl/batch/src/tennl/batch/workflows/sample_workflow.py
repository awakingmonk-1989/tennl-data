import asyncio
from typing import Any

from llama_index.core.base.llms.types import CompletionResponse
from llama_index.core.llms import LLM
from llama_index.core.workflow import step
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent

class JokeEvent(Event):
    topic: str
    joke: str


class SampleWorkflow(Workflow):
    name: str = "This is my sample workflow"
    llm: LLM
    az_endpoint: str = ""
    api_key: str = ""
    model = ""
    api_version=""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = AzureOpenAI(
            azure_endpoint=self.az_endpoint,
            api_key=self.api_key,
            model=self.model,
            engine=self.model,
            api_version=self.api_version,
        )

    @step
    async def create_joke(self, ev: StartEvent) -> JokeEvent:
        prompt = (
            "Create a joke in Telugu that suits all age groups. "
            f"Topic: {ev.topic}. It should be clean, friendly, and funny."
        )
        output: CompletionResponse = await self.llm.acomplete(prompt)
        print(f"Create Joke Output: \n{output}")

        print(f"\n\nModel raw output : \n\n")
        print(f"{output.model_dump_json(indent=2)}")

        return JokeEvent(joke=str(output), topic=ev.topic)

    @step
    async def validate_joke(self, ev: JokeEvent) -> StopEvent:
        print(f"Validating joke. Topic: {ev.topic}")
        prompt = (
            "Validate if this joke is extremely funny. Respond with JSON containing exactly 2 fields: "
            "validation_result (bool) and validation_reason (str)."
        )
        output = await self.llm.acomplete(prompt)

        print(f"\n\nModel raw output : \n\n")
        print(f"{output.model_dump_json(indent=2)}")
        return StopEvent(result=str(output))




async def execute_workflow():
    workflow = SampleWorkflow(timeout=60, verbose=True)
    # returns the workflow handler
    result = await workflow.run(topic="Life")
    print(str(result))

if __name__ == "__main__":
    asyncio.run(execute_workflow())









