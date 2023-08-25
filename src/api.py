from steamship.utils.repl import AgentREPL

from example_agents.basic_agent import BasicAgent


class AgentService(BasicAgent):
    """Note: this just permits Steamship's bundler to detect that this is the agent we want to deploy."""

    pass


if __name__ == "__main__":
    """Run a REPL for this agent.

    The preferred approach, however, is to locate this agent in `api.py` and then run `ship run local`.
    """
    AgentREPL(
        AgentService,
        agent_package_config={},
    ).run()
