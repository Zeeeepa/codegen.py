"""
Run command implementation
Handles agent execution with prompts
"""

from typing import Optional

from ..agents import Agent
from ..tasks import Task


class RunCommand:
    """Command to run agents with prompts"""

    def __init__(self, agent: Agent):
        self.agent = agent

    def execute(
        self,
        prompt: str,
        wait: bool = False,
        timeout: Optional[int] = None,
        poll_interval: float = 5.0,
        **kwargs,
    ) -> Task:
        """
        Execute an agent run with the given prompt

        Args:
            prompt: The prompt to send to the agent
            wait: Whether to wait for completion
            timeout: Timeout in seconds for waiting
            poll_interval: Polling interval for status checks
            **kwargs: Additional parameters to pass to the agent

        Returns:
            Task object representing the agent run
        """
        print(f"🚀 Running agent with prompt: {prompt}")

        # Create and start the task
        task = self.agent.run(prompt, **kwargs)
        print(f"📋 Task created: {task.id}")
        print(f"🔗 Status: {task.status}")

        if wait:
            print("⏳ Waiting for completion...")
            try:
                result = task.wait_for_completion(timeout=timeout, poll_interval=poll_interval)

                print(f"✅ Task completed with status: {result.status}")
                if result.result:
                    print(f"📄 Result: {result.result}")
                if result.github_pull_request:
                    pr = result.github_pull_request
                    print(f"🔗 GitHub PR: {pr.title} ({pr.url})")

            except TimeoutError:
                print(f"⏰ Task did not complete within {timeout} seconds")
                print(f"📋 Current status: {task.status}")

        return task
