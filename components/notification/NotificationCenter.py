```python
import streamlit as st
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import asyncio
from prometheus_client import Counter

# Notification metrics
notification_events = Counter(
    'notification_events_total',
    'Total notification events',
    ['type', 'priority']
)

class NotificationCenter:
    def __init__(self):
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = {
                'desktop_enabled': True,
                'email_enabled': False,
                'sound_enabled': True,
                'priority_threshold': 'info'
            }

    def add_notification(
        self,
        message: str,
        type: str = 'info',
        priority: str = 'normal',
        duration: int = 5,
        action: Dict[str, Any] = None
    ) -> None:
        """Add a new notification."""
        notification = {
            'id': len(st.session_state.notifications),
            'message': message,
            'type': type,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'action': action,
            'duration': duration
        }
        
        st.session_state.notifications.insert(0, notification)
        notification_events.labels(
            type=type,
            priority=priority
        ).inc()

        # Trigger desktop notification if enabled
        if st.session_state.notification_settings['desktop_enabled']:
            self._show_desktop_notification(notification)

    def render_notification_center(self):
        """Render the notification center UI."""
        with st.sidebar:
            st.subheader("Notifications")
            
            # Notification filters
            filter_type = st.multiselect(
                "Filter by type",
                ["info", "success", "warning", "error"],
                default=["info", "warning", "error"]
            )

            # Render notifications
            for notification in st.session_state.notifications:
                if notification['type'] in filter_type:
                    self._render_notification(notification)

            # Clear all button
            if st.button("Clear All"):
                st.session_state.notifications = []

    def _render_notification(self, notification: Dict[str, Any]):
        """Render a single notification."""
        with st.container():
            # Notification header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    self._get_notification_icon(notification['type']) +
                    f" **{notification['type'].title()}**"
                )
            with col2:
                timestamp = datetime.fromisoformat(notification['timestamp'])
                st.caption(self._format_time(timestamp))

            # Notification content
            st.markdown(notification['message'])

            # Action button if present
            if notification['action']:
                if st.button(
                    notification['action']['label'],
                    key=f"notification_{notification['id']}_action"
                ):
                    notification['action']['callback']()

            st.markdown("---")

    def _get_notification_icon(self, type: str) -> str:
        """Get icon for notification type."""
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        return icons.get(type, 'ℹ️')

    def _format_time(self, timestamp: datetime) -> str:
        """Format timestamp for display."""
        now = datetime.now()
        diff = now - timestamp

        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = diff.days
            return f"{days}d ago"

    def _show_desktop_notification(self, notification: Dict[str, Any]):
        """Show desktop notification."""
        try:
            import plyer
            plyer.notification.notify(
                title=f"Gray Ghost - {notification['type'].title()}",
                message=notification['message'],
                app_icon=None,
                timeout=notification['duration']
            )
        except ImportError:
            pass  # Desktop notifications not available
```