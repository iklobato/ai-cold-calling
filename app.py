#!/usr/bin/env python3

import asyncio
import csv
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, time
from pathlib import Path
from typing import List, Optional, Dict
from enum import Enum

import httpx
import pytz
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from TTS.api import TTS
from vosk import Model as VoskModel, KaldiRecognizer
import wave
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from twilio.rest import Client

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
    conversation_history: List[Dict] = None
    current_step: str = "introduction"
    is_active: bool = True
    opt_out_requested: bool = False

    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class AIConversationManager:
    def __init__(self, config: Config):
        self.config = config
        # Mistral LLM setup
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
        self.model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )
        # Coqui TTS setup
        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        # Vosk STT setup (ensure model is downloaded and path is correct)
        self.vosk_model = VoskModel("models/vosk-model-small-en-us-0.15")
        self.prompts = self.load_prompts()
        self.active_conversations: Dict[str, ConversationState] = {}
        logging.info("AIConversationManager initialized.")
        
    def load_prompts(self) -> Dict[str, PromptTemplate]:
        prompts = {}
        prompts_dir = Path(self.config.prompts_dir)
        prompts_dir.mkdir(exist_ok=True)
        logging.info(f"Loading prompts from {prompts_dir.resolve()}")
        
        for prompt_file in prompts_dir.glob("*.txt"):
            prompt_name = prompt_file.stem
            try:
                content = prompt_file.read_text().strip()
                if content:
                    prompts[prompt_name] = PromptTemplate.from_template(content)
                    logging.info(f"Loaded prompt: {prompt_name}")
                else:
                    logging.warning(f"Prompt file {prompt_file} is empty.")
            except Exception as e:
                logging.error(f"Error loading prompt {prompt_name}: {e}")
        logging.info(f"Total prompts loaded: {len(prompts)}")
        return prompts
    
    def get_system_prompt(self, contact: Contact) -> PromptTemplate:
        prompt_name = contact.prompt_name if contact.prompt_name in self.prompts else "default"
        prompt_template = self.prompts.get(prompt_name, self.prompts.get("default"))
        if not prompt_template:
            logging.warning(f"No prompt found for {contact.prompt_name}, using fallback")
            prompt_template = PromptTemplate.from_template(
                "No prompt found. Please add a prompt file in the prompts directory.\nPROSPECT INFORMATION:\n- Name: {name}\n- Company: {company}\n- Email: {email}\n- Phone: {phone_number}\n"
            )
        logging.debug(f"Selected prompt template: {prompt_name}")
        return prompt_template
    
    def reload_prompts(self):
        self.prompts = self.load_prompts()
        logging.info(f"Reloaded {len(self.prompts)} prompts: {list(self.prompts.keys())}")
    
    def get_available_prompts(self) -> List[str]:
        return list(self.prompts.keys())
    
    async def start_conversation(self, contact: Contact, call_id: str) -> ConversationState:
        logging.info(f"Starting conversation for call_id={call_id}, contact={contact.phone_number}")
        conversation = ConversationState(
            contact=contact,
            call_id=call_id,
            conversation_history=[],
            current_step="introduction",
            is_active=True
        )
        
        self.active_conversations[call_id] = conversation
        
        prompt_template = self.get_system_prompt(contact)
        initial_message = await self.generate_response(prompt_template, "", conversation)
        
        conversation.conversation_history.append({
            "role": "assistant",
            "content": initial_message,
            "timestamp": datetime.now().isoformat()
        })
        logging.debug(f"Initial message for {call_id}: {initial_message}")
        
        return conversation
    
    async def generate_response(self, system_prompt: PromptTemplate, user_input: str, conversation: ConversationState) -> str:
        try:
            logging.debug(f"Generating response for call_id={conversation.call_id}, user_input='{user_input}'")
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation.conversation_history[-5:]
            ])
            prompt_vars = {
                "name": conversation.contact.name,
                "company": conversation.contact.company,
                "email": conversation.contact.email,
                "phone_number": conversation.contact.phone_number,
                "agent_name": "AI Agent",
                "conversation_history": conversation_context,
                "user_input": user_input
            }
            base_prompt = system_prompt.format(**prompt_vars)
            full_prompt = (
                f"{base_prompt}\n\nCONVERSATION HISTORY:\n{conversation_context}\n\nUSER INPUT: {user_input}\n\n"
                "Generate a natural, conversational response. Keep it under 30 seconds when spoken."
            )
            # Use Mistral for generation
            result = self.generator(full_prompt, max_new_tokens=200, do_sample=True, temperature=0.7)
            return result[0]['generated_text'].strip()
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "I apologize, I'm having technical difficulties. Let me transfer you to a human representative."
    
    async def process_user_input(self, call_id: str, user_input: str) -> Optional[str]:
        logging.info(f"Processing user input for call_id={call_id}: {user_input}")
        conversation = self.active_conversations.get(call_id)
        if not conversation or not conversation.is_active:
            logging.warning(f"No active conversation for call_id={call_id}")
            return None
        
        opt_out_keywords = ['stop', 'remove', 'unsubscribe', 'do not call', 'take me off']
        if any(keyword in user_input.lower() for keyword in opt_out_keywords):
            conversation.opt_out_requested = True
            conversation.is_active = False
            logging.info(f"Opt-out requested for call_id={call_id}")
            return "I understand. I'll remove you from our list immediately. Thank you for your time. Have a great day!"
        
        conversation.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        system_prompt = self.get_system_prompt(conversation.contact)
        response = await self.generate_response(system_prompt, user_input, conversation)
        
        conversation.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        logging.debug(f"Assistant response for call_id={call_id}: {response}")
        return response
    
    async def text_to_speech(self, text: str) -> bytes:
        try:
            logging.info(f"Converting text to speech: {text[:60]}...")
            temp_path = "temp_tts.wav"
            self.tts.tts_to_file(text=text, file_path=temp_path)
            with open(temp_path, "rb") as f:
                audio_content = f.read()
            os.remove(temp_path)
            return audio_content
        except Exception as e:
            logging.error(f"TTS error: {e}")
            return b""
    
    async def speech_to_text(self, audio_data: bytes) -> str:
        try:
            logging.info("Converting speech to text.")
            temp_path = "temp_stt.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_data)
            wf = wave.open(temp_path, "rb")
            rec = KaldiRecognizer(self.vosk_model, wf.getframerate())
            result = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = rec.Result()
                    result += json.loads(res).get("text", "")
            res = rec.FinalResult()
            result += json.loads(res).get("text", "")
            wf.close()
            os.remove(temp_path)
            return result.strip()
        except Exception as e:
            logging.error(f"STT error: {e}")
            return ""
    
    def end_conversation(self, call_id: str) -> Optional[Dict]:
        conversation = self.active_conversations.get(call_id)
        if not conversation:
            logging.warning(f"No conversation found to end for call_id={call_id}")
            return None
        
        summary = {
            "call_id": call_id,
            "contact": asdict(conversation.contact),
            "duration": len(conversation.conversation_history),
            "opt_out_requested": conversation.opt_out_requested,
            "conversation_history": conversation.conversation_history
        }
        
        del self.active_conversations[call_id]
        logging.info(f"Ended conversation for call_id={call_id}")
        return summary

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
        # Do not add any sample data. All data must come from the CSV file provided by the user.
    
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
                # Twilio call initiation
                client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)
                twiml_url = f"https://yourapp.com/twiml/{call_id}"  # Placeholder, should point to your TwiML handler
                call = client.calls.create(
                    to=contact.phone_number,
                    from_=self.config.twilio_phone_number,
                    url=twiml_url,
                    timeout=self.config.conversation_timeout
                )
                call_sid = call.sid
                self.logger.info(f"Call initiated: {contact.phone_number} -> {call_sid} (Prompt: {contact.prompt_name})")
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

async def main():
    try:
        system = CallSystem()
        await system.run()
    except Exception as e:
        logging.error(f"Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🤖 AI-Powered Cold Calling System")
    print("=" * 50)
    print("Features:")
    print("✅ Google AI (Gemini) for conversations")
    print("✅ File-based prompts (prompts/*.txt)")
    print("✅ CSV contact management")
    print("✅ TCPA compliance built-in")
    print("✅ Conversation logging")
    print("✅ Opt-out handling")
    print("=" * 50)
    print("Setup:")
    print("1. pip install google-generativeai google-cloud-speech google-cloud-texttospeech httpx pytz python-dotenv")
    print("2. Create .env file with API keys")
    print("3. Add contacts to contacts.csv")
    print("4. Run: python ai_cold_calling.py")
    print("=" * 50)
    
    asyncio.run(main())
    