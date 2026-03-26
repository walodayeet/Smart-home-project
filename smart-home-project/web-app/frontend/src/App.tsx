import { useMemo } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { Header } from './components/Header'
import { BottomNav } from './components/BottomNav'
import { Dashboard } from './components/Dashboard'
import { CameraView } from './components/CameraView'
import { VoiceControl } from './components/VoiceControl'
import { DeviceGrid } from './components/DeviceGrid'
import { useWebSocket } from './hooks/useWebSocket'
import { useDevices } from './hooks/useDevices'
import { useCameras } from './hooks/useCameras'

const TAB_TO_PATH: Record<string, string> = {
  dashboard: '/dashboard',
  cameras: '/cameras',
  voice: '/voice',
  devices: '/devices',
}

function getTabFromPath(pathname: string): string {
  if (pathname.startsWith('/cameras')) return 'cameras'
  if (pathname.startsWith('/voice')) return 'voice'
  if (pathname.startsWith('/devices')) return 'devices'
  return 'dashboard'
}

function App() {
  const location = useLocation()
  const navigate = useNavigate()

  const { isConnected } = useWebSocket()
  useDevices()
  useCameras()

  const activeTab = useMemo(() => getTabFromPath(location.pathname), [location.pathname])

  const handleTabChange = (tab: string) => {
    const nextPath = TAB_TO_PATH[tab] ?? '/dashboard'
    if (nextPath !== location.pathname) {
      navigate(nextPath)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header isConnected={isConnected} />

      <main className="mx-auto max-w-7xl px-4 pt-14 pb-20">
        <div className="py-4">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/cameras" element={<CameraView />} />
            <Route path="/voice" element={<VoiceControl />} />
            <Route path="/devices" element={<DeviceGrid />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </main>

      <BottomNav activeTab={activeTab} onTabChange={handleTabChange} />

      {!isConnected && (
        <div className="fixed top-14 left-0 right-0 z-40 bg-warning py-2 text-center text-sm text-white">
          Reconnecting to server...
        </div>
      )}
    </div>
  )
}

export default App
