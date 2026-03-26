import { create } from 'zustand'

export interface Device {
  id: string
  name: string
  type: 'lock' | 'light' | 'blinds' | 'camera' | 'sensor'
  online: boolean
  state: string
  battery_level?: number
  last_seen: string
  metadata: Record<string, any>
}

export interface RecognitionEvent {
  status: 'recognized' | 'unknown' | 'masked' | 'error'
  person_id?: string
  person_name?: string
  confidence: number
  timestamp: string
  message: string
  requires_action: boolean
}

export interface Camera {
  id: string
  name: string
  location: string
  status: string
  resolution: string
  fps: number
}

interface AppState {
  // Devices
  devices: Device[]
  setDevices: (devices: Device[]) => void
  updateDevice: (device: Device) => void
  
  // Recognition
  recentEvents: RecognitionEvent[]
  setRecentEvents: (events: RecognitionEvent[]) => void
  addEvent: (event: RecognitionEvent) => void
  
  // Cameras
  cameras: Camera[]
  setCameras: (cameras: Camera[]) => void
  
  // System
  isConnected: boolean
  setIsConnected: (connected: boolean) => void
  systemStatus: any
  setSystemStatus: (status: any) => void
  
  // UI
  activeTab: string
  setActiveTab: (tab: string) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export const useStore = create<AppState>((set) => ({
  // Devices
  devices: [],
  setDevices: (devices) => set({ devices }),
  updateDevice: (device) => set((state) => ({
    devices: state.devices.map((d) => d.id === device.id ? device : d)
  })),
  
  // Recognition
  recentEvents: [],
  setRecentEvents: (events) => set({ recentEvents: events }),
  addEvent: (event) => set((state) => ({
    recentEvents: [event, ...state.recentEvents].slice(0, 50)
  })),
  
  // Cameras
  cameras: [],
  setCameras: (cameras) => set({ cameras }),
  
  // System
  isConnected: false,
  setIsConnected: (connected) => set({ isConnected: connected }),
  systemStatus: null,
  setSystemStatus: (status) => set({ systemStatus: status }),
  
  // UI
  activeTab: 'dashboard',
  setActiveTab: (tab) => set({ activeTab: tab }),
  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
}))
