```python
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime
from ..progress.ProgressTracker import ProgressTracker
from ..notification.NotificationManager import NotificationManager

class TaskManager:
    def __init__(self):
        self.progress_tracker = ProgressTracker()
        self.notification_manager = NotificationManager()

    def render_task_manager(self, tasks: List[Dict[str, Any]]):
        """Render task management interface."""
        st.subheader("Task Manager")

        # Task Overview
        self._render_task_overview(tasks)

        # Active Tasks
        self._render_active_tasks(tasks)

        # Task History
        self._render_task_history(tasks)

        # Task Queue Status
        self._render_queue_status()

    def _render_task_overview(self, tasks: List[Dict[str, Any]]):
        """Render task overview metrics."""
        active_tasks = [t for t in tasks if t['status'] == 'running']
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        failed_tasks = [t for t in tasks if t['status'] == 'failed']

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Active Tasks", len(active_tasks))
        with col2:
            st.metric("Completed Tasks", len(completed_tasks))
        with col3:
            st.metric("Failed Tasks", len(failed_tasks))
        with col4:
            success_rate = (len(completed_tasks) / len(tasks)) * 100 if tasks else 0
            st.metric("Success Rate", f"{success_rate:.1f}%")

    def _render_active_tasks(self, tasks: List[Dict[str, Any]]):
        """Render active tasks section."""
        st.subheader("Active Tasks")

        active_tasks = [t for t in tasks if t['status'] == 'running']
        if not active_tasks:
            st.info("No active tasks")
            return

        for task in active_tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(f"**{task['name']}**")
                    st.write(f"Started: {task['start_time']}")
                    self.progress_tracker.render_progress()

                with col2:
                    st.write(f"Queue: {task['queue']}")
                    st.write(f"Priority: {task['priority']}")

                with col3:
                    if st.button("Cancel", key=f"cancel_{task['id']}"):
                        self._cancel_task(task['id'])

    def _render_task_history(self, tasks: List[Dict[str, Any]]):
        """Render task history section."""
        st.subheader("Task History")

        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Status",
                options=["completed", "failed", "cancelled"],
                default=["completed", "failed"]
            )
        with col2:
            date_range = st.date_input(
                "Date Range",
                value=[datetime.now().date()]
            )

        # Filter tasks
        filtered_tasks = [
            t for t in tasks
            if t['status'] in status_filter
            and datetime.fromisoformat(t['end_time']).date() in date_range
        ]

        # Display tasks
        if not filtered_tasks:
            st.info("No tasks found")
            return

        for task in filtered_tasks:
            with st.expander(f"{task['name']} - {task['status']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Task ID:** {task['id']}")
                    st.write(f"**Started:** {task['start_time']}")
                    st.write(f"**Ended:** {task['end_time']}")
                
                with col2:
                    st.write(f"**Duration:** {task['duration']:.2f}s")
                    st.write(f"**Queue:** {task['queue']}")
                    if task['status'] == 'failed':
                        st.error(f"Error: {task['error']}")

    def _render_queue_status(self):
        """Render queue status section."""
        st.subheader("Queue Status")

        queues = {
            'high_priority': {'size': 0, 'capacity': 1000},
            'medium_priority': {'size': 0, 'capacity': 5000},
            'low_priority': {'size': 0, 'capacity': 10000}
        }

        for queue_name, stats in queues.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                progress = stats['size'] / stats['capacity']
                st.progress(progress)
            
            with col2:
                st.write(f"{stats['size']}/{stats['capacity']}")

    def _cancel_task(self, task_id: str):
        """Cancel a running task."""
        try:
            # Cancel task logic here
            self.notification_manager.add_notification(
                f"Task {task_id} cancelled successfully",
                type="success"
            )
        except Exception as e:
            self.notification_manager.add_notification(
                f"Error cancelling task: {str(e)}",
                type="error"
            )
```