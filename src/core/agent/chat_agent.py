from typing import List, Tuple
from langchain.agents import AgentExecutor, ConversationalChatAgent
from langchain.agents.conversational_chat.prompt import PREFIX
from langchain.memory import ConversationBufferWindowMemory
from steamship_langchain.llms import OpenAIChat
from langchain.schema import (
    AgentAction,
    AIMessage,
    BaseMessage,
    HumanMessage,
)

from core.agent.base import BaseAgent
from core.chat_parser import ChatCustomParser

TEMPERATURE = 0.7
MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4"

PREFIX = """Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Assistant always answers with the personality of {personality}

When Assistant whishes to respond with a UUID, it responds with only the UUID and nothing else.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist."""


TEMPLATE_TOOL_RESPONSE = """TOOL RESPONSE: 
---------------------
{observation}

USER'S INPUT
--------------------

Okay, so what is the response to my last comment? If it was a UUID, repeat the UUID and nothing else. If using information obtained from the tools you must mention it explicitly, without mentioning the tool names - I have forgotten all TOOL RESPONSES! Remember to respond with a markdown code snippet of a json blob with a single action, and NOTHING else. Remember I have a personality of {personality} when speaking!"""


class ConversationalChatAgentWithPersonality(ConversationalChatAgent):
    personality: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.personality = kwargs.get("personality")

    def _construct_scratchpad(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> List[BaseMessage]:
        """Construct the scratchpad that lets the agent continue its thought process.

        NOTE: This is copied out of LangChain because  LangChain does not allow modification of the
        TEMPLATE_TOOL_RESPONSE variable, which hard-codes in the requirement to not inflect the tool
        output with any particular personality.
        """
        thoughts: List[BaseMessage] = []
        for action, observation in intermediate_steps:
            thoughts.append(AIMessage(content=action.log))
            human_message = HumanMessage(
                content=TEMPLATE_TOOL_RESPONSE.format(
                    observation=observation, personality=self.personality
                )
            )
            thoughts.append(human_message)
        return thoughts


class ChatAgent(BaseAgent):
    name: str = "MyAgent"

    def get_agent(self):
        llm = OpenAIChat(
            client=self.client, temperature=TEMPERATURE, model_name=MODEL_NAME
        )

        sys_message = PREFIX.format(personality=self.get_personality())

        tools = self.get_tools()
        memory = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
        )

        agent = ConversationalChatAgentWithPersonality.from_llm_and_tools(
            llm,
            tools,
            personality=self.get_personality(),
            system_message=sys_message,
            output_parser=ChatCustomParser(),
        )
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=self.is_verbose_logging_enabled(),
        )
