import { useState, useRef } from 'react'
import { Upload, RefreshCw, AlertTriangle, UserX, UserCheck } from 'lucide-react'
import { useRecognition } from '../hooks/useRecognition'

export function RecognitionUpload() {
  const { uploadImage, isLoading, lastResult } = useRecognition()
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    
    // Show preview
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    
    // Upload and recognize
    try {
      await uploadImage(file)
    } catch (error) {
      console.error('Recognition failed:', error)
    }
  }
  
  const handleDrop = async (event: React.DragEvent) => {
    event.preventDefault()
    const file = event.dataTransfer.files?.[0]
    if (!file || !file.type.startsWith('image/')) return
    
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    
    try {
      await uploadImage(file)
    } catch (error) {
      console.error('Recognition failed:', error)
    }
  }
  
  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault()
  }
  
  const clearPreview = () => {
    setPreviewUrl(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }
  
  const getStatusIcon = () => {
    if (!lastResult) return null
    
    switch (lastResult.status) {
      case 'recognized':
        return <UserCheck className="w-12 h-12 text-success" />
      case 'unknown':
        return <UserX className="w-12 h-12 text-danger" />
      case 'masked':
        return <AlertTriangle className="w-12 h-12 text-warning" />
      default:
        return <AlertTriangle className="w-12 h-12 text-gray-400" />
    }
  }
  
  const getStatusColor = () => {
    if (!lastResult) return 'bg-gray-100'
    
    switch (lastResult.status) {
      case 'recognized':
        return 'bg-success/10 border-success/30'
      case 'unknown':
        return 'bg-danger/10 border-danger/30'
      case 'masked':
        return 'bg-warning/10 border-warning/30'
      default:
        return 'bg-gray-100'
    }
  }
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Face Recognition</h2>
        {previewUrl && (
          <button
            onClick={clearPreview}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Clear
          </button>
        )}
      </div>
      
      {!previewUrl ? (
        <div
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/50 transition-colors"
        >
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Upload className="w-8 h-8 text-primary-600" />
          </div>
          <p className="text-gray-700 font-medium mb-1">Tap to upload or drag image here</p>
          <p className="text-sm text-gray-500">JPG, PNG up to 10MB</p>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative rounded-xl overflow-hidden">
            <img
              src={previewUrl}
              alt="Preview"
              className="w-full h-64 object-cover"
            />
            {isLoading && (
              <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                <RefreshCw className="w-8 h-8 text-white animate-spin" />
              </div>
            )}
          </div>
          
          {lastResult && !isLoading && (
            <div className={`rounded-xl p-4 border ${getStatusColor()}`}>
              <div className="flex items-start gap-4">
                {getStatusIcon()}
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">
                    {lastResult.status === 'recognized'
                      ? lastResult.person_name
                      : lastResult.status === 'unknown'
                      ? 'Unknown Person'
                      : 'Partial Recognition'}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">{lastResult.message}</p>
                  
                  {lastResult.confidence > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">Confidence</span>
                        <span className="font-medium">
                          {(lastResult.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            lastResult.confidence > 0.8
                              ? 'bg-success'
                              : lastResult.confidence > 0.5
                              ? 'bg-warning'
                              : 'bg-danger'
                          }`}
                          style={{ width: `${lastResult.confidence * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                  
                  {lastResult.requires_action && (
                    <div className="mt-3 flex items-center gap-2 text-danger">
                      <AlertTriangle className="w-4 h-4" />
                      <span className="text-sm font-medium">Action Required</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="bg-blue-50 rounded-lg p-3 text-sm text-blue-800">
        <p className="font-medium mb-1">Demo Mode</p>
        <p>Upload any image to see simulated recognition results. The system will randomly return recognized, unknown, or masked detection.</p>
      </div>
    </div>
  )
}
