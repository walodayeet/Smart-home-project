import { useMemo, useState } from 'react'
import {
  Battery,
  Blinds,
  Clock3,
  Lightbulb,
  Lock,
  Unlock,
  Signal,
  SignalZero,
  Sun,
} from 'lucide-react'
import type { Device } from '../store'

interface DeviceCardProps {
  device: Device
  onToggle: (deviceId: string) => Promise<Device>
  onCommand: (deviceId: string, action: string, parameters?: Record<string, unknown>) => Promise<Device>
}

function formatLastSeen(timestamp: string): string {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return 'Unknown'
  }

  const diffMs = Date.now() - date.getTime()
  const diffMinutes = Math.floor(diffMs / 60000)

  if (diffMinutes < 1) {
    return 'Just now'
  }

  if (diffMinutes < 60) {
    return `${diffMinutes}m ago`
  }

  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) {
    return `${diffHours}h ago`
  }

  return `${Math.floor(diffHours / 24)}d ago`
}

function getBatteryTone(level: number): string {
  if (level <= 20) {
    return 'text-danger'
  }
  if (level <= 40) {
    return 'text-warning'
  }
  return 'text-success'
}

function getBrightness(device: Device): number {
  const value = device.metadata?.brightness
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return device.state === 'on' ? 100 : 0
  }

  return Math.min(100, Math.max(0, Math.round(value)))
}

function getBlindPosition(device: Device): number {
  const value = device.metadata?.position
  if (typeof value !== 'number' || Number.isNaN(value)) {
    if (device.state === 'open') return 100
    if (device.state === 'closed') return 0
    return 50
  }

  return Math.min(100, Math.max(0, Math.round(value)))
}

