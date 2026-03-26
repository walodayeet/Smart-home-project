import { useCallback, useEffect, useMemo, useState } from 'react'
import { AlertCircle, Camera, MapPin, RefreshCw } from 'lucide-react'
import { useCameras } from '../hooks/useCameras'

interface SnapshotState {
  src: string | null
  isLoading: boolean
  error: string | null
  updatedAt: number | null
}

const EMPTY_SNAPSHOT: SnapshotState = {
  src: null,
  isLoading: false,
  error: null,
  updatedAt: null,
}

function extractSnapshotSource(payload: unknown): string | null {
  if (typeof payload === 'string') {
    return payload
  }

  if (!payload || typeof payload !== 'object') {
    return null
  }

  const snapshotObject = payload as Record<string, unknown>
  const keys = ['image', 'snapshot', 'snapshot_url', 'image_url', 'url']

  for (const key of keys) {
    const value = snapshotObject[key]
    if (typeof value === 'string' && value.trim().length > 0) {
      return value
    }
  }

  return null
}

function isOnlineStatus(status: string): boolean {
  const normalized = status.toLowerCase()
  return normalized === 'online' || normalized === 'active' || normalized === 'connected'
}

export function CameraView() {
  const { cameras, isLoading, error, refresh, getSnapshot } = useCameras()
  const [liveCameras, setLiveCameras] = useState<Record<string, boolean>>({})
  const [snapshots, setSnapshots] = useState<Record<string, SnapshotState>>({})

  const fetchSnapshot = useCallback(
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
            error: src ? null : 'No snapshot available',
            updatedAt: Date.now(),
          },
        }))
      } catch (snapshotError) {
        console.error(`Failed to load snapshot for camera ${cameraId}`, snapshotError)
        setSnapshots((current) => ({
          ...current,
          [cameraId]: {
            ...(current[cameraId] ?? EMPTY_SNAPSHOT),
            isLoading: false,
            error: 'Failed to load snapshot',
          },
        }))
      }
    },
    [getSnapshot],
  )

  const activeCameraIds = useMemo(
    () => Object.keys(liveCameras).filter((cameraId) => liveCameras[cameraId]),
    [liveCameras],
  )

  useEffect(() => {
    if (activeCameraIds.length === 0) {
      return
    }

    const intervalId = window.setInterval(() => {
      activeCameraIds.forEach((cameraId) => {
        void fetchSnapshot(cameraId)
      })
    }, 10000)

    return () => window.clearInterval(intervalId)
  }, [activeCameraIds, fetchSnapshot])

  const toggleLiveView = (cameraId: string) => {
    setLiveCameras((current) => {
      const shouldEnable = !(current[cameraId] ?? false)

      if (shouldEnable) {
        void fetchSnapshot(cameraId)
      }

      return {
        ...current,
        [cameraId]: shouldEnable,
      }
    })
  }

  return (
    <section className="space-y-4 animate-slide-in" aria-label="Camera monitoring view">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-gray-900">Camera Monitoring</h2>
        <button
          type="button"
          onClick={() => void refresh()}
          className="btn btn-secondary text-sm"
          aria-label="Refresh camera list"
        >
          <RefreshCw className="mr-2 h-4 w-4" aria-hidden="true" />
          Refresh Cameras
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-3 text-sm text-danger" role="alert">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3" aria-live="polite">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="card p-4">
              <div className="mb-3 h-40 animate-pulse rounded-lg bg-gray-200" />
              <div className="mb-2 h-4 w-2/3 animate-pulse rounded bg-gray-200" />
              <div className="h-3 w-1/2 animate-pulse rounded bg-gray-100" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cameras.map((camera) => {
            const live = liveCameras[camera.id] ?? false
            const snapshot = snapshots[camera.id] ?? EMPTY_SNAPSHOT
            const isOnline = isOnlineStatus(camera.status)

            return (
              <article key={camera.id} className="card p-4" aria-label={`Camera ${camera.name}`}>
                <div className="mb-3 flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{camera.name}</h3>
                    <div className="mt-1 flex items-center gap-1 text-sm text-gray-500">
                      <MapPin className="h-4 w-4" aria-hidden="true" />
                      <span>{camera.location}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={isOnline ? 'status-dot-online' : 'status-dot-offline'}
                      aria-label={isOnline ? 'Online' : 'Offline'}
                    />
                    <span className="text-xs font-medium text-gray-600">{camera.status}</span>
                  </div>
                </div>

                <div className="mb-3 overflow-hidden rounded-lg bg-gray-100">
                  {!live && (
                    <div className="flex h-40 items-center justify-center px-4 text-center text-sm text-gray-500">
                      Tap “View Live” to load latest snapshot
                    </div>
                  )}

                  {live && snapshot.isLoading && (
                    <div className="h-40 animate-pulse bg-gray-200" aria-label="Loading camera snapshot" />
                  )}

                  {live && !snapshot.isLoading && snapshot.src && (
                    <img
                      src={snapshot.src}
                      alt={`Live snapshot from ${camera.name}`}
                      className="h-40 w-full object-cover"
                    />
                  )}

                  {live && !snapshot.isLoading && snapshot.error && (
                    <div className="flex h-40 flex-col items-center justify-center gap-2 px-3 text-center text-sm text-danger">
                      <AlertCircle className="h-5 w-5" aria-hidden="true" />
                      <span>{snapshot.error}</span>
                    </div>
                  )}
                </div>

                <div className="mb-2 flex items-center justify-between text-xs text-gray-500">
                  <span>
                    {camera.resolution} · {camera.fps} FPS
                  </span>
                  <span>
                    {snapshot.updatedAt
                      ? `Updated ${new Date(snapshot.updatedAt).toLocaleTimeString()}`
                      : 'Not loaded'}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={() => toggleLiveView(camera.id)}
                  className="btn btn-primary w-full"
                  aria-pressed={live}
                  aria-label={live ? `Stop live updates for ${camera.name}` : `View live snapshot for ${camera.name}`}
                >
                  <Camera className="mr-2 h-4 w-4" aria-hidden="true" />
                  {live ? 'Stop Live' : 'View Live'}
                </button>
              </article>
            )
          })}
        </div>
      )}

      {!isLoading && cameras.length === 0 && (
        <div className="card p-6 text-center text-sm text-gray-600">No cameras available.</div>
      )}
    </section>
  )
}
