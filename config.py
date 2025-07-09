import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    csv_file: str = os.getenv("CSV_FILE_PATH", "contacts.csv")
    prompts_dir: str = os.getenv("PROMPTS_DIR", "prompts")
    max_concurrent_calls: int = int(os.getenv("MAX_CONCURRENT_CALLS", "3"))
    calling_hours_start: int = int(os.getenv("CALLING_HOURS_START", "9"))
    calling_hours_end: int = int(os.getenv("CALLING_HOURS_END", "17"))
    timezone: str = os.getenv("TIMEZONE", "US/Eastern")
    conversation_timeout: int = int(os.getenv("CONVERSATION_TIMEOUT", "120")) 