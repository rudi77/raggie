import { useState } from 'react'
import { ThemeProvider } from './context/ThemeContext'
import { Header } from './components/layout/Header'
import { ChatInterface } from './components/layout/ChatInterface'
import { LiveTileGrid } from './components/live/LiveTileGrid'
import { Sidebar } from './components/layout/Sidebar'

export default function App() {
  const [page, setPage] = useState<'chat' | 'live'>('chat')
  return (
    <ThemeProvider>
      <div className="flex flex-col min-h-screen bg-light-background dark:bg-dark-background">
        <Header />
        <main className="flex-1 pt-16">
          <div className="flex h-full">
            <Sidebar active={page} onSelect={setPage} />
            <div className="flex-1 overflow-auto">
              {/* Chat Page (keeps mounted) */}
              <div className={`${page === 'chat' ? 'block' : 'hidden'} h-full`}> 
                <div className="h-full flex items-start justify-center p-4">
                  <div className="w-full max-w-3xl">
                    <ChatInterface centered={true} />
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