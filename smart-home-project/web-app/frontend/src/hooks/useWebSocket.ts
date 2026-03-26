import { useEffect, useRef, useState, useCallback } from 'react'
import { useStore } from '../store'

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const setDevices = useStore((state) => state.setDevices)
  const updateDevice = useStore((state) => state.updateDevice)
  const addEvent = useStore((state) => state.addEvent)
  
  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    
    ws.current = new WebSocket(wsUrl)
    
    ws.current.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
    }
    
    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        switch (data.type) {
          case 'devices_update':
            setDevices(data.devices)
            break
          case 'device_update':
            updateDevice(data.status)
            break
          case 'recognition_event':
            addEvent(data.event)
            break
          default:
            console.log('Unknown message type:', data.type)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
      // Attempt to reconnect after 3 seconds
      setTimeout(connect, 3000)
    }
    
    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }, [setDevices, updateDevice, addEvent])
  
  useEffect(() => {
    connect()
    
    return () => {
      ws.current?.close()
    }
  }, [connect])
  
  return { isConnected, ws: ws.current }
}
