```python
import streamlit as st
from typing import Dict, Any, Callable, List
import asyncio
from datetime import datetime
import json
from prometheus_client import Counter, Gauge

# Update metrics
update_events = Counter(
    'live_update_events_total',
    'Total live update events',
    ['type']
)

active_subscribers = Gauge(
    'live_update_subscribers',
    'Number of active update subscribers',
    ['type']
)

class UpdateManager:
    def __init__(self):
        if 'update_handlers' not in st.session_state:
            st.session_state.update_handlers = {}
        if 'update_queue' not in st.session_state:
            st.session_state.update_queue = []
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()

    def register_handler(
        self,
        update_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Register an update handler."""
        if update_type not in st.session_state.update_handlers:
            st.session_state.update_handlers[update_type] = []
        st.session_state.update_handlers[update_type].append(handler)
        active_subscribers.labels(type=update_type).inc()

    def unregister_handler(
        self,
        update_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Unregister an update handler."""
        if update_type in st.session_state.update_handlers:
            handlers = st.session_state.update_handlers[update_type]
            if handler in handlers:
                handlers.remove(handler)
                active_subscribers.labels(type=update_type).dec()

    def push_update(
        self,
        update_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Push a new update to all subscribers."""
        update = {
            'type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.update_queue.append(update)
        update_events.labels(type=update_type).inc()
        
        # Process update
        self._process_update(update)

    def _process_update(self, update: Dict[str, Any]) -> None:
        """Process an update through registered handlers."""
        update_type = update['type']
        if update_type in st.session_state.update_handlers:
            for handler in st.session_state.update_handlers[update_type]:
                try:
                    handler(update['data'])
                except Exception as e:
                    st.error(f"Error processing update: {str(e)}")

    def start_live_updates(self, container: st.container):
        """Start live updates in a container."""
        with container:
            if st.button("Stop Updates"):
                st.session_state.live_updates_active = False
                return

            while st.session_state.live_updates_active:
                current_time = datetime.now()
                
                # Process any new updates
                if st.session_state.update_queue:
                    update = st.session_state.update_queue.pop(0)
                    self._process_update(update)
                    st.session_state.last_update = current_time

                # Rerun every second
                time.sleep(1)
                st.rerun()

    def render_update_status(self):
        """Render update status information."""
        st.sidebar.subheader("Live Updates")
        
        # Update status
        status = "Active" if getattr(st.session_state, 'live_updates_active', False) else "Inactive"
        st.sidebar.text(f"Status: {status}")
        
        # Last update time
        last_update = st.session_state.last_update
        time_since = datetime.now() - last_update
        st.sidebar.text(f"Last Update: {time_since.seconds}s ago")
        
        # Update controls
        if st.sidebar.button("Toggle Updates"):
            st.session_state.live_updates_active = not getattr(
                st.session_state,
                'live_updates_active',
                False
            )
```