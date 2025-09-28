import React from 'react'

interface SidebarProps {
  active: 'chat' | 'live'
  onSelect: (page: 'chat' | 'live') => void
  conversations?: { id: number; title: string | null; created_at: string }[]
  activeConversationId?: number | null
  onSelectConversation?: (id: number) => void
  onNewChat?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ active, onSelect, conversations = [], activeConversationId = null, onSelectConversation, onNewChat }) => {
  const itemBase = 'w-full text-left px-4 py-3 rounded-md transition-colors'
  const activeStyles = 'bg-light-background-lighter dark:bg-dark-background-lighter text-light-text dark:text-dark-text'
  const inactiveStyles = 'text-light-text-secondary dark:text-dark-text-secondary hover:bg-light-background-lighter dark:hover:bg-dark-background-lighter'

  return (
    <aside className="w-56 shrink-0 h-[calc(100vh-4rem)] border-r border-light-border dark:border-dark-border bg-light-background-light dark:bg-dark-background-light p-3 flex flex-col">
      <nav className="space-y-2">
        <button
          className={`${itemBase} ${active === 'chat' ? activeStyles : inactiveStyles}`}
          onClick={() => onSelect('chat')}
        >
          Chat
        </button>
        <button
          className={`${itemBase} ${active === 'live' ? activeStyles : inactiveStyles}`}
          onClick={() => onSelect('live')}
        >
          Live Tiles
        </button>
      </nav>

      {active === 'chat' && (
        <div className="mt-4 flex-1 min-h-0 flex flex-col">
          <div className="flex items-center justify-between mb-2 px-1">
            <h3 className="text-sm font-semibold text-light-text dark:text-dark-text">Chats</h3>
            <button
              className="text-xs px-2 py-1 rounded-md border border-light-border dark:border-dark-border text-light-text-secondary dark:text-dark-text-secondary hover:bg-light-background-lighter dark:hover:bg-dark-background-lighter"
              onClick={onNewChat}
            >
              Neuer Chat
            </button>
          </div>
          <div className="overflow-y-auto space-y-1">
            {conversations.map(c => {
              const title = c.title && c.title.trim().length > 0 ? c.title : `Chat ${c.id}`
              const isActive = c.id === activeConversationId
              return (
                <button
                  key={c.id}
                  className={`${itemBase} w-full ${isActive ? activeStyles : inactiveStyles}`}
                  onClick={() => onSelectConversation && onSelectConversation(c.id)}
                >
                  <div className="text-sm text-left truncate">{title}</div>
                  <div className="text-xs text-light-text-secondary dark:text-dark-text-secondary text-left truncate">
                    {new Date(c.created_at).toLocaleDateString('de-DE')} {new Date(c.created_at).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </button>
              )
            })}
            {conversations.length === 0 && (
              <div className="text-xs text-light-text-secondary dark:text-dark-text-secondary px-2 py-2">
                Keine Chats vorhanden.
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  )
}


