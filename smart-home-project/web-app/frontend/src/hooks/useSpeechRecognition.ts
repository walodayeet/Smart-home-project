import { useState, useCallback, useRef, useEffect } from 'react'

interface UseSpeechRecognitionOptions {
  onResult?: (text: string) => void
  onError?: (error: string) => void
  continuous?: boolean
  lang?: string
}

export function useSpeechRecognition(options: UseSpeechRecognitionOptions = {}) {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [isSupported, setIsSupported] = useState(true)
  const recognitionRef = useRef<any>(null)
  
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setIsSupported(false)
      return
    }
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    recognitionRef.current = new SpeechRecognition()
    recognitionRef.current.continuous = options.continuous ?? false
    recognitionRef.current.interimResults = true
    recognitionRef.current.lang = options.lang ?? 'en-US'
    
    recognitionRef.current.onstart = () => {
      setIsListening(true)
      setTranscript('')
    }
    
    recognitionRef.current.onresult = (event: any) => {
      let finalTranscript = ''
      let interimTranscript = ''
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }
      
      const currentTranscript = finalTranscript || interimTranscript
      setTranscript(currentTranscript)
      
      if (finalTranscript && options.onResult) {
        options.onResult(finalTranscript)
      }
    }
    
    recognitionRef.current.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      if (options.onError) {
        options.onError(event.error)
      }
    }
    
    recognitionRef.current.onend = () => {
      setIsListening(false)
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [options.continuous, options.lang, options.onResult, options.onError])
  
  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Failed to start speech recognition:', error)
      }
    }
  }, [isListening])
  
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }, [isListening])
  
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }, [isListening, startListening, stopListening])
  
  return {
    isListening,
    transcript,
    isSupported,
    startListening,
    stopListening,
    toggleListening,
  }
}
