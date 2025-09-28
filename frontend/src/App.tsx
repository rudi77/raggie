import { useEffect, useState } from 'react'
import { ThemeProvider } from './context/ThemeContext'
import { Header } from './components/layout/Header'
import { ChatInterface } from './components/layout/ChatInterface'
import { LiveTileGrid } from './components/live/LiveTileGrid'
import { Sidebar } from './components/layout/Sidebar'
import { listConversations, createConversation, type ConversationSummary } from './services/chat.service'

export default function App() {
  const [page, setPage] = useState<'chat' | 'live'>('chat')
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [conversationId, setConversationId] = useState<number | null>(null)

  useEffect(() => {
    const init = async () => {
      try {
        const list = await listConversations()
        setConversations(list)

        let cid: number | null = null
        const stored = localStorage.getItem('chat.conversationId')
        if (stored) {
          const parsed = parseInt(stored, 10)
          if (!Number.isNaN(parsed) && list.some(c => c.id === parsed)) {
            cid = parsed
          }
        }
        if (!cid) {
          if (list.length > 0) {
            cid = list[0].id
          } else {
            const created = await createConversation()
            cid = created.id
          }
        }
        setConversationId(cid)
        localStorage.setItem('chat.conversationId', String(cid))
      } catch (e) {
        console.error('Failed to initialize conversations', e)
      }
    }
    init()
  }, [])

  const handleSelectConversation = (id: number) => {
    setConversationId(id)
    localStorage.setItem('chat.conversationId', String(id))
    setPage('chat')
  }

  const handleNewChat = async () => {
    try {
      const created = await createConversation()
      const list = await listConversations()
      setConversations(list)
      setConversationId(created.id)
      localStorage.setItem('chat.conversationId', String(created.id))
      setPage('chat')
    } catch (e) {
      console.error('Failed to create new conversation', e)
    }
  }

  return (
    <ThemeProvider>
      <div className="flex flex-col min-h-screen bg-light-background dark:bg-dark-background">
        <Header />
        <main className="flex-1 pt-16">
          <div className="flex h-full">
            <Sidebar 
              active={page} 
              onSelect={setPage}
              conversations={conversations}
              activeConversationId={conversationId}
              onSelectConversation={handleSelectConversation}
              onNewChat={handleNewChat}
            />
            <div className="flex-1 overflow-auto">
              {/* Chat Page (keeps mounted) */}
              <div className={`${page === 'chat' ? 'block' : 'hidden'} h-full`}> 
                <div className="h-full flex items-start justify-center p-4">
                  <div className="w-full max-w-3xl">
                    <ChatInterface centered={true} conversationId={conversationId} />
                  </div>
                </div>
              </div>

              {/* Live Tiles Page (keeps mounted) */}
              <div className={`${page === 'live' ? 'block' : 'hidden'}`}>
                <div className="p-4">
                  <h2 className="text-2xl font-bold mb-4 text-light-text dark:text-dark-text">Live Tiles</h2>
                  <LiveTileGrid />
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ThemeProvider>
  )
} 