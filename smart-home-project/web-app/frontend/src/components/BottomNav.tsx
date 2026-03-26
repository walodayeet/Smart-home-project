import { Camera, Mic, Grid3X3, Home } from 'lucide-react'

interface BottomNavProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

const tabs = [
  { id: 'dashboard', label: 'Home', icon: Home },
  { id: 'cameras', label: 'Cameras', icon: Camera },
  { id: 'voice', label: 'Voice', icon: Mic },
  { id: 'devices', label: 'Devices', icon: Grid3X3 },
]

export function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-bottom z-50">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive
                  ? 'text-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon
                size={24}
                className={`mb-1 transition-transform ${
                  isActive ? 'scale-110' : ''
                }`}
              />
              <span className="text-xs font-medium">{tab.label}</span>
              {isActive && (
                <div className="absolute bottom-0 w-12 h-0.5 bg-primary-600 rounded-full" />
              )}
            </button>
          )
        })}
      </div>
    </nav>
  )
}
