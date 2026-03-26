import { AlertCircle, Shield, Wifi, WifiOff } from 'lucide-react'
import { useSystemStatus } from '../hooks/useSystemStatus'

interface HeaderProps {
  isConnected: boolean
}

export function Header({ isConnected }: HeaderProps) {
  const { status } = useSystemStatus()
  const hasAlert = (status?.recent_events ?? 0) > 0

  return (
    <header className="safe-top fixed top-0 left-0 right-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-lg items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
            <Shield className="h-5 w-5 text-white" aria-hidden="true" />
          </div>
          <h1 className="text-lg font-bold text-gray-900">Smart Home</h1>
        </div>

        <div className="flex items-center gap-3">
          {hasAlert && (
            <div className="relative" aria-label="System alerts available">
              <AlertCircle className="h-5 w-5 text-danger" />
              <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-danger animate-pulse" />
            </div>
          )}

          <div className="flex items-center gap-1.5 text-sm" aria-live="polite">
            {isConnected ? (
              <>
                <Wifi className="h-4 w-4 text-success" aria-hidden="true" />
                <span className="hidden font-medium text-success sm:inline">Connected</span>
              </>
            ) : (
              <>
                <WifiOff className="h-4 w-4 text-gray-400" aria-hidden="true" />
                <span className="hidden text-gray-500 sm:inline">Offline</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
