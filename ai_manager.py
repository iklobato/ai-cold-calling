import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from langchain.prompts import PromptTemplate
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from TTS.api import TTS
from vosk import Model as VoskModel, KaldiRecognizer
import torch
import json
import os
import wave
from config import Config
from models import Contact, ConversationState

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
            "contact": conversation.contact,
            "duration": len(conversation.conversation_history),
            "opt_out_requested": conversation.opt_out_requested,
            "conversation_history": conversation.conversation_history
        }
        del self.active_conversations[call_id]
        logging.info(f"Ended conversation for call_id={call_id}")
        return summary 