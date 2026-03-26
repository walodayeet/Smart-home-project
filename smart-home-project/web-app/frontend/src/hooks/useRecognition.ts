import { useState } from 'react'
import { api } from '../api'
import { useStore, type RecognitionEvent } from '../store'

export function useRecognition() {
  const recentEvents = useStore((state) => state.recentEvents)
  const setRecentEvents = useStore((state) => state.setRecentEvents)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastResult, setLastResult] = useState<RecognitionEvent | null>(null)

  const uploadImage = async (file: File): Promise<RecognitionEvent> => {
    setIsLoading(true)
    setError(null)
    try {
      const result = (await api.uploadImage(file)) as RecognitionEvent
      setLastResult(result)
      return result
    } catch (err) {
      setError('Failed to process image')
      console.error(err)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const fetchRecentEvents = async (limit = 10): Promise<RecognitionEvent[]> => {
    setIsLoading(true)
    setError(null)
    try {
      const data = (await api.getRecentRecognitions(limit)) as RecognitionEvent[]
      setRecentEvents(data)
      return data
    } catch (err) {
      setError('Failed to fetch recent events')
      console.error(err)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    recentEvents,
    isLoading,
    error,
    lastResult,
    uploadImage,
    fetchRecentEvents,
  }
}
