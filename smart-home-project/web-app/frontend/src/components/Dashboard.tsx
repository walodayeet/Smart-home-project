import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  AlertTriangle,
  Camera,
  CheckCircle2,
  Home,
  Lightbulb,
  Lock,
  RefreshCw,
  Shield,
  User,
  UserX,
} from 'lucide-react'
import { useStore } from '../store'
import { useSystemStatus } from '../hooks/useSystemStatus'
import { useDevices } from '../hooks/useDevices'
import { useCameras } from '../hooks/useCameras'
import { useRecognition } from '../hooks/useRecognition'

interface SnapshotCardState {
  src: string | null
  isLoading: boolean
  error: string | null
}

const EMPTY_SNAPSHOT: SnapshotCardState = {
  src: null,
  isLoading: false,
  error: null,
}

function extractSnapshotSource(payload: unknown): string | null {
  if (typeof payload === 'string') {
    return payload
  }

  if (!payload || typeof payload !== 'object') {
    return null
  }

  const data = payload as Record<string, unknown>
  const keys = ['image', 'snapshot', 'snapshot_url', 'image_url', 'url']

  for (const key of keys) {
    const value = data[key]
    if (typeof value === 'string' && value.trim().length > 0) {
      return value
    }
  }

  return null
}

function formatEventTime(timestamp: string): string {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return 'Unknown time'
  }

  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function getGreeting(): string {
  const hour = new Date().getHours()

  if (hour < 12) {
    return 'Good morning'
  }

  if (hour < 18) {
    return 'Good afternoon'
  }

  return 'Good evening'
}

