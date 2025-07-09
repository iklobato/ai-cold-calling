from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

class CallStatus(Enum):
    PENDING = "pending"
    CALLING = "calling"
    COMPLETED = "completed"
    FAILED = "failed"
    OPTED_OUT = "opted_out"

@dataclass
class Contact:
    phone_number: str
    name: str
    email: str = ""
    company: str = ""
    status: str = CallStatus.PENDING.value
    call_attempts: int = 0
    consent_obtained: bool = False
    opt_out_date: str = ""
    prompt_name: str = "default"

@dataclass
class ConversationState:
    contact: Contact
    call_id: str
    conversation_history: Optional[List[Dict]] = None
    current_step: str = "introduction"
    is_active: bool = True
    opt_out_requested: bool = False

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = [] 