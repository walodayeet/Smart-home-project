import { useEffect, useState } from 'react'
import { api } from '../api'
import { useStore, type Camera } from '../store'

export function useCameras() {
  const cameras = useStore((state) => state.cameras)
  const setCameras = useStore((state) => state.setCameras)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchCameras = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = (await api.getCameras()) as Camera[]
      setCameras(data)
    } catch (err) {
      setError('Failed to fetch cameras')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const getSnapshot = async (cameraId: string): Promise<unknown> => {
    try {
      return await api.getCameraSnapshot(cameraId)
    } catch (err) {
      console.error('Failed to get snapshot:', err)
      throw err
    }
  }

  useEffect(() => {
    void fetchCameras()
  }, [])

  return {
    cameras,
    isLoading,
    error,
    refresh: fetchCameras,
    getSnapshot,
  }
}
