import { useCallback, useMemo, useRef, useState, type TouchEvent } from 'react'
import { ArrowUpDown, Filter, RefreshCw } from 'lucide-react'
import { DeviceCard } from './DeviceCard'
import { useDevices } from '../hooks/useDevices'

type DeviceFilter = 'all' | 'lock' | 'light' | 'blinds'
type SortKey = 'name' | 'type' | 'last_seen'

const FILTER_OPTIONS: Array<{ id: DeviceFilter; label: string }> = [
  { id: 'all', label: 'All' },
  { id: 'lock', label: 'Locks' },
  { id: 'light', label: 'Lights' },
  { id: 'blinds', label: 'Blinds' },
]

const SORT_OPTIONS: Array<{ value: SortKey; label: string }> = [
  { value: 'name', label: 'Name' },
  { value: 'type', label: 'Type' },
  { value: 'last_seen', label: 'Last seen' },
]

export function DeviceGrid() {
  const { devices, toggleDevice, sendCommand, refresh, isLoading, error } = useDevices()
  const [filter, setFilter] = useState<DeviceFilter>('all')
  const [sortBy, setSortBy] = useState<SortKey>('name')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [pullDistance, setPullDistance] = useState(0)
  const touchStartYRef = useRef<number | null>(null)
  const isPullingRef = useRef(false)

  const visibleDevices = useMemo(() => {
    const filtered = devices.filter((device) => (filter === 'all' ? true : device.type === filter))

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name)
        case 'type':
          return a.type.localeCompare(b.type)
        case 'last_seen':
          return new Date(b.last_seen).getTime() - new Date(a.last_seen).getTime()
        default:
          return 0
      }
    })
  }, [devices, filter, sortBy])

  const triggerRefresh = useCallback(async () => {
    if (isRefreshing) {
      return
    }

    setIsRefreshing(true)
    try {
      await refresh()
    } finally {
      setIsRefreshing(false)
    }
  }, [isRefreshing, refresh])

  const handleTouchStart = (event: TouchEvent<HTMLElement>) => {
    if (window.scrollY > 0) {
      return
    }

    touchStartYRef.current = event.touches[0].clientY
  }

  const handleTouchMove = (event: TouchEvent<HTMLElement>) => {
    if (touchStartYRef.current === null || window.scrollY > 0) {
      return
    }

    const deltaY = event.touches[0].clientY - touchStartYRef.current
    if (deltaY <= 0) {
      return
    }

    isPullingRef.current = true
    const distance = Math.min(100, deltaY * 0.5)
    setPullDistance(distance)

    if (distance > 0) {
      event.preventDefault()
    }
  }

  const handleTouchEnd = () => {
    if (isPullingRef.current && pullDistance >= 70) {
      void triggerRefresh()
    }

    touchStartYRef.current = null
    isPullingRef.current = false
    setPullDistance(0)
  }

  return (
    <section
      className="space-y-4 animate-slide-in"
      aria-label="Device controls"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Devices</h2>
        <button
          type="button"
          onClick={() => void triggerRefresh()}
          className="btn btn-secondary text-sm"
          aria-label="Refresh devices"
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} aria-hidden="true" />
          Refresh
        </button>
      </div>

      <div
        className="overflow-hidden rounded-xl border border-gray-200 bg-white px-4 py-2 text-center text-xs text-gray-500 transition-all duration-200"
        style={{
          maxHeight: pullDistance > 0 || isRefreshing ? '56px' : '0px',
          opacity: pullDistance > 0 || isRefreshing ? 1 : 0,
          paddingTop: pullDistance > 0 || isRefreshing ? '8px' : '0px',
          paddingBottom: pullDistance > 0 || isRefreshing ? '8px' : '0px',
        }}
        aria-live="polite"
      >
        {isRefreshing ? 'Refreshing devices…' : pullDistance >= 70 ? 'Release to refresh' : 'Pull down to refresh'}
      </div>

      {error && (
        <div className="rounded-xl border border-danger/30 bg-danger/10 p-3 text-sm text-danger" role="alert">
          {error}
        </div>
      )}

      <div className="card p-3">
        <div className="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
          <Filter className="h-4 w-4" aria-hidden="true" />
          Filter by type
        </div>

        <div className="mb-3 flex gap-2 overflow-x-auto pb-1 scrollbar-hide" role="tablist" aria-label="Filter devices by type">
          {FILTER_OPTIONS.map((option) => (
            <button
              key={option.id}
              type="button"
              role="tab"
              aria-selected={filter === option.id}
              onClick={() => setFilter(option.id)}
              className={`rounded-lg px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
                filter === option.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        <label htmlFor="device-sort" className="mb-1 flex items-center gap-2 text-sm font-medium text-gray-700">
          <ArrowUpDown className="h-4 w-4" aria-hidden="true" />
          Sort devices
        </label>
        <select
          id="device-sort"
          value={sortBy}
          onChange={(event) => setSortBy(event.currentTarget.value as SortKey)}
          className="input py-2"
          aria-label="Sort devices"
        >
          {SORT_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading && devices.length === 0 ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4" aria-live="polite">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="card p-4">
              <div className="mb-3 h-4 w-2/3 animate-pulse rounded bg-gray-200" />
              <div className="mb-2 h-3 w-1/2 animate-pulse rounded bg-gray-100" />
              <div className="h-10 animate-pulse rounded bg-gray-200" />
            </div>
          ))}
        </div>
      ) : visibleDevices.length === 0 ? (
        <div className="card p-8 text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
            <Filter className="h-6 w-6 text-gray-400" aria-hidden="true" />
          </div>
          <h3 className="text-base font-semibold text-gray-900">No devices found</h3>
          <p className="mt-1 text-sm text-gray-500">Try another filter or refresh your devices.</p>
          <button type="button" onClick={() => setFilter('all')} className="btn btn-primary mt-4 text-sm">
            Show all devices
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4" aria-live="polite">
          {visibleDevices.map((device) => (
            <DeviceCard key={device.id} device={device} onToggle={toggleDevice} onCommand={sendCommand} />
          ))}
        </div>
      )}
    </section>
  )
}
