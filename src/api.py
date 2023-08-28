# The Steamship runtime will pick up the AgentService that you have defined in api.py
#
# Here, we're importing a basic example and re-exporting it so that the Steamship Runtime will pick it up.
#
# To build your own, copy-paste one of the examples form src/example_agents into this file and edit.
from example_agents.basic_agent import BasicAgentService


class MyAgentService(BasicAgentService):
    pass
