import React from 'react'

interface SidebarProps {
  active: 'chat' | 'live'
  onSelect: (page: 'chat' | 'live') => void
}

export const Sidebar: React.FC<SidebarProps> = ({ active, onSelect }) => {
  const itemBase = 'w-full text-left px-4 py-3 rounded-md transition-colors'
  const activeStyles = 'bg-light-background-lighter dark:bg-dark-background-lighter text-light-text dark:text-dark-text'
  const inactiveStyles = 'text-light-text-secondary dark:text-dark-text-secondary hover:bg-light-background-lighter dark:hover:bg-dark-background-lighter'

  return (
    <aside className="w-56 shrink-0 h-[calc(100vh-4rem)] border-r border-light-border dark:border-dark-border bg-light-background-light dark:bg-dark-background-light p-3">
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
    </aside>
  )
}


