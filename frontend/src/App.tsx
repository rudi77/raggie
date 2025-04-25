import { ThemeProvider } from './context/ThemeContext'
import { Header } from './components/layout/Header'
import { ChatInterface } from './components/layout/ChatInterface'

export default function App() {
  return (
    <ThemeProvider>
      <div className="flex flex-col min-h-screen bg-background">
        <Header />
        <main className="flex-1 pt-header">
          <ChatInterface />
        </main>
      </div>
    </ThemeProvider>
  )
} 