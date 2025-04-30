import { ThemeProvider } from './context/ThemeContext'
import { Header } from './components/layout/Header'
import { ChatInterface } from './components/layout/ChatInterface'
import { LiveTileGrid } from './components/live/LiveTileGrid'

export default function App() {
  return (
    <ThemeProvider>
      <div className="flex flex-col min-h-screen bg-light-background dark:bg-dark-background">
        <Header />
        <main className="flex-1 pt-16">
          <div className="flex h-full">
            <div className="flex-1 overflow-auto p-4">
              <div className="max-w-7xl mx-auto">
                <h2 className="text-2xl font-bold mb-4 text-light-text dark:text-dark-text">
                  Dashboard
                </h2>
                <LiveTileGrid />
              </div>
            </div>
          </div>
          <ChatInterface />
        </main>
      </div>
    </ThemeProvider>
  )
} 