export function DeviceCard({ device, onToggle, onCommand }: DeviceCardProps) {
  const [isPending, setIsPending] = useState(false)
  const [localBrightness, setLocalBrightness] = useState(() => getBrightness(device))

  const isOnline = device.online
  const normalizedState = device.state.toLowerCase()
  const isLocked = normalizedState.includes('locked')
  const isLightOn = normalizedState === 'on'
  const blindPosition = useMemo(() => getBlindPosition(device), [device])

  const runAction = async (action: () => Promise<unknown>) => {
    if (isPending || !isOnline) {
      return
    }

    setIsPending(true)
    try {
      await action()
    } catch (error) {
      console.error('Device action failed', error)
    } finally {
      setIsPending(false)
    }
  }

  const updateBrightness = async (value: number) => {
    setLocalBrightness(value)
    await runAction(() => onCommand(device.id, 'set_brightness', { brightness: value }))
  }

  const statusLabel = isOnline ? 'Online' : 'Offline'

  return (
    <article
      className="card p-4 transition-transform duration-150 active:scale-95"
      aria-label={`${device.name} device card`}
    >
      <header className="mb-4 flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="rounded-lg bg-gray-100 p-2 text-primary-600" aria-hidden="true">
            {device.type === 'lock' && (isLocked ? <Lock className="h-5 w-5" /> : <Unlock className="h-5 w-5" />)}
            {device.type === 'light' && <Lightbulb className="h-5 w-5" />}
            {device.type === 'blinds' && <Blinds className="h-5 w-5" />}
          </div>

          <div className="min-w-0">
            <h3 className="truncate font-semibold text-gray-900">{device.name}</h3>
            <p className="truncate text-sm capitalize text-gray-500">{device.type}</p>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1 text-xs">
          <span className="flex items-center gap-1 text-gray-600">
            {isOnline ? (
              <Signal className="h-3.5 w-3.5 text-success" aria-hidden="true" />
            ) : (
              <SignalZero className="h-3.5 w-3.5 text-gray-400" aria-hidden="true" />
            )}
            <span>{statusLabel}</span>
          </span>

          {typeof device.battery_level === 'number' && (
            <span className={`flex items-center gap-1 ${getBatteryTone(device.battery_level)}`}>
              <Battery className="h-3.5 w-3.5" aria-hidden="true" />
              <span>{device.battery_level}%</span>
            </span>
          )}
        </div>
      </header>

      {device.type === 'lock' && (
        <section className="space-y-3" aria-label="Lock controls">
          <p className="text-sm text-gray-600">
            Status:{' '}
            <span className={isLocked ? 'font-medium text-success' : 'font-medium text-warning'}>
              {isLocked ? 'Locked' : 'Unlocked'}
            </span>
          </p>
          <button
            type="button"
            onClick={() => void runAction(() => onToggle(device.id))}
            disabled={!isOnline || isPending}
            className={`btn w-full ${isLocked ? 'btn-danger' : 'btn-success'} disabled:cursor-not-allowed disabled:opacity-60`}
            aria-label={isLocked ? `Unlock ${device.name}` : `Lock ${device.name}`}
          >
            {isLocked ? (
              <>
                <Unlock className="mr-2 h-4 w-4" aria-hidden="true" />
                Unlock
              </>
            ) : (
              <>
                <Lock className="mr-2 h-4 w-4" aria-hidden="true" />
                Lock
              </>
            )}
          </button>
        </section>
      )}

      {device.type === 'light' && (
        <section className="space-y-3" aria-label="Light controls">
          <p className="text-sm text-gray-600">
            Status:{' '}
            <span className={isLightOn ? 'font-medium text-warning' : 'font-medium text-gray-600'}>
              {isLightOn ? 'On' : 'Off'}
            </span>
          </p>

          <button
            type="button"
            onClick={() => void runAction(() => onToggle(device.id))}
            disabled={!isOnline || isPending}
            className={`btn w-full ${isLightOn ? 'btn-secondary' : 'btn-primary'} disabled:cursor-not-allowed disabled:opacity-60`}
            aria-label={`${isLightOn ? 'Turn off' : 'Turn on'} ${device.name}`}
          >
            <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
            Turn {isLightOn ? 'Off' : 'On'}
          </button>

          <div>
            <label htmlFor={`brightness-${device.id}`} className="mb-1 flex items-center justify-between text-sm text-gray-600">
              <span className="inline-flex items-center gap-1">
                <Sun className="h-4 w-4" aria-hidden="true" />
                Brightness
              </span>
              <span className="font-medium text-gray-900">{localBrightness}%</span>
            </label>
            <input
              id={`brightness-${device.id}`}
              type="range"
              min={0}
              max={100}
              step={1}
              value={localBrightness}
              onChange={(event) => setLocalBrightness(Number(event.currentTarget.value))}
              onPointerUp={(event) => {
                const value = Number((event.currentTarget as HTMLInputElement).value)
                void updateBrightness(value)
              }}
              onKeyUp={(event) => {
                if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                  const value = Number((event.currentTarget as HTMLInputElement).value)
                  void updateBrightness(value)
                }
              }}
              disabled={!isOnline || isPending}
              className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-gray-200 accent-primary-600 disabled:cursor-not-allowed"
              aria-label={`Brightness control for ${device.name}`}
            />
          </div>
        </section>
      )}

      {device.type === 'blinds' && (
        <section className="space-y-3" aria-label="Blinds controls">
          <p className="text-sm text-gray-600">
            Position: <span className="font-medium text-gray-900">{blindPosition}%</span>
          </p>

          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200" aria-hidden="true">
            <div className="h-full bg-primary-600 transition-all" style={{ width: `${blindPosition}%` }} />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => void runAction(() => onCommand(device.id, 'open'))}
              disabled={!isOnline || isPending || blindPosition >= 100}
              className="btn btn-primary disabled:cursor-not-allowed disabled:opacity-60"
              aria-label={`Open ${device.name}`}
            >
              Open
            </button>
            <button
              type="button"
              onClick={() => void runAction(() => onCommand(device.id, 'close'))}
              disabled={!isOnline || isPending || blindPosition <= 0}
              className="btn btn-secondary disabled:cursor-not-allowed disabled:opacity-60"
              aria-label={`Close ${device.name}`}
            >
              Close
            </button>
          </div>
        </section>
      )}

      <footer className="mt-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
        <span className="inline-flex items-center gap-1">
          <Clock3 className="h-3.5 w-3.5" aria-hidden="true" />
          Last seen {formatLastSeen(device.last_seen)}
        </span>
      </footer>
    </article>
  )
}
