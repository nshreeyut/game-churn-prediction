/**
 * useChat — Custom React Hook
 * ============================
 * Manages all state for the chat conversation.
 *
 * WHY SEPARATE THIS FROM THE COMPONENT?
 * ---------------------------------------
 * ChatPanel's job: render the UI (message bubbles, input box, send button)
 * useChat's job:   manage the data (message history, streaming state, API calls)
 *
 * Separating them makes both easier to read, test, and maintain.
 * If you want to redesign the chat UI, you only touch ChatPanel.
 * If you want to change how messages are sent, you only touch this hook.
 *
 * STREAMING STATE EXPLAINED:
 * ---------------------------
 * There are two pieces of state for the LLM's response:
 *
 *   messages         → the COMPLETED conversation history
 *                      [{role: "user", content: "..."}, {role: "assistant", content: "..."}]
 *
 *   streamingMessage → the CURRENT partial response being typed out in real-time
 *                      This is a temporary string that grows as chunks arrive.
 *                      When streaming finishes, it gets added to messages and reset to "".
 *
 * The UI renders `messages` as the history, plus `streamingMessage` as a
 * live "currently typing" bubble at the bottom.
 *
 * @param {object|null} playerContext - the current player's full data object
 *                                     passed to the API so the LLM has context
 *
 * TODO: Implement this hook.
 * Steps:
 *   1. const [messages, setMessages] = useState([])
 *      const [streamingMessage, setStreamingMessage] = useState('')
 *      const [loading, setLoading] = useState(false)
 *
 *   2. Write sendMessage(text):
 *        a. Add user message: setMessages(prev => [...prev, { role: 'user', content: text }])
 *        b. setLoading(true), setStreamingMessage('')
 *        c. Call streamChat({
 *             message: text,
 *             playerContext,
 *             conversationHistory: messages,
 *             onChunk: (chunk) => setStreamingMessage(prev => prev + chunk),
 *             onDone: () => {
 *               // Move the completed stream into the messages array
 *               setMessages(prev => [...prev, { role: 'assistant', content: streamingMessage_final }])
 *               setStreamingMessage('')
 *               setLoading(false)
 *             },
 *             onError: (err) => { setLoading(false) }
 *           })
 *
 *   NOTE: There's a subtle challenge here — the onDone callback captures `streamingMessage`
 *   from a closure, but state updates are async. One clean solution:
 *   Use a useRef to track the accumulated stream text alongside the state.
 *   const streamRef = useRef('')
 *   In onChunk: streamRef.current += chunk; setStreamingMessage(streamRef.current)
 *   In onDone:  setMessages(prev => [...prev, { role: 'assistant', content: streamRef.current }])
 *               streamRef.current = ''; setStreamingMessage('')
 *
 * LEARN MORE: https://react.dev/reference/react/useRef
 */

import { useState, useRef } from 'react'
import { streamChat } from '../api/chat'

export function useChat(playerContext = null) {
  const [messages, setMessages] = useState([])
  const [streamingMessage, setStreamingMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const streamRef = useRef('')  // tracks accumulated stream text (see note above)

  // TODO: implement sendMessage

  return {
    messages,
    streamingMessage,
    loading,
    sendMessage: () => {},  // TODO: replace with real implementation
  }
}
