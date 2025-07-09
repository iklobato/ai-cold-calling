# 🤖 AI-Powered Cold Calling System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Mistral LLM](https://img.shields.io/badge/LLM-Mistral%207B-blueviolet.svg)](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
[![Coqui TTS](https://img.shields.io/badge/TTS-Coqui%20TTS-orange.svg)](https://github.com/coqui-ai/TTS)
[![Vosk STT](https://img.shields.io/badge/STT-Vosk-yellowgreen.svg)](https://alphacephei.com/vosk/)
[![Twilio](https://img.shields.io/badge/Telephony-Twilio-red.svg)](https://www.twilio.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A sophisticated AI-powered cold calling system that automates phone outreach using local LLM (Mistral-7B-Instruct) for intelligent conversations, Coqui TTS for voice synthesis, Vosk for speech recognition, and Twilio for telephony. The system manages contacts via CSV files, uses customizable prompt-based sales scripts, and includes built-in TCPA compliance features.

---

## 🎯 What This System Does

### **Core Functionality**
- **Automated Cold Calling**: Dials prospects from a CSV database during business hours
- **AI-Powered Conversations**: Uses Mistral-7B-Instruct LLM to conduct natural, contextual sales conversations
- **Voice Processing**: Converts speech to text (Vosk) and text to speech (Coqui TTS) for real-time voice interactions
- **Multi-Product Support**: Different sales scripts for different products/services via prompt files
- **Compliance Management**: Built-in TCPA compliance with opt-out handling and calling hours
- **Conversation Logging**: Records full conversation transcripts for analysis and compliance
- **Lead Management**: Tracks call outcomes and updates contact statuses automatically

### **Business Use Cases**
- **Sales Teams**: Automate initial prospect outreach and qualification
- **Real Estate**: Contact homeowners about property opportunities
- **Insurance**: Reach prospects interested in coverage
- **SaaS Companies**: Demo scheduling and product introductions
- **E-commerce**: Upselling and customer engagement
- **Service Businesses**: Appointment setting and lead generation

---

## 🏗️ How The System Works

### **Technical Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────┐
│   CSV Database  │    │  Prompt Files   │    │   Mistral LLM (local)  │
│   (contacts.csv)│    │  (prompts/*.txt)│    │   (7B-Instruct)        │
└─────────────────┘    └─────────────────┘    └────────────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────────────────┐
                    │   Call System (app.py)       │
                    │  (Main Orchestration Script) │
                    └──────────────────────────────┘
                                 │
         ┌───────────────────────┼────────────────────────────────────────────┐
         │                       │                                            │
┌─────────────────┐    ┌─────────────────┐    ┌────────────────────────────┐
│  Vosk STT       │    │  Coqui TTS      │    │  Twilio Calling           │
│  (Speech-to-Text│    │  (Text-to-Speech│    │  (Telephony API)          │
└─────────────────┘    └─────────────────┘    └────────────────────────────┘
```

### **Call Flow Process**

1. **Contact Selection**: System reads `contacts.csv` and selects callable prospects
2. **Compliance Check**: Validates consent, calling hours, and DNC status
3. **Prompt Loading**: Loads appropriate sales script from `prompts/[prompt_name].txt`
4. **Call Initiation**: Twilio API dials the prospect's phone number using a TwiML handler URL
5. **Voice Processing**: Vosk Speech-to-Text captures prospect responses
6. **AI Processing**: Mistral LLM generates contextual responses based on conversation history
7. **Voice Synthesis**: Coqui TTS converts AI responses to voice
8. **Conversation Management**: Tracks conversation state and detects opt-out requests
9. **Call Completion**: Logs conversation transcript and updates contact status
10. **Compliance Handling**: Processes opt-out requests and updates DNC lists

### **Data Flow**

```
CSV Contact → Compliance Check → Prompt Selection → Call Initiation
     ↓
Voice Input → Speech-to-Text (Vosk) → LLM Processing (Mistral) → Response Generation
     ↓
Text-to-Speech (Coqui) → Voice Output → Conversation Continue/End
     ↓
Conversation Log → Contact Update → Compliance Update
```

---

## 🔧 System Components & Responsibilities

### **1. Main Application (`CallSystem` class in app.py)**
**Responsibility**: Orchestrates the entire calling process
- **Contact Management**: Loads, validates, and updates contact records
- **Session Management**: Runs calling sessions with concurrency control
- **Compliance Enforcement**: Checks calling hours, consent, and DNC lists
- **Logging**: Maintains system logs and conversation transcripts
- **Configuration**: Manages system settings and API credentials

### **2. AI Conversation Manager (`AIConversationManager` class)**
**Responsibility**: Handles AI-powered conversations
- **Prompt Management**: Loads and manages sales scripts from text files (using LangChain PromptTemplate)
- **Conversation State**: Tracks conversation history and context
- **LLM Integration**: Interfaces with Mistral-7B-Instruct for response generation
- **Voice Processing**: Manages speech-to-text (Vosk) and text-to-speech (Coqui TTS) operations
- **Opt-out Detection**: Recognizes and processes removal requests
- **Response Generation**: Creates contextual, natural responses

### **3. Contact Database (`contacts.csv`)**
**Responsibility**: Stores prospect information and call history
- **Contact Details**: Name, phone, email, company information
- **Call Status**: Tracks pending, calling, completed, failed states
- **Compliance Data**: Consent status, opt-out dates, call attempts
- **Prompt Assignment**: Links contacts to specific sales scripts
- **History Tracking**: Maintains call attempts and outcomes

### **4. Prompt System (`prompts/` directory)**
**Responsibility**: Manages customizable sales scripts
- **Script Storage**: Individual `.txt` files for different products/services
- **Dynamic Loading**: Automatically loads new prompts without restart
- **Fallback Handling**: Uses default prompt if specified prompt missing
- **Personalization**: Injects contact-specific information into scripts
- **Compliance Integration**: Includes required disclosures and opt-out handling

### **5. Compliance Manager (integrated)**
**Responsibility**: Ensures TCPA and regulatory compliance
- **Calling Hours**: Enforces business hours restrictions
- **Consent Verification**: Validates prospect consent before calling
- **DNC Management**: Maintains do-not-call lists and opt-out processing
- **AI Disclosure**: Ensures required AI technology disclosure
- **Audit Trail**: Maintains compliance logs and documentation

### **6. External API Integrations**

#### **Mistral LLM (local)**
**Responsibility**: Provides conversational intelligence
- **Natural Language Processing**: Understands prospect responses
- **Context Awareness**: Maintains conversation history
- **Response Generation**: Creates human-like responses
- **Objection Handling**: Processes and responds to sales objections
- **Personalization**: Adapts responses based on prospect information

#### **Coqui TTS (local)**
**Responsibility**: Handles voice synthesis
- **Text-to-Speech**: Converts AI responses to natural voice output
- **Audio Quality**: Ensures clear, professional voice synthesis
- **Language Support**: Handles multiple languages and accents

#### **Vosk STT (local)**
**Responsibility**: Handles voice recognition
- **Speech-to-Text**: Converts prospect voice to text for LLM processing
- **Language Support**: Handles multiple languages and accents

#### **Twilio Telephony**
**Responsibility**: Manages phone call operations
- **Call Routing**: Dials prospect phone numbers
- **Call Control**: Manages call duration and termination
- **TwiML Handler**: Uses a TwiML URL to control call flow (must be implemented by user)
- **Quality Assurance**: Ensures reliable call delivery

---

## 📋 Prerequisites

### **Required Services**
- **Twilio Account**: For phone calling capabilities
- **Python 3.8+**: Runtime environment
- **Local Model Files**: Download Mistral, Coqui TTS, and Vosk models as required

### **System Requirements**
- **Memory**: 8GB RAM minimum (16GB+ recommended for LLM)
- **Storage**: Several GB free space for models, logs, and data
- **Network**: Stable internet connection for Twilio API calls
- **OS**: Linux, macOS, or Windows

---

## 🚀 Installation & Setup

### **1. Clone and Install**
```bash
# Clone the repository
git clone <repository-url>
cd ai-call

# Install dependencies
pip install torch transformers TTS vosk httpx pytz python-dotenv langchain twilio
```

### **2. Model Downloads**
- Download the Mistral-7B-Instruct model from HuggingFace (see https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
- Download the Vosk English model (see https://alphacephei.com/vosk/models)
- Coqui TTS models are downloaded automatically on first use

### **3. API Configuration**

#### **Twilio Setup**
```bash
# Get credentials from https://console.twilio.com/
# Purchase phone number from Twilio dashboard
export TWILIO_ACCOUNT_SID="your_twilio_account_sid"
export TWILIO_AUTH_TOKEN="your_twilio_auth_token"
export TWILIO_PHONE_NUMBER="+1234567890"
```

### **4. Configuration File**

Create `.env` file in project root:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token  
TWILIO_PHONE_NUMBER=+1234567890

# System Configuration
CSV_FILE_PATH=contacts.csv
PROMPTS_DIR=prompts
MAX_CONCURRENT_CALLS=3
CALLING_HOURS_START=9
CALLING_HOURS_END=17
TIMEZONE=US/Eastern
CONVERSATION_TIMEOUT=120
```

### **5. Contact Database Setup**

The system auto-creates `contacts.csv` with headers only. **You must add your own contact data.** Format:

```csv
phone_number,name,email,company,status,call_attempts,consent_obtained,opt_out_date,prompt_name
```

**Column Descriptions:**
- `phone_number`: Contact's phone number (E.164 format: +1234567890)
- `name`: Contact's full name
- `email`: Contact's email address
- `company`: Contact's company name
- `status`: Call status (pending, calling, completed, failed, opted_out)
- `call_attempts`: Number of call attempts made
- `consent_obtained`: Boolean (true/false) - REQUIRED for TCPA compliance
- `opt_out_date`: Date when contact opted out (ISO format)
- `prompt_name`: Sales script to use (matches filename in prompts/ directory)

### **6. Prompt Configuration**

The system auto-creates the `prompts/` directory if missing. Add your prompt files as needed:

```
prompts/
├── default.txt          # General sales script
├── saas_product.txt     # SaaS/Software sales
├── real_estate.txt      # Real estate services
├── insurance.txt        # Insurance products
└── ecommerce.txt        # E-commerce solutions
```

**Prompt Structure:**
Each prompt file should include:
- **Introduction**: Opening greeting with AI disclosure
- **Value Proposition**: Key benefits and features
- **Qualifying Questions**: Questions to understand needs
- **Objection Handling**: Responses to common objections
- **Call-to-Action**: Next steps and closing
- **Compliance**: Opt-out handling instructions

---

## 🎮 Usage

### **Start the System**
```bash
python app.py
```

### **System Output**
```
🤖 AI-Powered Cold Calling System
==================================================
Starting LLM-Powered Cold Calling System
Loaded prompt: default
Loaded prompt: saas_product
Available prompts (5): default, saas_product, real_estate, insurance, ecommerce
Prompt files location: /path/to/prompts
To add new prompts: create new .txt files in the prompts directory
Calling 3 contacts
Call initiated: +1234567890 -> call_sid_123 (Prompt: saas_product)
Session complete: 3/3 successful, 1 opt-outs
```

### **Monitoring**
```bash
# System logs
tail -f calling_system.log

# Conversation transcripts
tail -f conversation_logs.jsonl

# Check call status
grep "Call initiated" calling_system.log
```

---

## 📁 File Structure

```
ai-call/
├── app.py                      # Main application script
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies (optional)
├── README.md                   # This documentation
├── contacts.csv                # Contact database (auto-created, headers only)
├── dnc_list.txt                # Do Not Call list (auto-created)
├── calling_system.log          # System event logs
├── conversation_logs.jsonl     # Conversation transcripts (JSON Lines)
└── prompts/                    # Sales script directory (auto-created)
    ├── default.txt
    ├── saas_product.txt
    ├── real_estate.txt
    ├── insurance.txt
    └── ecommerce.txt
```

---

## 📊 Data Management

### **Contact Status States**
- **pending**: Ready to be called
- **calling**: Currently being called
- **completed**: Call finished successfully
- **failed**: Call failed due to technical issues
- **opted_out**: Contact requested removal from list

### **Conversation Logs Format**
```json
{
  "call_id": "call_+1234567890_20250101_120000",
  "contact": {
    "phone_number": "+1234567890",
    "name": "John Doe",
    "company": "Tech Corp",
    "prompt_name": "saas_product"
  },
  "duration": 15,
  "opt_out_requested": false,
  "conversation_history": [
    {
      "role": "assistant",
      "content": "Hi John, this is Sarah from ProductivityPro...",
      "timestamp": "2025-01-01T12:00:00"
    },
    {
      "role": "user", 
      "content": "What exactly does your platform do?",
      "timestamp": "2025-01-01T12:00:15"
    }
  ]
}
```

---

## ⚖️ Compliance Features

### **TCPA Compliance**
- **Consent Verification**: Only calls contacts with `consent_obtained=true`
- **AI Disclosure**: Required disclosure at call start
- **Opt-out Processing**: Immediate removal upon request
- **Calling Hours**: Respects business hours (9 AM - 5 PM by default)
- **Call Frequency**: Limits call attempts per contact
- **Record Keeping**: Maintains detailed audit logs

### **Do Not Call (DNC) Management**
- **Internal DNC List**: Maintains `dnc_list.txt` for opt-outs
- **Automatic Updates**: Adds opt-out numbers to DNC list
- **Pre-call Validation**: Checks DNC status before calling
- **Compliance Logging**: Records all DNC interactions

### **Data Privacy**
- **Local Storage**: All data stored locally (no cloud storage)
- **Encryption**: Sensitive data encrypted at rest (user responsibility)
- **Access Control**: Role-based access to system (user responsibility)
- **Audit Trail**: Complete activity logging

---

## 🔧 Customization

### **Adding New Prompts**
1. Create new file: `prompts/your_product.txt`
2. Add your sales script content
3. Update CSV `prompt_name` column
4. System automatically loads new prompts

### **Modifying Existing Prompts**
1. Edit any `.txt` file in `prompts/` directory
2. Changes take effect immediately
3. No system restart required

### **Custom Calling Hours**
```bash
# In .env file
CALLING_HOURS_START=8    # 8 AM
CALLING_HOURS_END=18     # 6 PM
TIMEZONE=US/Pacific      # Pacific timezone
```

### **Concurrency Control**
```bash
# In .env file
MAX_CONCURRENT_CALLS=5   # Max 5 simultaneous calls
```

### **TwiML Handler**
- You must implement a TwiML handler endpoint (e.g., using Flask, Django, or FastAPI) to provide call instructions to Twilio. The system will use a URL like `https://yourapp.com/twiml/{call_id}` when initiating calls. This endpoint should return valid TwiML XML to control the call flow (e.g., play audio, gather input, etc.).
- See [Twilio TwiML Docs](https://www.twilio.com/docs/voice/twiml) for details.

---

## 🐛 Troubleshooting

### **Common Issues**

**"Missing required API keys"**
- Check `.env` file has all required credentials
- Verify Twilio API keys are valid and active
- Ensure environment variables are loaded

**"No callable contacts"**
- Verify contacts have `consent_obtained=true`
- Check contacts aren't opted out
- Confirm calling hours settings

**"Call failed"**
- Check Twilio account balance
- Verify phone number format (+1234567890)
- Test network connectivity
- Review Twilio API status

**"Model errors"**
- Ensure Mistral, Vosk, and Coqui models are downloaded and accessible
- Check system memory and storage

---

## 💰 Cost Estimates

### **Service Costs (Monthly)**
- **Twilio Calling**: ~$0.013 per minute (US, as of 2024; see [Twilio Pricing](https://www.twilio.com/voice/pricing))
- **Local LLM/TTS/STT**: No per-use cost, but requires hardware resources

**Total estimated cost**: Primarily telephony (Twilio) and hardware

### **Scaling Considerations**
- **1,000 calls/month**: ~$100-150
- **10,000 calls/month**: ~$1,000-1,500
- **100,000 calls/month**: ~$10,000-15,000

---

## 🔒 Security Considerations

### **Data Protection**
- Store API keys in environment variables
- Use secure file permissions (600) for configuration files
- Implement access logging and monitoring
- Regular security audits of stored data

### **API Security**
- Rotate API keys regularly
- Use service account keys for Twilio
- Implement rate limiting
- Monitor API usage for anomalies

### **Compliance Security**
- Encrypt conversation logs at rest (user responsibility)
- Implement secure deletion of opted-out data
- Regular compliance audits
- Secure backup procedures

---

## 📈 Performance Optimization

### **System Optimization**
- **Concurrent Calls**: Adjust `MAX_CONCURRENT_CALLS` based on resources
- **Response Time**: Optimize prompt length for faster LLM processing
- **Memory Usage**: Monitor conversation history storage
- **API Limits**: Implement rate limiting for API calls

### **Monitoring Metrics**
- Call success rate
- Conversation duration
- Opt-out rates
- API response times
- System resource usage

---

## 🤝 Contributing

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black app.py
```

### **Code Standards**
- Follow PEP 8 style guide
- Use type hints for function parameters
- Add docstrings for all classes and methods
- Include unit tests for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### **Documentation**
- [Mistral LLM (HuggingFace)](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)
- [Coqui TTS Documentation](https://github.com/coqui-ai/TTS)
- [Vosk Speech Recognition](https://alphacephei.com/vosk/)
- [Twilio API Documentation](https://www.twilio.com/docs/)
- [Twilio TwiML Docs](https://www.twilio.com/docs/voice/twiml)

### **Community**
- GitHub Issues for bug reports
- Discussions for feature requests
- Stack Overflow for technical questions

### **Commercial Support**
Contact [support@yourcompany.com] for enterprise support and customization services.

---

**⚠️ Important**: This system is designed for legitimate business use only. Ensure compliance with all applicable laws and regulations, including TCPA, GDPR, and local privacy laws. Always obtain proper consent before calling prospects and respect opt-out requests immediately.

**🚀 Ready to start?** Follow the installation guide above and begin automating your cold calling process with AI!
