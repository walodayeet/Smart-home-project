import { useCallback, useRef, useState } from 'react'
import { Loader2, Mic, MicOff, Send, Sparkles } from 'lucide-react'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'
import { api } from '../api'

interface VoiceCommandResult {
  success: boolean
  message: string
  action?: string
}

const SUGGESTIONS = [
  'Lock the door',
  'Turn on lights',
  'Turn off all lights',
  'Open the blinds',
  'Close the blinds',
  'Unlock front door',
]

function normalizeVoiceResult(payload: unknown): VoiceCommandResult {
  if (!payload || typeof payload !== 'object') {
    return {
      success: false,
      message: 'Command processed, but no response message was returned.',
    }
  }

  const data = payload as Record<string, unknown>

  return {
    success: typeof data.success === 'boolean' ? data.success : true,
    message: typeof data.message === 'string' ? data.message : 'Command sent successfully.',
    action: typeof data.action === 'string' ? data.action : undefined,
  }
}

export function VoiceControl() {
  const [response, setResponse] = useState<VoiceCommandResult | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [lastSubmittedText, setLastSubmittedText] = useState('')
  const ignoreNextClickRef = useRef(false)

  const sendVoiceCommand = useCallback(async (text: string) => {
    const commandText = text.trim()
    if (!commandText) {
      return
    }

    setIsProcessing(true)
    setResponse(null)
    setLastSubmittedText(commandText)

    try {
      const result = await api.sendVoiceCommand(commandText)
      setResponse(normalizeVoiceResult(result))
    } catch (error) {
      console.error('Failed to process voice command', error)
      setResponse({
        success: false,
        message: 'Failed to process command. Please try again.',
      })
    } finally {
      setIsProcessing(false)
    }
  }, [])

  const handleSpeechResult = useCallback(
    (text: string) => {
      void sendVoiceCommand(text)
    },
    [sendVoiceCommand],
  )

  const handleSpeechError = useCallback((error: string) => {
    setResponse({
      success: false,
      message: `Speech recognition error: ${error}`,
    })
  }, [])

  const {
    isListening,
    transcript,
    isSupported,
    startListening,
    stopListening,
  } = useSpeechRecognition({
    onResult: handleSpeechResult,
    onError: handleSpeechError,
    continuous: true,
    lang: 'en-US',
  })

  const handleMicPointerDown = () => {
    if (isProcessing || isListening) {
      return
    }

    ignoreNextClickRef.current = true
    startListening()
  }

  const handleMicClick = () => {
    if (ignoreNextClickRef.current) {
      ignoreNextClickRef.current = false
      return
    }

    if (isListening) {
      stopListening()
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    void sendVoiceCommand(suggestion)
  }

  if (!isSupported) {
    return (
      <section className="card p-6 text-center" aria-label="Voice control unsupported">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-danger/10 text-danger">
          <MicOff className="h-7 w-7" aria-hidden="true" />
        </div>
        <h2 className="text-lg font-semibold text-gray-900">Voice control unavailable</h2>
        <p className="mt-2 text-sm text-gray-600">
          Your browser does not support speech recognition. Use Chrome or Edge for voice commands.
        </p>
      </section>
    )
  }

  return (
    <section className="space-y-5 animate-slide-in" aria-label="Voice control panel">
      <div className="card p-6">
        <div className="flex flex-col items-center justify-center">
          <div className="relative mb-5 flex h-40 w-40 items-center justify-center">
            {isListening && (
              <>
                <span className="absolute inline-flex h-40 w-40 rounded-full bg-primary-500/20 animate-pulse-ring" />
                <span className="absolute inline-flex h-32 w-32 rounded-full bg-primary-500/30 animate-pulse-ring" />
              </>
            )}

            <button
              type="button"
              onPointerDown={handleMicPointerDown}
              onClick={handleMicClick}
              disabled={isProcessing}
              className={`relative z-10 flex h-28 w-28 items-center justify-center rounded-full text-white shadow-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-primary-200 active:scale-95 disabled:cursor-not-allowed disabled:opacity-70 ${
                isListening ? 'bg-danger' : 'bg-primary-600 hover:bg-primary-700'
              }`}
              aria-label={isListening ? 'Stop voice recording' : 'Start voice recording'}
              aria-pressed={isListening}
            >
              {isProcessing ? (
                <Loader2 className="h-11 w-11 animate-spin" aria-hidden="true" />
              ) : isListening ? (
                <MicOff className="h-11 w-11" aria-hidden="true" />
              ) : (
                <Mic className="h-11 w-11" aria-hidden="true" />
              )}
            </button>
          </div>

          <p className="text-sm font-medium text-gray-700">
            {isListening
              ? 'Listening… Tap again to stop.'
              : isProcessing
                ? 'Processing command…'
                : 'Hold to start recording, tap to stop.'}
          </p>
        </div>
      </div>

      <div className="card p-4" aria-live="polite">
        <h3 className="mb-2 text-sm font-semibold text-gray-700">Transcript</h3>
        <p className="min-h-[2.5rem] text-sm text-gray-900">
          {transcript || <span className="text-gray-400">Start speaking to see your transcript…</span>}
        </p>
      </div>

      <div className="card p-4">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
          <Sparkles className="h-4 w-4 text-primary-600" aria-hidden="true" />
          Suggested commands
        </div>
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={isListening || isProcessing}
              className="rounded-full bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-60"
              aria-label={`Use suggestion: ${suggestion}`}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {(response || lastSubmittedText) && (
        <div
          className={`rounded-xl border p-4 ${
            response?.success
              ? 'border-success/30 bg-success/10 text-success'
              : 'border-danger/30 bg-danger/10 text-danger'
          }`}
          role="status"
          aria-live="polite"
        >
          <div className="mb-1 flex items-center gap-2 text-sm font-semibold">
            <Send className="h-4 w-4" aria-hidden="true" />
            Command response
          </div>
          <p className="text-sm">
            <span className="font-medium">“{lastSubmittedText || 'Voice command'}”</span>
            {' — '}
            {response?.message ?? 'Awaiting response…'}
          </p>
          {response?.action && (
            <p className="mt-2 text-xs opacity-90">
              Action: <code className="rounded bg-white/50 px-1 py-0.5">{response.action}</code>
            </p>
          )}
        </div>
      )}
    </section>
  )
}
