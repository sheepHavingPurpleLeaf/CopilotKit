"""Fixed LangGraph Agent to resolve messages_in_process initialization issues"""

from typing import Optional, Dict, Any, Union
from ag_ui_langgraph import LangGraphAgent
from langchain_core.runnables import RunnableConfig


class FixedLangGraphAgent(LangGraphAgent):
    """
    Fixed version of LangGraphAgent that ensures messages_in_process is always properly initialized
    and provides robust error handling for the streaming interface.
    """
    
    def __init__(self, *, name: str, graph, description: Optional[str] = None, 
                 config: Union[Optional[RunnableConfig], dict] = None):
        """Initialize the agent with guaranteed messages_in_process initialization"""
        super().__init__(name=name, graph=graph, description=description, config=config)
        
        # Force initialize messages_in_process as a dictionary
        self.messages_in_process = {}
        
        print(f"✅ FixedLangGraphAgent '{name}' initialized with messages_in_process: {type(self.messages_in_process)}")
    
    def set_message_in_progress(self, run_id: str, message_data: dict):
        """Override to ensure messages_in_process is always a dict"""
        if not hasattr(self, 'messages_in_process') or self.messages_in_process is None:
            print("⚠️ messages_in_process was None, reinitializing...")
            self.messages_in_process = {}
        
        if not isinstance(self.messages_in_process, dict):
            print(f"⚠️ messages_in_process was {type(self.messages_in_process)}, converting to dict...")
            self.messages_in_process = {}
        
        try:
            self.messages_in_process[run_id] = message_data
            print(f"✅ Message set for run_id {run_id[:8]}...")
        except Exception as e:
            print(f"❌ Error setting message in progress: {e}")
            # Reinitialize and try again
            self.messages_in_process = {}
            self.messages_in_process[run_id] = message_data
            print(f"✅ Recovered and set message for run_id {run_id[:8]}...")
        
    def get_message_in_progress(self, run_id: str):
        """Get a message in progress, ensuring dict is initialized"""
        if not hasattr(self, 'messages_in_process') or self.messages_in_process is None:
            print("⚠️ messages_in_process was None in get_message, reinitializing...")
            self.messages_in_process = {}
        
        if not isinstance(self.messages_in_process, dict):
            print(f"⚠️ messages_in_process was {type(self.messages_in_process)} in get_message, converting...")
            self.messages_in_process = {}
        
        return self.messages_in_process.get(run_id)
        
    def remove_message_in_progress(self, run_id: str):
        """Remove a message from progress tracking"""
        if not hasattr(self, 'messages_in_process') or self.messages_in_process is None:
            print("⚠️ messages_in_process was None in remove_message, reinitializing...")
            self.messages_in_process = {}
            return
        
        if not isinstance(self.messages_in_process, dict):
            print(f"⚠️ messages_in_process was {type(self.messages_in_process)} in remove_message, converting...")
            self.messages_in_process = {}
            return
        
        try:
            removed = self.messages_in_process.pop(run_id, None)
            if removed:
                print(f"✅ Removed message for run_id {run_id[:8]}...")
        except Exception as e:
            print(f"❌ Error removing message: {e}")
            # Reset the dict if there's an error
            self.messages_in_process = {}
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to prevent messages_in_process from being set to None"""
        if name == 'messages_in_process' and value is None:
            print("🛡️ Preventing messages_in_process from being set to None")
            super().__setattr__(name, {})
        else:
            super().__setattr__(name, value)
    
    def reset_message_state(self):
        """Public method to reset message state if needed"""
        print("🔄 Resetting message state...")
        self.messages_in_process = {}
        print("✅ Message state reset complete")