```python
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime

class NotificationManager:
    def __init__(self):
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []

    def add_notification(self, message: str, type: str = 'info', duration: int = 5):
        """Add a new notification."""
        st.session_state.notifications.append({
            'message': message,
            'type': type,
            'timestamp': datetime.now(),
            'duration': duration
        })

    def render_notifications(self):
        """Render all active notifications."""
        current_time = datetime.now()
        active_notifications = []

        for notification in st.session_state.notifications:
            time_diff = (current_time - notification['timestamp']).total_seconds()
            
            if time_diff < notification['duration']:
                self._render_notification(notification)
                active_notifications.append(notification)

        st.session_state.notifications = active_notifications

    def _render_notification(self, notification: Dict[str, Any]):
        """Render a single notification."""
        notification_styles = {
            'info': {'icon': 'ℹ️', 'color': 'blue'},
            'success': {'icon': '✅', 'color': 'green'},
            'warning': {'icon': '⚠️', 'color': 'orange'},
            'error': {'icon': '❌', 'color': 'red'}
        }

        style = notification_styles.get(notification['type'], notification_styles['info'])
        
        st.markdown(
            f"""
            <div style="padding: 10px; border-left: 5px solid {style['color']}; background-color: rgba(0,0,0,0.05); margin: 10px 0;">
                {style['icon']} {notification['message']}
            </div>
            """,
            unsafe_allow_html=True
        )
```