# 🎭 BANTER - AI Conversation Arena

A fun, interactive application where two AI personalities engage in hilarious debates, discussions, fights, or roasts on any topic. Powered by **FastAPI**, **React**, and **Ollama**.

## 🚀 Features

- **12 Unique Personalities**: From "Ada (AI Researcher)" to "Blaze (Tech Bro)" to "Chaos Agent (5-year-old)"
- **4 Conversation Modes**:
  - ⚖️ **Debate** - Formal arguments with dramatic legal theatrics
  - 💬 **Discuss** - Friendly but passive-aggressive exchanges
  - 🥊 **Fight** - Gloves-off verbal sparring
  - 🔥 **Roast** - Stand-up comedy roast style
- **Custom Personality Upload**: Upload your own `.pdf`, `.txt`, or `.md` files as custom agents
- **Real-Time Streaming**: Watch conversations unfold turn-by-turn
- **Modern Ocean Blue UI**: Sleek dark mode with glassmorphism design
- **Local & Private**: Runs 100% locally using Ollama

## 🛠️ Prerequisites

- **Python 3.9+**
- **Node.js 16+** (for frontend)
- **Ollama**: [Download here](https://ollama.ai)

## 📦 Installation

### 1. Clone & Setup Backend
```bash
git clone https://github.com/shivamtyagi18/Conversation.git
cd Conversation

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Setup Ollama Model
```bash
ollama serve
# In a new terminal
ollama pull mistral
```

## 🏃‍♂️ Running the App

Run Backend and Frontend in **separate terminal windows**:

**Terminal 1: Backend**
```bash
python3 -m uvicorn server:app --reload --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** to start!

## 🎮 How to Use

1. **Select Agent A and Agent B** from the dropdowns
2. **Enter a Topic** (e.g., "Is a hot dog a sandwich?")
3. **Choose a Mode** (Debate, Discuss, Fight, or Roast)
4. Click **Start Conversation**
5. Watch the banter unfold!
6. Click **Stop Conversation** to end, or **Reset Chat** to start fresh

## 🧩 Adding Custom Personalities

Create `.md` files in `data/personalities/` with this format:

```markdown
Character Name (Role)

You are a [Role Name].
TRAITS: [List traits]
[Description of behavior]
Catchphrases: "..."
```

## 📁 Project Structure

```
Conversation/
├── server.py           # FastAPI backend
├── core/
│   └── ollama_client.py  # LLM agent logic
├── data/personalities/   # Agent personality files
└── frontend/
    └── src/
        ├── App.jsx       # React frontend
        └── App.css       # Ocean Blue theme
```

## 📄 License

MIT License
