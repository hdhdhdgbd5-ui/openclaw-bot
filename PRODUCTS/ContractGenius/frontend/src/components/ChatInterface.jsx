import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { chatWithContract } from '../utils/api'

const ChatInterface = ({ contractId }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I've analyzed your contract and I'm ready to answer any questions you have. What would you like to know about this agreement?"
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const history = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await chatWithContract(contractId, userMessage, history)
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.response }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I apologize, but I encountered an error processing your question. Please try again.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const getSuggestedQuestions = () => [
    "What are my main obligations?",
    "What happens if I breach the contract?",
    "Can I terminate this agreement early?",
    "Are there any hidden costs?",
    "What are my rights under this contract?",
  ]

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 bg-primary-50 rounded-t-xl">
        <div className="flex items-center space-x-2">
          <div className="bg-primary-600 p-2 rounded-lg">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Contract Assistant</h3>
            <p className="text-sm text-gray-500">Ask me anything about your contract</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex items-start space-x-2 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`p-2 rounded-lg ${
              message.role === 'user' 
                ? 'bg-primary-600' 
                : 'bg-gray-100'
            }`}>
              {message.role === 'user' ? (
                <User className="h-4 w-4 text-white" />
              ) : (
                <Bot className="h-4 w-4 text-gray-600" />
              )}
            </div>
            
            <div className={`max-w-[80%] p-3 rounded-lg ${
              message.role === 'user'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-800'
            }`}>
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-center space-x-2">
            <div className="bg-gray-100 p-2 rounded-lg">
              <Bot className="h-4 w-4 text-gray-600" />
            </div>
            <div className="bg-gray-100 p-3 rounded-lg flex items-center space-x-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm text-gray-600">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className="px-4 py-2 border-t border-gray-100">
          <p className="text-xs text-gray-500 mb-2">Suggested questions:</p>
          <div className="flex flex-wrap gap-2">
            {getSuggestedQuestions().map((question, index) => (
              <button
                key={index}
                onClick={() => {
                  setInput(question)
                }}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-xs text-gray-700 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your contract..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  )
}

export default ChatInterface