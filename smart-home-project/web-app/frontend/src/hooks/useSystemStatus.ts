import { useEffect, useState } from 'react'
import { api } from '../api'

export function useSystemStatus() {
  const [status, setStatus] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const fetchStatus = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await api.getSystemStatus()
      setStatus(data)
    } catch (err) {
      setError('Failed to fetch system status')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }
  
  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])
  
  return {
    status,
    isLoading,
    error,
    refresh: fetchStatus,
  }
}
