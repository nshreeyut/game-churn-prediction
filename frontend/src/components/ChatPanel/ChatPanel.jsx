/**
 * ChatPanel Component
 * ====================
 * The AI analyst chatbot interface. Lives in the right column of the home page.
 * Pre-loaded with the current player's context so the LLM knows who you're asking about.
 *
 * PROPS:
 *   playerContext — the full player data object (or null if no player is selected)
 *                  passed to useChat() → sent to the API → given to the LangChain agent
 *
 * WHAT TO RENDER:
 *
 * 1. CHAT HEADER
 *    Title: "AI Analyst"
 *    If playerContext is set, show: "Analyzing: {player_id} on {platform}"
 *
 * 2. MESSAGE LIST (scrollable)
 *    Map over messages from useChat():
 *      - User messages:     right-aligned, different background
 *      - Assistant messages: left-aligned, with a small AI icon or label
 *    Show streamingMessage as a live "typing" bubble at the bottom when loading=true
 *    Auto-scroll to bottom when new messages arrive (useEffect + useRef on the list div)
 *
 * 3. SUGGESTED QUESTIONS (show when chat is empty)
 *    To help users get started, show clickable example questions:
 *      - "Why is this player predicted to churn?"
 *      - "What does engagement score mean?"
 *      - "How can we retain this player?"
 *      - "What's the overall churn rate in the dataset?"
 *    Clicking one fills the input and sends it.
 *
 * 4. INPUT BAR
 *    - A text <input> for typing a message
 *    - A Send button (disabled while loading=true)
 *    - Submit on Enter key OR button click
 *
 * AUTO-SCROLL TRICK:
 * ------------------
 * To scroll to the bottom when messages update:
 *   const bottomRef = useRef(null)
 *   useEffect(() => {
 *     bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
 *   }, [messages, streamingMessage])
 *   // At the bottom of your message list: <div ref={bottomRef} />
 *
 * TODO: Implement this component.
 * The useChat hook gives you everything you need:
 *   const { messages, streamingMessage, loading, sendMessage } = useChat(playerContext)
 */

import { useState, useEffect, useRef } from 'react'
import { useChat } from '../../hooks/useChat'
import './ChatPanel.css'

// Suggested starter questions shown when the chat is empty
const SUGGESTED_QUESTIONS = [
  "Why is this player predicted to churn?",
  "What does the engagement score mean?",
  "How can we retain this player?",
  "What's the overall churn rate in the dataset?",
]

function ChatPanel({ playerContext }) {
  const { messages, streamingMessage, loading, sendMessage } = useChat(playerContext)
  const [inputText, setInputText] = useState('')
  const bottomRef = useRef(null)

  // Auto-scroll to bottom when messages or streaming content changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingMessage])

  function handleSubmit(e) {
    e.preventDefault()
    if (!inputText.trim() || loading) return
    sendMessage(inputText.trim())
    setInputText('')
  }

  return (
    <div className="chat-panel">
      {/* Header */}
      <div className="chat-header">
        <h2>AI Analyst</h2>
        {playerContext && (
          <span className="chat-context-label">
            {/* TODO: Show "Analyzing: {playerContext.player_id} on {playerContext.platform}" */}
          </span>
        )}
      </div>

      {/* Message list */}
      <div className="chat-messages">
        {/*
          TODO: Render message history.
          Each message has: { role: 'user' | 'assistant', content: '...' }
          Apply different CSS classes for user vs assistant.
        */}

        {/* Suggested questions (shown when no messages yet) */}
        {messages.length === 0 && !loading && (
          <div className="suggested-questions">
            <p className="suggested-label">Try asking:</p>
            {SUGGESTED_QUESTIONS.map((q) => (
              <button
                key={q}
                className="suggestion-btn"
                onClick={() => {
                  setInputText(q)
                  // TODO: optionally auto-send: sendMessage(q)
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}

        {/*
          TODO: Render the live streaming message bubble when streamingMessage is non-empty.
          Show a pulsing cursor or "typing..." indicator when loading=true but streamingMessage is empty.
        */}

        {/* Anchor div for auto-scrolling */}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form className="chat-input-bar" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask about this player or the dataset…"
          disabled={loading}
          className="chat-input"
        />
        <button type="submit" disabled={loading || !inputText.trim()} className="chat-send-btn">
          {loading ? '…' : 'Send'}
        </button>
      </form>
    </div>
  )
}

export default ChatPanel
