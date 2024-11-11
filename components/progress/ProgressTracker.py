```python
import streamlit as st
from typing import Dict, Any, List
import time

class ProgressTracker:
    def __init__(self):
        if 'tasks' not in st.session_state:
            st.session_state.tasks = {}
        if 'completed_tasks' not in st.session_state:
            st.session_state.completed_tasks = set()

    def add_task(self, task_id: str, description: str, total_steps: int = 1):
        """Add a new task to track."""
        st.session_state.tasks[task_id] = {
            'description': description,
            'total_steps': total_steps,
            'current_step': 0,
            'status': 'pending'
        }

    def update_task(self, task_id: str, step: int = None, status: str = None):
        """Update task progress."""
        if task_id in st.session_state.tasks:
            if step is not None:
                st.session_state.tasks[task_id]['current_step'] = step
            if status:
                st.session_state.tasks[task_id]['status'] = status
            if status == 'completed':
                st.session_state.completed_tasks.add(task_id)

    def render_progress(self):
        """Render progress bars for all tasks."""
        for task_id, task in st.session_state.tasks.items():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                progress = task['current_step'] / task['total_steps']
                st.progress(progress)
                
            with col2:
                status_color = {
                    'pending': '🟡',
                    'in_progress': '🔵',
                    'completed': '🟢',
                    'error': '🔴'
                }
                st.write(f"{status_color[task['status']]} {task['description']}")

    def get_overall_progress(self) -> float:
        """Calculate overall progress percentage."""
        if not st.session_state.tasks:
            return 0.0
        completed = len(st.session_state.completed_tasks)
        total = len(st.session_state.tasks)
        return (completed / total) * 100
```