import { useEffect, useState } from 'react'
import { api } from '../api'
import { useStore, type Device } from '../store'

export function useDevices() {
  const devices = useStore((state) => state.devices)
  const setDevices = useStore((state) => state.setDevices)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchDevices = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = (await api.getDevices()) as Device[]
      setDevices(data)
    } catch (err) {
      setError('Failed to fetch devices')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const toggleDevice = async (deviceId: string): Promise<Device> => {
    try {
      const updatedDevice = (await api.toggleDevice(deviceId)) as Device
      useStore.getState().updateDevice(updatedDevice)
      return updatedDevice
    } catch (err) {
      console.error('Failed to toggle device:', err)
      throw err
    }
  }

  const sendCommand = async (
    deviceId: string,
    action: string,
    parameters?: Record<string, unknown>,
  ): Promise<Device> => {
    try {
      const updatedDevice = (await api.sendCommand(deviceId, action, parameters)) as Device
      useStore.getState().updateDevice(updatedDevice)
      return updatedDevice
    } catch (err) {
      console.error('Failed to send command:', err)
      throw err
    }
  }

  useEffect(() => {
    void fetchDevices()
  }, [])

  return {
    devices,
    isLoading,
    error,
    refresh: fetchDevices,
    toggleDevice,
    sendCommand,
  }
}
