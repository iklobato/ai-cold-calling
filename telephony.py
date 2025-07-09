import logging
from twilio.rest import Client
from config import Config
from models import Contact

def initiate_call(contact: Contact, call_id: str, config: Config, twiml_url: str) -> str:
    """
    Initiate an outbound call using Twilio.
    Returns the call SID.
    """
    try:
        client = Client(config.twilio_account_sid, config.twilio_auth_token)
        call = client.calls.create(
            to=contact.phone_number,
            from_=config.twilio_phone_number,
            url=twiml_url,
            timeout=config.conversation_timeout
        )
        logging.info(f"Call initiated: {contact.phone_number} -> {call.sid} (Prompt: {contact.prompt_name})")
        return call.sid
    except Exception as e:
        logging.error(f"Twilio call failed for {contact.phone_number}: {e}")
        raise 