const API_BASE = '/api'

class ApiService {
  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    
    return response.json()
  }
  
  // Health
  async healthCheck() {
    return this.fetch('/health')
  }
  
  // Devices
  async getDevices() {
    return this.fetch('/devices')
  }
  
  async getDevice(deviceId: string) {
    return this.fetch(`/devices/${deviceId}`)
  }
  
  async toggleDevice(deviceId: string) {
    return this.fetch(`/devices/${deviceId}/toggle`, { method: 'POST' })
  }
  
  async sendCommand(deviceId: string, action: string, parameters?: any) {
    return this.fetch(`/devices/${deviceId}/command`, {
      method: 'POST',
      body: JSON.stringify({ action, parameters }),
    })
  }
  
  // Cameras
  async getCameras() {
    return this.fetch('/cameras')
  }
  
  async getCameraSnapshot(cameraId: string) {
    return this.fetch(`/cameras/${cameraId}/snapshot`)
  }
  
  // Recognition
  async uploadImage(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE}/recognition/upload`, {
      method: 'POST',
      body: formData,
    })
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`)
    }
    
    return response.json()
  }
  
  async getRecentRecognitions(limit = 10) {
    return this.fetch(`/recognition/recent?limit=${limit}`)
  }
  
  // Voice
  async sendVoiceCommand(text: string) {
    return this.fetch('/voice/command', {
      method: 'POST',
      body: JSON.stringify({ text }),
    })
  }
  
  // Access Log
  async getAccessLog(limit = 50) {
    return this.fetch(`/access-log?limit=${limit}`)
  }
  
  // System
  async getSystemStatus() {
    return this.fetch('/system/status')
  }
}

export const api = new ApiService()
