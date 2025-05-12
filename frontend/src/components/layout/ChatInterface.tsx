'use client'

import { Paperclip, Mic, Send } from 'lucide-react'
import { useState } from 'react'
import * as Babel from '@babel/standalone'
import React from 'react'
import { queryText2Sql, QueryResponse } from '../../services/api'
import { SaveTemplateButton } from '../SaveTemplateButton'

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
  const [isCollapsed, setIsCollapsed] = useState(false)

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

  const renderSqlResponse = (response: QueryResponse, question: string) => {
    if (!response || !response.result) return null;

    return (
      <div className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <h4 className="text-sm font-medium text-light-text dark:text-dark-text">Generated SQL:</h4>
            <SaveTemplateButton query={response.sql} sourceQuestion={question} />
          </div>
          <pre className="p-3 bg-light-background dark:bg-dark-background rounded-md text-light-text dark:text-dark-text text-sm overflow-x-auto">
            <code>{response.sql}</code>
          </pre>
        </div>

        <div className="space-y-2">
          <h4 className="text-sm font-medium text-light-text dark:text-dark-text">Results:</h4>
          {Array.isArray(response.result) && response.result.length > 0 && typeof response.result[0] === 'object' ? (
            <div className="overflow-x-auto rounded-lg border border-light-border dark:border-dark-border">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-light-border dark:border-dark-border bg-light-background-lighter dark:bg-dark-background-lighter">
                    {Object.keys(response.result[0]).map(header => (
                      <th key={header} className="px-4 py-3 text-sm font-medium text-light-text dark:text-dark-text uppercase tracking-wider">
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-light-border dark:divide-dark-border">
                  {response.result.map((row, rowIndex) => (
                    <tr 
                      key={rowIndex}
                      className="bg-light-background-light dark:bg-dark-background-light hover:bg-light-background-lighter dark:hover:bg-dark-background-lighter transition-colors duration-150 ease-in-out"
                    >
                      {Object.values(row).map((value, valueIndex) => (
                        <td key={valueIndex} className="px-4 py-3 text-sm text-light-text dark:text-dark-text whitespace-nowrap">
                          {value !== null && value !== undefined ? String(value) : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <pre className="p-3 bg-light-background dark:bg-dark-background rounded-md text-light-text dark:text-dark-text text-sm overflow-x-auto">
              {response.formatted_result}
            </pre>
          )}
        </div>
      </div>
    );
  };

  return (
    <>
      {/* Backdrop when chat is open */}
      {!isCollapsed && (
        <div 
          className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40"
          onClick={() => setIsCollapsed(true)}
        />
      )}
      
      <div className={`fixed left-0 top-16 bottom-0 flex z-50 transition-all duration-300 ease-in-out ${isCollapsed ? 'w-12' : 'w-[600px]'}`}>
        {/* Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-12 flex items-center justify-center bg-light-background-light dark:bg-dark-background-light border-r border-light-border dark:border-dark-border hover:bg-light-background-lighter dark:hover:bg-dark-background-lighter transition-colors"
        >
          <span className="text-light-text-secondary dark:text-dark-text-secondary text-lg font-medium">
            {isCollapsed ? '→' : '←'}
          </span>
        </button>

        {/* Main Chat Container */}
        <div className={`flex flex-col flex-1 bg-light-background dark:bg-dark-background border-r border-light-border dark:border-dark-border shadow-lg ${isCollapsed ? 'hidden' : ''}`}>
          <div className="flex-1 overflow-y-auto">
            <div className="w-full min-h-full py-6 px-4">
              {messages.map(message => (
                <div key={message.id} className="mb-4">
                  {message.isUser ? (
                    <div className="flex justify-end">
                      <div className="max-w-[400px]">
                        <div className="bg-light-primary dark:bg-dark-primary text-white px-4 py-2 rounded-xl">
                          {message.text}
                        </div>
                        <div className="text-sm text-light-primary dark:text-dark-primary mt-1 text-right">
                          {message.timestamp}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col space-y-2">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-light-primary dark:bg-dark-primary text-white flex items-center justify-center">
                          A
                        </div>
                        <span className="text-light-text-secondary dark:text-dark-text-secondary">Assistant</span>
                      </div>
                      <div className="bg-light-background-light dark:bg-dark-background-light rounded-xl p-6 space-y-4">
                        <div className="text-light-text dark:text-dark-text">{message.text}</div>
                        {message.sqlResponse && renderSqlResponse(message.sqlResponse, message.text)}
                        {message.showDynamicComponent && DynamicComponent && <DynamicComponent />}
                        <div className="text-sm text-light-primary dark:text-dark-primary text-right">
                          {message.timestamp}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-light-border dark:border-dark-border bg-light-background dark:bg-dark-background py-4 px-4">
            <form onSubmit={handleSubmit} className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                placeholder="Stelle eine Frage oder frage nach Daten..."
                className="w-full bg-light-background-light dark:bg-dark-background-light rounded-full pl-12 pr-32 py-4 text-light-text dark:text-dark-text placeholder-light-text-secondary dark:placeholder-dark-text-secondary focus:outline-none focus:ring-1 focus:ring-light-primary dark:focus:ring-dark-primary border border-light-border dark:border-dark-border"
                disabled={loading}
              />
              <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center space-x-2">
                <button type="button" className="text-light-text-secondary dark:text-dark-text-secondary hover:text-light-text dark:hover:text-dark-text transition-colors">
                  <Paperclip className="w-5 h-5" />
                </button>
              </div>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center space-x-4">
                <button type="button" className="text-light-text-secondary dark:text-dark-text-secondary hover:text-light-text dark:hover:text-dark-text transition-colors">
                  <Mic className="w-5 h-5" />
                </button>
                <button 
                  type="submit" 
                  className="text-light-primary dark:text-dark-primary hover:text-light-primary/90 dark:hover:text-dark-primary/90 transition-colors"
                  disabled={loading}
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </form>
            <div className="text-xs text-light-text-secondary dark:text-dark-text-secondary mt-2 text-center">
              Press Enter to send, Shift + Enter for new line
            </div>
          </div>
        </div>
      </div>
    </>
  )
} 