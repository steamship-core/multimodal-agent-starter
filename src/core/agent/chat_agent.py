from langchain.agents import AgentExecutor, ConversationalChatAgent
from langchain.agents.conversational_chat.prompt import PREFIX
from langchain.memory import ConversationBufferWindowMemory
from steamship_langchain.llms import OpenAIChat

from core.agent.base import BaseAgent
from core.chat_parser import ChatCustomParser

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"


class ChatAgent(BaseAgent):
    name: str = "MyAgent"

    def get_agent(self):
        llm = OpenAIChat(
            client=self.client, temperature=TEMPERATURE, model_name=MODEL_NAME
        )

        sys_message = (
            f"{PREFIX}\n Please take on the personality of {self.get_personality()}"
        )

        tools = self.get_tools()
        memory = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
        )

        agent = ConversationalChatAgent.from_llm_and_tools(
            llm, tools, system_message=sys_message, output_parser=ChatCustomParser()
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=self.is_verbose_logging_enabled(),
        )
