import asyncio
import csv
import json
import logging
import re
import sys
from datetime import datetime, time
from pathlib import Path
from typing import List, Dict
import pytz
from dataclasses import asdict
from config import Config
from models import Contact, CallStatus
from ai_manager import AIConversationManager
from telephony import initiate_call

class CallSystem:
    def __init__(self):
        self.config = Config()
        self.validate_config()
        self.setup_logging()
        self.ai_manager = AIConversationManager(self.config)
        self.dnc_numbers = self.load_dnc_list()
        self.timezone = pytz.timezone(self.config.timezone)
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_calls)
        logging.info("CallSystem initialized.")

    def validate_config(self):
        required = [
            self.config.twilio_account_sid,
            self.config.twilio_auth_token,
            self.config.twilio_phone_number
        ]
        if not all(required):
            logging.error("Missing required Twilio API keys")
            raise ValueError("Missing required Twilio API keys")
        logging.info("Config validated.")

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('calling_system.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        logging.info("Logging setup complete.")

    def load_dnc_list(self) -> set:
        dnc_file = Path("dnc_list.txt")
        if dnc_file.exists():
            dnc_numbers = {line.strip() for line in dnc_file.read_text().splitlines() if line.strip()}
            logging.info(f"Loaded {len(dnc_numbers)} DNC numbers.")
            return dnc_numbers
        logging.info("No DNC list found.")
        return set()

    def normalize_phone(self, phone: str) -> str:
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            digits = '1' + digits
        normalized = '+' + digits
        logging.debug(f"Normalized phone {phone} to {normalized}")
        return normalized

    def is_callable(self, contact: Contact) -> bool:
        if not contact.consent_obtained or contact.opt_out_date:
            logging.info(f"Contact {contact.phone_number} not callable: consent={contact.consent_obtained}, opt_out_date={contact.opt_out_date}")
            return False
        if self.normalize_phone(contact.phone_number) in self.dnc_numbers:
            logging.info(f"Contact {contact.phone_number} is on DNC list.")
            return False
        current_time = datetime.now(self.timezone).time()
        within_hours = (time(self.config.calling_hours_start, 0) <= current_time <=
                time(self.config.calling_hours_end, 0))
        logging.debug(f"Current time {current_time}, within calling hours: {within_hours}")
        return within_hours

    def load_contacts(self) -> List[Contact]:
        csv_file = Path(self.config.csv_file)
        if not csv_file.exists():
            self.create_csv()
            logging.info(f"Created new contacts CSV at {csv_file}")
            return []
        contacts = []
        with open(csv_file, 'r') as f:
            for row in csv.DictReader(f):
                if row.get('phone_number') and row.get('name'):
                    contacts.append(Contact(
                        phone_number=row['phone_number'],
                        name=row['name'],
                        email=row.get('email', ''),
                        company=row.get('company', ''),
                        status=row.get('status', CallStatus.PENDING.value),
                        call_attempts=int(row.get('call_attempts', 0)),
                        consent_obtained=row.get('consent_obtained', 'false').lower() == 'true',
                        opt_out_date=row.get('opt_out_date', ''),
                        prompt_name=row.get('prompt_name', 'default')
                    ))
        logging.info(f"Loaded {len(contacts)} contacts from CSV.")
        return contacts

    def create_csv(self):
        headers = ['phone_number', 'name', 'email', 'company', 'status', 'call_attempts', 'consent_obtained', 'opt_out_date', 'prompt_name']
        with open(self.config.csv_file, 'w', newline='') as f:
            csv.DictWriter(f, fieldnames=headers).writeheader()
        logging.info(f"Created contacts CSV with headers: {headers}")

    def save_contacts(self, contacts: List[Contact]):
        headers = ['phone_number', 'name', 'email', 'company', 'status', 'call_attempts', 'consent_obtained', 'opt_out_date', 'prompt_name']
        with open(self.config.csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for contact in contacts:
                writer.writerow(asdict(contact))
        logging.info(f"Saved {len(contacts)} contacts to CSV.")

    def update_contact_status(self, phone_number: str, status: str, increment_attempts: bool = False):
        contacts = self.load_contacts()
        for contact in contacts:
            if contact.phone_number == phone_number:
                contact.status = status
                if increment_attempts:
                    contact.call_attempts += 1
                break
        self.save_contacts(contacts)

    def save_conversation_log(self, conversation_summary: Dict):
        log_file = Path("conversation_logs.jsonl")
        with open(log_file, 'a') as f:
            f.write(json.dumps(conversation_summary) + "\n")

    def validate_contact_prompts(self):
        contacts = self.load_contacts()
        available_prompts = self.ai_manager.get_available_prompts()
        invalid_contacts = []
        for contact in contacts:
            if contact.prompt_name not in available_prompts:
                invalid_contacts.append(f"{contact.name} ({contact.phone_number}) - prompt: {contact.prompt_name}")
        if invalid_contacts:
            self.logger.warning(f"Found {len(invalid_contacts)} contacts with invalid prompts:")
            for contact in invalid_contacts:
                self.logger.warning(f"  - {contact}")
            self.logger.info("These contacts will use the 'default' prompt")

    async def make_call(self, contact: Contact) -> dict:
        async with self.semaphore:
            call_id = f"call_{contact.phone_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                if not self.is_callable(contact):
                    return {"status": "blocked", "phone": contact.phone_number}
                self.update_contact_status(contact.phone_number, CallStatus.CALLING.value, True)
                conversation = await self.ai_manager.start_conversation(contact, call_id)
                twiml_url = f"https://yourapp.com/twiml/{call_id}"  # Placeholder, should point to your TwiML handler
                call_sid = initiate_call(contact, call_id, self.config, twiml_url)
                await asyncio.sleep(2)
                conversation_summary = self.ai_manager.end_conversation(call_id)
                if conversation_summary:
                    self.save_conversation_log(conversation_summary)
                final_status = CallStatus.OPTED_OUT.value if conversation.opt_out_requested else CallStatus.COMPLETED.value
                self.update_contact_status(contact.phone_number, final_status)
                return {
                    "status": "success",
                    "phone": contact.phone_number,
                    "call_sid": call_sid,
                    "conversation_id": call_id,
                    "opt_out": conversation.opt_out_requested
                }
            except Exception as e:
                self.logger.error(f"Call failed {contact.phone_number}: {e}")
                self.update_contact_status(contact.phone_number, CallStatus.FAILED.value)
                return {"status": "failed", "phone": contact.phone_number, "error": str(e)}

    async def run_calling_session(self):
        contacts = [c for c in self.load_contacts() if c.status == CallStatus.PENDING.value]
        callable_contacts = [c for c in contacts if self.is_callable(c)][:self.config.max_concurrent_calls]
        if not callable_contacts:
            self.logger.info("No callable contacts")
            return
        self.logger.info(f"Calling {len(callable_contacts)} contacts")
        tasks = [self.make_call(contact) for contact in callable_contacts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
        opt_outs = sum(1 for r in results if isinstance(r, dict) and r.get("opt_out"))
        self.logger.info(f"Session complete: {successful}/{len(results)} successful, {opt_outs} opt-outs")

    async def run(self):
        self.logger.info("Starting LLM-Powered Cold Calling System")
        available_prompts = self.ai_manager.get_available_prompts()
        self.logger.info(f"Available prompts ({len(available_prompts)}): {', '.join(available_prompts)}")
        self.validate_contact_prompts()
        prompts_dir = Path(self.config.prompts_dir)
        self.logger.info(f"Prompt files location: {prompts_dir.absolute()}")
        self.logger.info("To add new prompts: create new .txt files in the prompts directory")
        try:
            while True:
                if self.is_calling_hours_active():
                    await self.run_calling_session()
                    await asyncio.sleep(300)
                else:
                    self.logger.info("Outside calling hours")
                    await asyncio.sleep(3600)
        except KeyboardInterrupt:
            self.logger.info("Shutting down")

    def is_calling_hours_active(self) -> bool:
        current_time = datetime.now(self.timezone).time()
        return (time(self.config.calling_hours_start, 0) <= current_time <=
                time(self.config.calling_hours_end, 0)) 