import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [personalities, setPersonalities] = useState([])
  const [session, setSession] = useState(null)
  const sessionRef = useRef(null)

  // Setup Form State
  const [agentA, setAgentA] = useState('')
  const [agentB, setAgentB] = useState('')
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Upload State
  const [isUploading, setIsUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const fileInputRef = useRef(null)

  // Chat State
  const [messages, setMessages] = useState([])
  const [isDiscussionActive, setIsDiscussionActive] = useState(false)
  const chatEndRef = useRef(null)

  const API_URL = 'http://localhost:8000/api'

  const fetchPersonalities = () => {
    fetch(`${API_URL}/personalities`)
      .then(res => res.json())
      .then(data => {
        setPersonalities(data)
        if (data.length > 0) {
          setAgentA(data[0].name)
          setAgentB(data[1] ? data[1].name : data[0].name)
        }
      })
      .catch(err => console.error("Failed to load personalities", err))
  }

  useEffect(() => {
    fetchPersonalities()
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startConversation = async () => {
    if (!topic) {
      setError("Please enter a topic.")
      return
    }
    setLoading(true)
    setError('')
    setMessages([])

    try {
      const res = await fetch(`${API_URL}/conversation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_a_name: agentA,
          agent_b_name: agentB,
          topic: topic
        })
      })

      if (!res.ok) throw new Error("Failed to start")

      const data = await res.json()
      setSession(data.session_id)
      sessionRef.current = data.session_id
      setMessages([data.initial_turn])
      setIsDiscussionActive(true)

      // Start polling for next turns
      processNextTurn(data.session_id)

    } catch (e) {
      setError(e.message)
      setLoading(false)
    }
  }

  const processNextTurn = async (sessionId) => {
    // Check if stopped
    if (sessionId !== sessionRef.current) return

    try {
      const res = await fetch(`${API_URL}/conversation/next?session_id=${sessionId}`, {
        method: 'POST'
      })

      if (sessionId !== sessionRef.current) return

      if (!res.ok) {
        setIsDiscussionActive(false)
        setLoading(false)
        return
      }

      const data = await res.json()

      if (data.status === 'done') {
        setIsDiscussionActive(false)
        setLoading(false)
        return
      }

      setMessages(prev => [...prev, data])

      setTimeout(() => {
        processNextTurn(sessionId)
      }, 2000)

    } catch (e) {
      console.error(e)
      setLoading(false)
    }
  }

  const stopConversation = () => {
    sessionRef.current = null
    setIsDiscussionActive(false)
    setLoading(false)
  }

  const resetConversation = () => {
    stopConversation()
    setSession(null)
    setMessages([])
    if (session) {
      fetch(`${API_URL}/conversation/reset?session_id=${session}`, { method: 'POST' })
    }
  }

  const handleFileUpload = async (event, forAgent) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setUploadStatus('Analyzing profile...')
    setError('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_URL}/personalities/upload`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }

      const data = await res.json()
      setUploadStatus(`Created: ${data.name}`)

      // Refresh personalities and auto-select the new one
      const newList = await fetch(`${API_URL}/personalities`).then(r => r.json())
      setPersonalities(newList)

      if (forAgent === 'A') {
        setAgentA(data.name)
      } else if (forAgent === 'B') {
        setAgentB(data.name)
      }

      setTimeout(() => setUploadStatus(''), 5000)
    } catch (e) {
      setError(e.message)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="container">
      <header>
        <h1>🤖 Dual-Agent Arena 🤖</h1>
      </header>

      <main>
        {/* Sidebar / Config */}
        <div className="sidebar">
          <div className="card">
            <h2>Configuration</h2>

            <label>Agent A</label>
            <select value={agentA} onChange={e => setAgentA(e.target.value)} disabled={isDiscussionActive}>
              {personalities.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
              <option value="__custom__">➕ Upload Custom...</option>
            </select>
            {agentA === '__custom__' && (
              <div style={{ marginTop: '10px' }}>
                <input
                  type="file"
                  accept=".pdf,.txt,.md"
                  onChange={(e) => handleFileUpload(e, 'A')}
                  disabled={isUploading}
                />
                {isUploading && <span style={{ marginLeft: '10px', color: '#a29bfe' }}>Analyzing...</span>}
              </div>
            )}

            <label>Agent B</label>
            <select value={agentB} onChange={e => setAgentB(e.target.value)} disabled={isDiscussionActive}>
              {personalities.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
              <option value="__custom__">➕ Upload Custom...</option>
            </select>
            {agentB === '__custom__' && (
              <div style={{ marginTop: '10px' }}>
                <input
                  type="file"
                  accept=".pdf,.txt,.md"
                  onChange={(e) => handleFileUpload(e, 'B')}
                  disabled={isUploading}
                />
                {isUploading && <span style={{ marginLeft: '10px', color: '#a29bfe' }}>Analyzing...</span>}
              </div>
            )}

            <label>Topic</label>
            <textarea
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="e.g. Is a hot dog a sandwich?"
              disabled={isDiscussionActive}
            />

            {error && <div className="error">{error}</div>}

            {!isDiscussionActive ? (
              <button
                className="btn-primary"
                onClick={startConversation}
                disabled={loading}
              >
                {loading ? "Initializing..." : "Start Debate"}
              </button>
            ) : (
              <button
                className="btn-secondary"
                onClick={stopConversation}
                style={{ background: '#ff9f43' }}
              >
                Stop Debate
              </button>
            )}

            {messages.length > 0 && !isDiscussionActive && (
              <button className="btn-secondary" onClick={resetConversation} style={{ marginTop: '10px' }}>
                Reset Chat
              </button>
            )}

            {uploadStatus && <div style={{ marginTop: '15px', color: '#8effc1', fontSize: '0.85rem', padding: '10px', background: 'rgba(0,242,96,0.1)', borderRadius: '8px' }}>{uploadStatus}</div>}
          </div>
        </div>

        {/* Chat Area */}
        <div className="chat-window">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Select agents and a topic to begin the conversation.</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.speaker === agentA ? 'left' : 'right'}`}>
              <div className="avatar">{msg.speaker[0]}</div>
              <div className="content">
                <div className="name">{msg.speaker}</div>
                <div className="text">{msg.message}</div>
              </div>
            </div>
          ))}
          {isDiscussionActive && <div className="typing-indicator">Agents are typing...</div>}
          <div ref={chatEndRef} />
        </div>
      </main>
    </div>
  )
}

export default App
