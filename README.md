# 🤖 AI-Powered Cold Calling System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Google AI](https://img.shields.io/badge/Google%20AI-Gemini-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A sophisticated AI-powered cold calling system that automates phone outreach using Google AI's Gemini for intelligent conversations, Google Cloud Speech services for voice processing, and Plivo for telephony. The system manages contacts via CSV files, uses customizable prompt-based sales scripts, and includes built-in TCPA compliance features.

---

## 🎯 What This System Does

### **Core Functionality**
- **Automated Cold Calling**: Dials prospects from a CSV database during business hours
- **AI-Powered Conversations**: Uses Google's Gemini LLM to conduct natural, contextual sales conversations
- **Voice Processing**: Converts speech to text and text to speech for real-time voice interactions
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
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CSV Database  │    │  Prompt Files   │    │   Google AI     │
│   (contacts.csv)│    │  (prompts/*.txt)│    │   (Gemini LLM)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Call System   │
                    │  (Main Script)  │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Google Speech  │    │  Plivo Calling  │    │  Compliance     │
│  (STT/TTS)      │    │  (Telephony)    │    │  (TCPA/DNC)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Call Flow Process**

1. **Contact Selection**: System reads `contacts.csv` and selects callable prospects
2. **Compliance Check**: Validates consent, calling hours, and DNC status
3. **Prompt Loading**: Loads appropriate sales script from `prompts/[prompt_name].txt`
4. **Call Initiation**: Plivo API dials the prospect's phone number
5. **Voice Processing**: Google Speech-to-Text captures prospect responses
6. **AI Processing**: Gemini LLM generates contextual responses based on conversation history
7. **Voice Synthesis**: Google Text-to-Speech converts AI responses to voice
8. **Conversation Management**: Tracks conversation state and detects opt-out requests
9. **Call Completion**: Logs conversation transcript and updates contact status
10. **Compliance Handling**: Processes opt-out requests and updates DNC lists

### **Data Flow**

```
CSV Contact → Compliance Check → Prompt Selection → Call Initiation
     ↓
Voice Input → Speech-to-Text → LLM Processing → Response Generation
     ↓
Text-to-Speech → Voice Output → Conversation Continue/End
     ↓
Conversation Log → Contact Update → Compliance Update
```

---

## 🔧 System Components & Responsibilities

### **1. Main Application (`CallSystem` class)**
**Responsibility**: Orchestrates the entire calling process
- **Contact Management**: Loads, validates, and updates contact records
- **Session Management**: Runs calling sessions with concurrency control
- **Compliance Enforcement**: Checks calling hours, consent, and DNC lists
- **Logging**: Maintains system logs and conversation transcripts
- **Configuration**: Manages system settings and API credentials

### **2. AI Conversation Manager (`AIConversationManager` class)**
**Responsibility**: Handles AI-powered conversations
- **Prompt Management**: Loads and manages sales scripts from text files
- **Conversation State**: Tracks conversation history and context
- **LLM Integration**: Interfaces with Google's Gemini for response generation
- **Voice Processing**: Manages speech-to-text and text-to-speech operations
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

#### **Google AI (Gemini)**
**Responsibility**: Provides conversational intelligence
- **Natural Language Processing**: Understands prospect responses
- **Context Awareness**: Maintains conversation history
- **Response Generation**: Creates human-like responses
- **Objection Handling**: Processes and responds to sales objections
- **Personalization**: Adapts responses based on prospect information

#### **Google Cloud Speech**
**Responsibility**: Handles voice processing
- **Speech-to-Text**: Converts prospect voice to text for LLM processing
- **Text-to-Speech**: Converts AI responses to natural voice output
- **Audio Quality**: Ensures clear, professional voice synthesis
- **Language Support**: Handles multiple languages and accents

#### **Plivo Telephony**
**Responsibility**: Manages phone call operations
- **Call Routing**: Dials prospect phone numbers
- **Call Control**: Manages call duration and termination
- **Webhook Integration**: Handles call events and status updates
- **Quality Assurance**: Ensures reliable call delivery

---

## 📋 Prerequisites

### **Required Services**
- **Google AI API**: For Gemini LLM conversations
- **Google Cloud Project**: For Speech-to-Text and Text-to-Speech
- **Plivo Account**: For phone calling capabilities
- **Python 3.8+**: Runtime environment

### **System Requirements**
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 1GB free space for logs and data
- **Network**: Stable internet connection for API calls
- **OS**: Linux, macOS, or Windows

---

## 🚀 Installation & Setup

### **1. Clone and Install**
```bash
# Clone the repository
git clone <repository-url>
cd ai-cold-calling-system

# Install dependencies
pip install google-generativeai google-cloud-speech google-cloud-texttospeech httpx pytz python-dotenv

# Or use requirements.txt
pip install -r requirements.txt
```

### **2. API Configuration**

#### **Google AI Setup**
```bash
# Get API key from https://makersuite.google.com/app/apikey
export GOOGLE_AI_KEY="your_google_ai_api_key"
```

#### **Google Cloud Setup**
```bash
# Create project at https://console.cloud.google.com/
# Enable Speech-to-Text and Text-to-Speech APIs
# Create service account and download JSON key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

#### **Plivo Setup**
```bash
# Get credentials from https://console.plivo.com/accounts/credentials/
# Purchase phone number from Plivo dashboard
export PLIVO_AUTH_ID="your_plivo_auth_id"
export PLIVO_AUTH_TOKEN="your_plivo_auth_token"
export PLIVO_PHONE_NUMBER="+1234567890"
```

### **3. Configuration File**

Create `.env` file in project root:

```bash
# Google AI Configuration
GOOGLE_AI_KEY=your_google_ai_api_key_here
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id

# Plivo Configuration
PLIVO_AUTH_ID=your_plivo_auth_id
PLIVO_AUTH_TOKEN=your_plivo_auth_token  
PLIVO_PHONE_NUMBER=+1234567890

# System Configuration
CSV_FILE_PATH=contacts.csv
PROMPTS_DIR=prompts
MAX_CONCURRENT_CALLS=3
CALLING_HOURS_START=9
CALLING_HOURS_END=17
TIMEZONE=US/Eastern
CONVERSATION_TIMEOUT=120
```

### **4. Contact Database Setup**

The system auto-creates `contacts.csv` with sample data. Format:

```csv
phone_number,name,email,company,status,call_attempts,consent_obtained,opt_out_date,prompt_name
+1234567890,John Doe,john@techcorp.com,Tech Corp,pending,0,true,,saas_product
+1234567891,Jane Smith,jane@realty.com,Smith Realty,pending,0,true,,real_estate
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

### **5. Prompt Configuration**

The system auto-creates prompt files in `prompts/` directory:

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

**Example Prompt (`prompts/saas_product.txt`):**
```
Hi {name}, this is {agent_name} from ProductivityPro. Just a heads up, this call uses AI technology to help answer your questions. You can say "stop" at any time to end the call.

I noticed {company} might benefit from our platform that helps teams work smarter. I’d love to learn about your needs and see if we can help.

Here’s what we offer:
- Save 2-3 hours per employee per day (based on real customer feedback)
- Works with tools you already use
- Most companies see results in about a month
- Trusted by thousands of businesses

Can I ask a few quick questions to understand your situation?
- What’s your biggest productivity challenge?
- How many people are on your team?
- What tools do you use now?
- Who usually decides on new software at your company?

If you have any questions or concerns, just let me know. If I don’t know the answer, I’ll connect you with a human rep.

If you’d like to end the call or be removed from our list, just say "stop" and I’ll do that right away.

Would you be open to a quick 10-minute demo this week? If now isn’t a good time, just let me know what works for you.

PROSPECT INFO:
- Name: {name}
- Company: {company}
- Email: {email}
- Phone: {phone_number}

Let me know if you want to continue or have any questions!
```

---

## 🎮 Usage

### **Start the System**
```bash
python ai_cold_calling.py
```

### **System Output**
```
🤖 AI-Powered Cold Calling System
==================================================
Starting LLM-Powered Cold Calling System
Created default prompt file: prompts/default.txt
Created default prompt file: prompts/saas_product.txt
Loaded prompt: default
Loaded prompt: saas_product
Available prompts (5): default, saas_product, real_estate, insurance, ecommerce
Prompt files location: /path/to/prompts
To add new prompts: create new .txt files in the prompts directory
Calling 3 contacts
Call initiated: +1234567890 -> call_uuid_123 (Prompt: saas_product)
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
ai-cold-calling-system/
├── ai_cold_calling.py           # Main application script
├── .env                         # Environment configuration
├── requirements.txt             # Python dependencies
├── README.md                   # This documentation
├── contacts.csv                # Contact database (auto-created)
├── dnc_list.txt               # Do Not Call list (auto-created)
├── calling_system.log         # System event logs
├── conversation_logs.jsonl    # Conversation transcripts (JSON Lines)
└── prompts/                   # Sales script directory (auto-created)
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
- **Encryption**: Sensitive data encrypted at rest
- **Access Control**: Role-based access to system
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

---

## 🐛 Troubleshooting

### **Common Issues**

**"Missing required API keys"**
- Check `.env` file has all required credentials
- Verify API keys are valid and active
- Ensure environment variables are loaded

**"No callable contacts"**
- Verify contacts have `consent_obtained=true`
- Check contacts aren't opted out
- Confirm calling hours settings

**"Call failed"**
- Check Plivo account balance
- Verify phone number format (+1234567890)
- Test network connectivity
- Review Plivo API status

**"Google AI errors"**
- Validate Google AI API key
- Check API quota limits
- Verify Google Cloud project configuration

**"Speech service errors"**
- Confirm Google Cloud credentials
- Enable required APIs in Google Cloud Console
- Check service account permissions

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python ai_cold_calling.py
```

### **Test Configuration**
```bash
# Test API connections
python -c "
import google.generativeai as genai
genai.configure(api_key='your_key')
print('Google AI: OK')

from google.cloud import speech
client = speech.SpeechClient()
print('Google Speech: OK')

import plivo
client = plivo.RestClient('auth_id', 'auth_token')
print('Plivo: OK')
"
```

---

## 💰 Cost Estimates

### **Service Costs (Monthly)**
- **Google AI (Gemini)**: ~$0.002 per 1K tokens (~$20 for 10K conversations)
- **Google Speech-to-Text**: ~$0.024 per minute (~$240 for 10K minutes)  
- **Google Text-to-Speech**: ~$0.016 per 1K characters (~$160 for 10K responses)
- **Plivo Calling**: ~$0.0055 per minute (~$55 for 10K minutes)

**Total estimated cost**: ~$0.05 per minute of conversation

### **Scaling Considerations**
- **1,000 calls/month**: ~$50-75
- **10,000 calls/month**: ~$500-750
- **100,000 calls/month**: ~$5,000-7,500

---

## 🔒 Security Considerations

### **Data Protection**
- Store API keys in environment variables
- Use secure file permissions (600) for configuration files
- Implement access logging and monitoring
- Regular security audits of stored data

### **API Security**
- Rotate API keys regularly
- Use service account keys for Google Cloud
- Implement rate limiting
- Monitor API usage for anomalies

### **Compliance Security**
- Encrypt conversation logs at rest
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
black ai_cold_calling.py
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
- [Google AI Documentation](https://ai.google.dev/docs)
- [Google Cloud Speech Documentation](https://cloud.google.com/speech-to-text/docs)
- [Plivo API Documentation](https://www.plivo.com/docs/)

### **Community**
- GitHub Issues for bug reports
- Discussions for feature requests
- Stack Overflow for technical questions

### **Commercial Support**
Contact [support@yourcompany.com] for enterprise support and customization services.

---

**⚠️ Important**: This system is designed for legitimate business use only. Ensure compliance with all applicable laws and regulations, including TCPA, GDPR, and local privacy laws. Always obtain proper consent before calling prospects and respect opt-out requests immediately.

**🚀 Ready to start?** Follow the installation guide above and begin automating your cold calling process with AI!