export function Dashboard() {
  const devices = useStore((state) => state.devices)
  const recentEvents = useStore((state) => state.recentEvents)

  const { status, refresh: refreshStatus } = useSystemStatus()
  const { sendCommand, refresh: refreshDevices } = useDevices()
  const { cameras, refresh: refreshCameras, getSnapshot } = useCameras()
  const { fetchRecentEvents } = useRecognition()

  const [isActionLoading, setIsActionLoading] = useState(false)
  const [snapshots, setSnapshots] = useState<Record<string, SnapshotCardState>>({})

  const onlineDevices = useMemo(() => devices.filter((device) => device.online).length, [devices])
  const locks = useMemo(() => devices.filter((device) => device.type === 'lock'), [devices])
  const lights = useMemo(() => devices.filter((device) => device.type === 'light'), [devices])
  const camerasOnline = useMemo(() => {
    if (typeof status?.cameras_online === 'number') {
      return status.cameras_online
    }

    return cameras.filter((camera) => camera.status.toLowerCase().includes('online')).length
  }, [cameras, status?.cameras_online])

  const recentFiveEvents = useMemo(() => recentEvents.slice(0, 5), [recentEvents])

  const fetchThumbnail = useCallback(
    async (cameraId: string) => {
      setSnapshots((current) => ({
        ...current,
        [cameraId]: {
          ...(current[cameraId] ?? EMPTY_SNAPSHOT),
          isLoading: true,
          error: null,
        },
      }))

      try {
        const payload = await getSnapshot(cameraId)
        const src = extractSnapshotSource(payload)

        setSnapshots((current) => ({
          ...current,
          [cameraId]: {
            src,
            isLoading: false,
            error: src ? null : 'No image available',
          },
        }))
      } catch (error) {
        console.error('Failed to fetch camera snapshot', error)
        setSnapshots((current) => ({
          ...current,
          [cameraId]: {
            ...(current[cameraId] ?? EMPTY_SNAPSHOT),
            isLoading: false,
            error: 'Snapshot unavailable',
          },
        }))
      }
    },
    [getSnapshot],
  )

  useEffect(() => {
    void fetchRecentEvents(5)
  }, [fetchRecentEvents])

  useEffect(() => {
    const visibleCameras = cameras.slice(0, 4)
    visibleCameras.forEach((camera) => {
      void fetchThumbnail(camera.id)
    })
  }, [cameras, fetchThumbnail])

  const runQuickAction = async (action: () => Promise<void>) => {
    if (isActionLoading) {
      return
    }

    setIsActionLoading(true)
    try {
      await action()
    } finally {
      setIsActionLoading(false)
    }
  }

  const handleLockAll = async () => {
    await runQuickAction(async () => {
      const pendingLocks = locks.filter((lock) => !lock.state.toLowerCase().includes('locked'))
      await Promise.all(pendingLocks.map((lock) => sendCommand(lock.id, 'lock').catch((error) => console.error(error))))
      await refreshDevices()
    })
  }

  const handleLightsOff = async () => {
    await runQuickAction(async () => {
      const activeLights = lights.filter((light) => light.state.toLowerCase() === 'on')
      await Promise.all(
        activeLights.map((light) => sendCommand(light.id, 'turn_off').catch((error) => console.error(error))),
      )
      await refreshDevices()
    })
  }

  const handleRefreshAll = async () => {
    await runQuickAction(async () => {
      await Promise.all([refreshStatus(), refreshDevices(), refreshCameras(), fetchRecentEvents(5)])
    })
  }

  return (
    <section className="space-y-5 animate-slide-in" aria-label="Dashboard overview">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{getGreeting()}</h2>
          <p className="text-sm text-gray-500">Your home status is ready.</p>
        </div>

        <button
          type="button"
          onClick={() => void handleRefreshAll()}
          disabled={isActionLoading}
          className="btn btn-secondary text-sm disabled:cursor-not-allowed disabled:opacity-70"
          aria-label="Refresh dashboard data"
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isActionLoading ? 'animate-spin' : ''}`} aria-hidden="true" />
          Refresh
        </button>
      </div>

      <article className="card p-4" aria-label="System status card">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-700">
          <Shield className="h-4 w-4 text-primary-600" aria-hidden="true" />
          System status
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg bg-gray-50 p-3">
            <p className="text-xs text-gray-500">Devices online</p>
            <p className="mt-1 text-xl font-bold text-gray-900">
              {onlineDevices} <span className="text-sm font-medium text-gray-500">/ {devices.length}</span>
            </p>
          </div>
          <div className="rounded-lg bg-gray-50 p-3">
            <p className="text-xs text-gray-500">Cameras online</p>
            <p className="mt-1 text-xl font-bold text-gray-900">
              {camerasOnline} <span className="text-sm font-medium text-gray-500">/ {cameras.length}</span>
            </p>
          </div>
        </div>
      </article>

      <article className="card p-4" aria-label="Quick actions">
        <h3 className="mb-3 text-base font-semibold text-gray-900">Quick actions</h3>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <button
            type="button"
            onClick={() => void handleLockAll()}
            disabled={isActionLoading}
            className="btn btn-success disabled:cursor-not-allowed disabled:opacity-70"
            aria-label="Lock all doors"
          >
            <Lock className="mr-2 h-4 w-4" aria-hidden="true" />
            Lock all doors
          </button>
          <button
            type="button"
            onClick={() => void handleLightsOff()}
            disabled={isActionLoading}
            className="btn btn-secondary disabled:cursor-not-allowed disabled:opacity-70"
            aria-label="Turn off all lights"
          >
            <Lightbulb className="mr-2 h-4 w-4" aria-hidden="true" />
            Lights off
          </button>
        </div>
      </article>

      <article className="card p-4" aria-label="Recent recognition events">
        <h3 className="mb-3 text-base font-semibold text-gray-900">Recent recognition events</h3>

        {recentFiveEvents.length === 0 ? (
          <p className="text-sm text-gray-500">No recognition events yet.</p>
        ) : (
          <ul className="space-y-2">
            {recentFiveEvents.map((event) => (
              <li key={`${event.timestamp}-${event.status}-${event.person_name ?? 'unknown'}`} className="rounded-lg bg-gray-50 p-3">
                <div className="flex items-start gap-3">
                  {event.status === 'recognized' && <CheckCircle2 className="mt-0.5 h-4 w-4 text-success" aria-hidden="true" />}
                  {event.status === 'unknown' && <UserX className="mt-0.5 h-4 w-4 text-danger" aria-hidden="true" />}
                  {event.status === 'masked' && <AlertTriangle className="mt-0.5 h-4 w-4 text-warning" aria-hidden="true" />}
                  {event.status === 'error' && <AlertTriangle className="mt-0.5 h-4 w-4 text-danger" aria-hidden="true" />}

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-gray-900">
                      {event.person_name ?? (event.status === 'unknown' ? 'Unknown visitor' : 'System event')}
                    </p>
                    <p className="truncate text-xs text-gray-500">{event.message}</p>
                  </div>

                  <span className="text-xs text-gray-500">{formatEventTime(event.timestamp)}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </article>

      <article className="card p-4" aria-label="Camera snapshot thumbnails">
        <h3 className="mb-3 text-base font-semibold text-gray-900">Camera snapshots</h3>

        {cameras.length === 0 ? (
          <p className="text-sm text-gray-500">No cameras available.</p>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {cameras.slice(0, 4).map((camera) => {
              const snapshot = snapshots[camera.id] ?? EMPTY_SNAPSHOT

              return (
                <div key={camera.id} className="overflow-hidden rounded-lg border border-gray-100 bg-gray-50">
                  <div className="flex aspect-video items-center justify-center bg-gray-100">
                    {snapshot.isLoading && <RefreshCw className="h-5 w-5 animate-spin text-gray-400" aria-hidden="true" />}

                    {!snapshot.isLoading && snapshot.src && (
                      <img src={snapshot.src} alt={`Snapshot from ${camera.name}`} className="h-full w-full object-cover" />
                    )}

                    {!snapshot.isLoading && !snapshot.src && (
                      <div className="flex flex-col items-center gap-1 text-gray-400">
                        <Camera className="h-5 w-5" aria-hidden="true" />
                        <span className="text-[10px]">{snapshot.error ?? 'No image'}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center justify-between px-2 py-1.5">
                    <span className="truncate text-xs font-medium text-gray-700">{camera.name}</span>
                    <Home className="h-3.5 w-3.5 text-gray-400" aria-hidden="true" />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </article>

      <div className="rounded-xl border border-primary-100 bg-primary-50 p-3 text-sm text-primary-800">
        <div className="flex items-center gap-2 font-medium">
          <User className="h-4 w-4" aria-hidden="true" />
          Smart hint
        </div>
        <p className="mt-1">Use voice tab for quick commands like “Lock all doors” or “Turn off lights”.</p>
      </div>
    </section>
  )
}
