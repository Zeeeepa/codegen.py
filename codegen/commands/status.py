"""
Status command implementation
Handles task status checking and listing
"""

from typing import Optional

from ..agents import Agent
from ..tasks import Task, TaskStatus


class StatusCommand:
    """Command to check task status and list tasks"""

    def __init__(self, agent: Agent):
        self.agent = agent

    def execute(
        self,
        task_id: Optional[int] = None,
        limit: int = 10,
        show_logs: bool = False,
        log_limit: int = 10,
    ) -> Optional[Task]:
        """
        Execute status command

        Args:
            task_id: Specific task ID to check (None to list recent tasks)
            limit: Number of tasks to list
            show_logs: Whether to show logs for specific task
            log_limit: Number of log entries to show

        Returns:
            Task object if checking specific task, None if listing
        """
        if task_id:
            return self._show_task_status(task_id, show_logs, log_limit)
        else:
            self._list_recent_tasks(limit)
            return None

    def _show_task_status(self, task_id: int, show_logs: bool, log_limit: int) -> Task:
        """Show status for a specific task"""
        task = self.agent.get_task(task_id)

        print(f"📋 Task {task.id}")
        print(f"🔗 Status: {task.status}")
        print(f"📅 Created: {task.created_at}")
        print(f"📅 Updated: {task.updated_at}")

        if task.result:
            print(f"📄 Result: {task.result}")
        if task.error:
            print(f"❌ Error: {task.error}")
        if task.github_pull_request:
            pr = task.github_pull_request
            print(f"🔗 GitHub PR: {pr.title} ({pr.url})")

        if show_logs:
            print("\\n📜 Recent logs:")
            logs = task.get_logs(limit=log_limit)
            for log in logs.logs:
                timestamp = log.created_at
                print(f"  [{timestamp}] {log.message_type}: {log.content}")

        return task

    def _list_recent_tasks(self, limit: int):
        """List recent tasks"""
        tasks = self.agent.list_tasks(limit=limit)
        print(f"📋 Recent tasks ({len(tasks)}):")

        for task in tasks:
            status_emoji = self._get_status_emoji(task.status)
            print(f"  {status_emoji} {task.id}: {task.status} ({task.created_at})")

    def _get_status_emoji(self, status: str) -> str:
        """Get emoji for task status"""
        return {
            TaskStatus.COMPLETED: "✅",
            TaskStatus.RUNNING: "🔄",
            TaskStatus.PENDING: "⏳",
            TaskStatus.FAILED: "❌",
            TaskStatus.CANCELLED: "🚫",
        }.get(status, "❓")
