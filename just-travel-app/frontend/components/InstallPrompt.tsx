/**
 * InstallPrompt - PWA installation prompt
 * Shows after 3 seconds if not previously dismissed
 * Note: iOS Safari doesn't support beforeinstallprompt (manual installation only)
 */

'use client'

import { useEffect, useState } from 'react'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export default function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [showPrompt, setShowPrompt] = useState(false)

  useEffect(() => {
    // Check if already dismissed
    const dismissed = localStorage.getItem('pwa-install-dismissed')
    if (dismissed) {
      return
    }

    // Listen for beforeinstallprompt event (Chrome, Edge, Android)
    const handleBeforeInstallPrompt = (e: Event) => {
      // Prevent default prompt
      e.preventDefault()

      // Store event for later use
      setDeferredPrompt(e as BeforeInstallPromptEvent)

      // Show prompt after 3 seconds
      setTimeout(() => {
        setShowPrompt(true)
      }, 3000)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [])

  const handleInstall = async () => {
    if (!deferredPrompt) {
      return
    }

    // Show native install prompt
    await deferredPrompt.prompt()

    // Wait for user choice
    const { outcome } = await deferredPrompt.userChoice

    console.log(`PWA install ${outcome}`)

    // Hide prompt
    setShowPrompt(false)
    setDeferredPrompt(null)

    // If accepted, mark as installed
    if (outcome === 'accepted') {
      localStorage.setItem('pwa-install-dismissed', 'true')
    }
  }

  const handleDismiss = () => {
    setShowPrompt(false)
    localStorage.setItem('pwa-install-dismissed', 'true')
  }

  // Don't render if no prompt or already dismissed
  if (!showPrompt || !deferredPrompt) {
    return null
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-sm">
      <div className="card-brutal bg-brutal-dark/95 backdrop-blur-md border-brutal-orange p-6 shadow-glow-orange">
        <div className="flex items-start gap-4">
          <div className="text-4xl">✈️</div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-brutal-orange mb-2">
              Install Just Travel
            </h3>
            <p className="text-sm text-brutal-text/80 mb-4">
              Add to home screen for quick access and offline itineraries!
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleInstall}
                className="btn-brutal bg-brutal-orange text-white px-4 py-2 text-sm font-bold hover:scale-105 transition-transform"
              >
                Install
              </button>
              <button
                onClick={handleDismiss}
                className="btn-brutal bg-brutal-dark border-brutal-text/30 text-brutal-text/70 px-4 py-2 text-sm hover:scale-105 transition-transform"
              >
                Not Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
