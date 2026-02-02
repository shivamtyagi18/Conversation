# Duel Agents: AI Conversation Arena

A fun, interactive application where two AI personalities debate, discuss, or argue about a topic of your choice. Powered by **FastAPI**, **React**, and **Ollama**.

## 🚀 Features
- **10+ Unique Personalities**: From a "Grumpy Sysadmin" to a "Chaos Agent (5-year-old)".
- **Real-Time Streaming**: Watch the conversation unfold turn-by-turn.
- **Modern UI**: Dark mode, avatar-based chat interface.
- **Local Privacy**: Runs 100% locally using Ollama.

## 🛠️ Prerequisites
- **Python 3.9+**
- **Node.js 16+** (for frontend)
- **Ollama**: [Download here](https://ollama.ai)

## 📦 Installation

### 1. Clone & Setup Backend
```bash
# Clone repository
git clone <your-repo-url>
cd Conversation

# It is recommended to create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Setup Ollama Model
Ensure Ollama is installed and running, then pull the model (default is `mistral`):
```bash
ollama serve
# In a new terminal
ollama pull mistral
```

## 🏃‍♂️ Running the App

You need to run the Backend and Frontend in **separate terminal windows**.

**Terminal 1: Backend**
```bash
# From project root
python3 -m uvicorn server:app --reload --port 8000
```

**Terminal 2: Frontend**
```bash
# From project root
cd frontend
npm run dev
```

Open the link shown in the Frontend terminal (usually **http://localhost:5173**) to start!

## 🎮 How to Use
1.  **Select Agent A and Agent B** from the dropdowns (e.g., *Product Manager* vs *Software Engineer*).
2.  **Enter a Topic** (e.g., "Why is Jira so slow?").
3.  Click **Start Debate**.
4.  To end the chat, click **Stop / Reset**.

## 🧩 Customization
Add new personalities by creating `.md` files in `data/personalities/`.
Format:
```markdown
You are a [Role Name].
TRAITS: [List traits]
[Description of behavior]
Catchphrases: "..."
```
