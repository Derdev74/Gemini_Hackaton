/**
 * OfflineBanner - Shows notification when offline
 * Appears as a fixed banner at the top of the screen
 */

'use client'

import { useOnlineStatus } from '../hooks/useOnlineStatus'

export default function OfflineBanner() {
  const isOnline = useOnlineStatus()

  // Don't render if online
  if (isOnline) {
    return null
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-brutal-orange/90 backdrop-blur-sm text-white py-3 px-4 text-center font-bold border-b-4 border-brutal-orange shadow-lg">
      <div className="flex items-center justify-center gap-2">
        <span className="text-2xl">📡</span>
        <span>You're offline. Some features are limited.</span>
      </div>
    </div>
  )
}
