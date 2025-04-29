'use client'

import { Paperclip, Mic, Send } from 'lucide-react'
import { useState, useEffect } from 'react'
import * as Babel from '@babel/standalone'
import React from 'react'
import { queryText2Sql, QueryResponse } from '../../services/api'

interface Message {
  id: string
  text: string
  timestamp: string
  isUser: boolean
  showDynamicComponent?: boolean
  sqlResponse?: QueryResponse
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [DynamicComponent, setDynamicComponent] = useState<React.FC | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      timestamp: new Date().toLocaleTimeString('de-DE', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }),
      isUser: true,
    }

    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      // Try to process as SQL query first
      const sqlResponse = await queryText2Sql({ question: inputValue })
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Hier ist das Ergebnis deiner Anfrage:',
        timestamp: new Date().toLocaleTimeString('de-DE', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }),
        isUser: false,
        sqlResponse
      }
      setMessages(prev => [...prev, botResponse])
    } catch (err) {
      // If SQL query fails, try revenue visualization
      const isRevenueQuery =
        inputValue.toLowerCase().includes('umsatz') ||
        inputValue.toLowerCase().includes('revenue') ||
        inputValue.toLowerCase().includes('entwicklung')

      if (isRevenueQuery) {
        fetch(`http://localhost:8000/api/generated-code?query=${encodeURIComponent(inputValue)}`)
          .then(res => res.json())
          .then(({ code }) => {
            console.log('Fetched code:', code);
            const transpiled = Babel.transform(code, {
              presets: [Babel.availablePresets['react']],
              filename: 'dynamic.js',
              configFile: false,
              babelrc: false
            }).code
            console.log('Transpiled code:', transpiled);

            const moduleCode = `
              const React = arguments[0];
              const exports = {};
              ${transpiled}
              return exports.default;
            `
            try {
              const executeCode = new Function(moduleCode)
              const Component = executeCode(React)

              if (typeof Component !== 'function') {
                throw new Error('Generated code did not return a valid React component')
              }

              setDynamicComponent(() => Component)

              const botResponse: Message = {
                id: (Date.now() + 1).toString(),
                text: 'Hier ist die angeforderte Umsatzentwicklung:',
                timestamp: new Date().toLocaleTimeString('de-DE', {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                }),
                isUser: false,
                showDynamicComponent: true,
              }

              setMessages(prev => [...prev, botResponse])
            } catch (error) {
              console.error('Error executing code:', error);
              const errorResponse: Message = {
                id: (Date.now() + 1).toString(),
                text: 'Entschuldigung, ich konnte deine Anfrage nicht verarbeiten.',
                timestamp: new Date().toLocaleTimeString('de-DE', {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                }),
                isUser: false,
              }
              setMessages(prev => [...prev, errorResponse])
            }
          })
          .catch(err => {
            console.error('Error fetching or transpiling code:', err)
            const errorResponse: Message = {
              id: (Date.now() + 1).toString(),
              text: 'Entschuldigung, es gab einen Fehler bei der Verarbeitung deiner Anfrage.',
              timestamp: new Date().toLocaleTimeString('de-DE', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
              }),
              isUser: false,
            }
            setMessages(prev => [...prev, errorResponse])
          })
      } else {
        const errorResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: 'Entschuldigung, ich konnte deine Anfrage nicht verarbeiten.',
          timestamp: new Date().toLocaleTimeString('de-DE', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          }),
          isUser: false,
        }
        setMessages(prev => [...prev, errorResponse])
      }
    } finally {
      setLoading(false)
      setInputValue('')
    }
  }

  const renderSqlResponse = (response: QueryResponse) => {
    if (!response || !response.result) return null;

    return (
      <div className="space-y-4">
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-300">Generated SQL:</h4>
          <pre className="p-3 bg-[#1a1f2e] rounded-md text-gray-300 text-sm overflow-x-auto">
            <code>{response.sql}</code>
          </pre>
        </div>

        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-300">Results:</h4>
          {Array.isArray(response.result) && response.result.length > 0 && typeof response.result[0] === 'object' ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-gray-400 text-sm">
                    {Object.keys(response.result[0]).map(header => (
                      <th key={header} className="py-2 pr-4">{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="text-gray-200">
                  {response.result.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {Object.values(row).map((value, valueIndex) => (
                        <td key={valueIndex} className="py-2 pr-4">
                          {value !== null && value !== undefined ? String(value) : ''}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <pre className="p-3 bg-[#1a1f2e] rounded-md text-gray-300 text-sm overflow-x-auto">
              {response.formatted_result}
            </pre>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-[#1a1f2e] pt-16">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-6">
          <div className="w-full min-h-full py-6">
            {messages.map(message => (
              <div key={message.id} className="mb-4">
                {message.isUser ? (
                  <div className="flex justify-end">
                    <div className="max-w-[240px]">
                      <div className="bg-[#4285f4] text-white px-4 py-2 rounded-xl">
                        {message.text}
                      </div>
                      <div className="text-sm text-[#4285f4] mt-1 text-right">
                        {message.timestamp}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col space-y-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-[#4285f4] text-white flex items-center justify-center">
                        A
                      </div>
                      <span className="text-gray-400">Assistant</span>
                    </div>
                    <div className="bg-[#1e2538] rounded-xl p-6 space-y-4">
                      <div className="text-white">{message.text}</div>
                      {message.sqlResponse && renderSqlResponse(message.sqlResponse)}
                      {message.showDynamicComponent && DynamicComponent && <DynamicComponent />}
                      <div className="text-sm text-[#4285f4] text-right">
                        {message.timestamp}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="border-t border-[#2a2f3e] bg-[#1a1f2e] py-6">
        <div className="max-w-2xl mx-auto px-4">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              placeholder="Stelle eine Frage oder frage nach Daten..."
              className="w-full bg-[#1e2538] rounded-full pl-12 pr-32 py-4 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-[#4285f4] border border-[#2a2f3e]"
              disabled={loading}
            />
            <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center space-x-2">
              <button type="button" className="text-gray-400 hover:text-gray-300 transition-colors">
                <Paperclip className="w-5 h-5" />
              </button>
            </div>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center space-x-4">
              <button type="button" className="text-gray-400 hover:text-gray-300 transition-colors">
                <Mic className="w-5 h-5" />
              </button>
              <button 
                type="submit" 
                className="text-[#4285f4] hover:text-[#4285f4]/90 transition-colors"
                disabled={loading}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </form>
          <div className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift + Enter for new line
          </div>
        </div>
      </div>
    </div>
  )
} 