**Intro**

- **Project Title:** SMS AI Chatbot
- **Overview:** A proof of concept (POC) for an AI-powered SMS chatbot designed to answer domain-specific questions, oversee an online schedule, and book events. The chatbot provides an assistant-like experience, facilitating communication between the admin and public users when necessary.

**Scope**

- **Text-Focus:** The system is designed for SMS-based communication, accessible to anyone with a QWERTY-equipped mobile phone.

**Tech & Tools**

- **Backend:** Python & Flask
- **LLM:** OpenAI ChatGPT 3.5 Turbo
- **Vector store:** For domain-specific knowledge
- **SMS:** Twilio
- **Scheduling:** Zoho Booking API

**Components**

- **Zoho Booking API Client**
- **API Integrations:** Twilio, OpenAI, Zoho Booking
- **Potential Database/CMS Integration:** conversation threads, user data

**Plans**

- **Timeline:** 3 months or less
- **Fine-Tuning Prompts:** 1 month
- **Integrations:** 1 month
- **Zoho Client:** 1 month

**Testing**

- **Extensive Self-Testing:** Texting the chatbot in a local environment
  - Twilio account and sms setup
  - ngrok account API & setup
  - run ngrok http --domain [name of the ngrok instance] [PORT]
  - in the directory where [app.py] is located, run [python app.py]
- **Jupyter Notebook Tests:** For code validation
