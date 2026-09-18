# 🤖 ResolveAI

## Agentic Customer Complaint Resolution System

ResolveAI is an AI-powered customer complaint resolution system designed to automate customer support workflows using **LLM-based reasoning, Retrieval-Augmented Generation (RAG), and business tools**.

The system understands customer complaints, identifies the issue, retrieves relevant company policies, checks business/order information, makes a resolution decision, and generates both a customer-facing response and an internal support note.

---

## 🌐 Live Demo

🚀 **Live Application:**  
https://resolve-ai-8uij67guf3kigrdcfpuhcr.streamlit.app/

---

## ✨ Features

### 🤖 AI Complaint Triage

Automatically analyzes customer complaints and extracts:

- **Complaint Category**
- **Customer Intent**
- **Sentiment**
- **Priority**
- **Complaint Summary**

### 📚 RAG-Based Policy Retrieval

ResolveAI retrieves relevant information from the company knowledge base based on the customer's complaint.

The current knowledge base includes:

- Refund Policy
- Shipping Policy
- Warranty Policy
- Customer Support Policy

### 🔍 Business Data Lookup

The system uses mock business data to retrieve relevant order information such as:

- Order ID
- Product
- Order Value
- Order Status
- Customer Information

### 🧠 AI-Powered Decision Making

The decision agent combines the customer complaint, retrieved policies, and business data to determine an appropriate resolution.

```text
Customer Complaint
        +
Retrieved Policies
        +
Business Data
        ↓
AI Decision Agent
        ↓
Resolution Decision
```

### 💬 Automated Response Generation

ResolveAI generates two types of responses.

#### Customer Response

- Clear
- Professional
- Context-aware

#### Internal Support Note

- Resolution decision
- Relevant context
- Suggested follow-up action

### ⚡ Agentic Resolution Pipeline

The system follows a multi-step workflow where each stage contributes information to the next stage.

```text
Triage → RAG → Business Tools → Decision → Resolution
```

---

## 🏗️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core application logic |
| **Streamlit** | Web application and user interface |
| **Google Gemini** | LLM-powered analysis and decision making |
| **RAG** | Retrieval of relevant company policies |
| **HTML** | UI structure |
| **CSS** | Custom styling and responsive interface |
| **Git** | Version control |
| **GitHub** | Source code repository |
| **Streamlit Community Cloud** | Application deployment |

---

## 📂 Project Structure

```text
Resolve-AI/
│
├── app.py
│   └── Main Streamlit application
│
├── knowledge_base.py
│   └── Company policies and RAG retrieval logic
│
├── style.css
│   └── Custom application styling
│
├── requirements.txt
│   └── Python dependencies
│
├── .gitignore
│   └── Files excluded from version control
│
└── .streamlit/
    └── secrets.toml
        └── Local API key configuration
```

> `.streamlit/secrets.toml` is excluded from GitHub using `.gitignore` to protect the Gemini API key.

---

## 🔄 How It Works

### Step 1 — Customer Complaint

The user enters a customer complaint into the ResolveAI interface.

### Step 2 — AI Triage

The Gemini LLM analyzes the complaint and identifies important information such as:

- Category
- Intent
- Sentiment
- Priority
- Summary

### Step 3 — Policy Retrieval

The system searches the knowledge base for policies relevant to the complaint.

For example, a delayed delivery complaint can retrieve the **Shipping Policy**.

### Step 4 — Business Data Lookup

The system checks mock business/order data to understand the customer's specific situation.

### Step 5 — AI Decision Agent

The decision agent combines:

```text
Complaint
+
AI Triage Results
+
Retrieved Policies
+
Business Data
```

and determines an appropriate resolution.

### Step 6 — Response Generation

Finally, ResolveAI generates:

1. A customer-facing response
2. An internal support note

This creates an end-to-end automated complaint resolution workflow.

---

## 🧪 Example

### Customer Complaint

> My order was supposed to arrive three days ago but I still haven't received it.

### AI Analysis

| Field | Result |
|-------|--------|
| **Category** | Shipping |
| **Intent** | Delayed Delivery |

### Resolution Flow

```text
Customer Complaint
        ↓
Shipping Issue Detected
        ↓
Shipping Policy Retrieved
        ↓
Order Information Checked
        ↓
AI Resolution Decision
        ↓
Customer Response Generated
```

---

## 🚀 Deployment

ResolveAI is deployed using **Streamlit Community Cloud**.

### Live Application

👉 https://resolve-ai-8uij67guf3kigrdcfpuhcr.streamlit.app/

The application is connected to the GitHub repository and can be deployed directly from the `main` branch.

### Environment Configuration

The Gemini API key is stored securely using Streamlit Secrets.

```text
.streamlit/secrets.toml
```

Example:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

> ⚠️ **Never commit API keys or other sensitive credentials to GitHub.**

---

## 🔮 Future Improvements

The project can be extended with:

- Integration with a real customer database
- Vector database for scalable RAG
- Real-time order management APIs
- Automated refund processing
- Human-in-the-loop approval
- Customer authentication
- Conversation history
- Customer support analytics dashboard
- Multi-agent orchestration
- CRM and helpdesk integration
- Real-time customer notifications
- Advanced semantic search
- Persistent customer profiles

---

## 🎯 Project Goal

The goal of **ResolveAI** is to demonstrate how modern AI technologies can be combined to solve a practical business problem.

The project brings together:

```text
LLM
+
RAG
+
Business Tools
+
Agentic Decision Making
+
Automated Response Generation
```

to create an intelligent customer complaint resolution workflow that can reduce manual support effort and provide consistent, policy-aware responses.

---

## 🔐 Security

ResolveAI uses **Streamlit Secrets** to store the Gemini API key.

The secrets file is intentionally excluded from version control:

```text
.streamlit/secrets.toml
```

The API key is therefore not included in the public GitHub repository.

---

## 👩‍💻 Author

**Ananya Rishi**

B.Tech in Computer Science & Engineering  
Specialization: Artificial Intelligence & Machine Learning

---

## ⭐ Project

**ResolveAI — Agentic Customer Complaint Resolution System**

🚀 **Live Demo:**  
https://resolve-ai-8uij67guf3kigrdcfpuhcr.streamlit.app/
