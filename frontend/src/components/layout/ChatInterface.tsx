'use client'

import { Paperclip, Mic, Send } from 'lucide-react'
import { useState, useEffect } from 'react'
import * as Babel from '@babel/standalone'
import React from 'react'

interface Message {
  id: string
  text: string
  timestamp: string
  isUser: boolean
  showDynamicComponent?: boolean
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [DynamicComponent, setDynamicComponent] = useState<React.FC | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
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

          // Create a new function to evaluate the code in the proper context
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
          }
        })
        .catch(err => {
          console.error('Error fetching or transpiling code:', err)
        })
    }

    setInputValue('')
  }

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
                      <span className="text-gray-400">Accountant</span>
                    </div>
                    <div className="bg-[#1e2538] rounded-xl p-6 space-y-4">
                      <h2 className="text-xl text-white font-medium">Aktuelle Buchungen</h2>
                      <p className="text-gray-400 text-sm">
                        Hier sind die letzten Buchungen aufgelistet. Alle Beträge sind in EUR.
                      </p>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left">
                          <thead>
                            <tr className="text-gray-400 text-sm">
                              <th className="py-2">DATUM</th>
                              <th className="py-2">BESCHREIBUNG</th>
                              <th className="py-2">KATEGORIE</th>
                              <th className="py-2 text-right">BETRAG</th>
                            </tr>
                          </thead>
                          <tbody className="text-gray-200">
                            <tr>
                              <td className="py-2">2024-02-01</td>
                              <td className="py-2">Büromaterial</td>
                              <td className="py-2">Betriebsausgaben</td>
                              <td className="py-2 text-right">156,78</td>
                            </tr>
                            {/* Add more rows as needed */}
                          </tbody>
                        </table>
                      </div>
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
              placeholder="Type your instructions..."
              className="w-full bg-[#1e2538] rounded-full pl-12 pr-32 py-4 text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-[#4285f4] border border-[#2a2f3e]"
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
              <button type="submit" className="text-[#4285f4] hover:text-[#4285f4]/90 transition-colors">
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