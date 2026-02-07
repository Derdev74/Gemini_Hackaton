/**
 * Root Layout Component
 * =====================
 *
 * Neo-brutalist design with yellow header and pink/yellow footer.
 * Preserves PWA functionality and auth providers.
 */

import type { Metadata, Viewport } from 'next'
import MeshBackground from '../components/MeshBackground'
import OfflineBanner from '../components/OfflineBanner'
import InstallPrompt from '../components/InstallPrompt'
import { Providers } from './providers'
import './globals.css'

/**
 * Viewport configuration for PWA
 */
export const viewport: Viewport = {
  themeColor: '#FFE135',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
}

/**
 * Metadata configuration for SEO and browser display
 */
export const metadata: Metadata = {
  title: 'Just Travel - AI-Powered Travel Planning',
  description: 'Plan your perfect trip with AI-powered recommendations for destinations, accommodations, and experiences tailored to your preferences.',
  keywords: ['travel', 'AI', 'trip planning', 'itinerary', 'vacation', 'travel agent'],
  authors: [{ name: 'Just Travel Team' }],
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Just Travel',
  },
  icons: {
    icon: [
      { url: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icons/icon-512x512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/icons/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
  },
  openGraph: {
    title: 'Just Travel - AI-Powered Travel Planning',
    description: 'Your personal AI travel assistant for the perfect trip',
    type: 'website',
  },
}

/**
 * Root layout component that wraps all pages
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen flex flex-col bg-background">
        <MeshBackground />
        <Providers>
          <OfflineBanner />
          <InstallPrompt />

          {/* Modern Dark Header */}
          <header className="sticky top-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10">
            <nav className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                {/* Logo */}
                <a href="/" className="no-underline">
                  <h1 className="text-2xl md:text-3xl font-mono font-bold tracking-tight">
                    <span className="text-white">JUST</span>
                    <span className="text-orange-400 ml-1">TRAVEL</span>
                  </h1>
                </a>

                {/* Navigation links */}
                <div className="hidden md:flex items-center gap-6">
                  <a
                    href="/my-itineraries"
                    className="font-mono font-bold uppercase text-sm text-white/70 no-underline hover:text-orange-400 transition-colors"
                  >
                    My Trips
                  </a>
                  <a
                    href="#plan"
                    className="bg-gradient-to-r from-orange-500 to-pink-500 text-white font-mono font-bold text-sm px-5 py-2.5 rounded-full hover:opacity-90 transition-all no-underline shadow-lg shadow-orange-500/25"
                  >
                    Start Planning
                  </a>
                </div>

                {/* Mobile menu button */}
                <button className="md:hidden p-2 border border-white/20 rounded-lg bg-white/5">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </nav>
          </header>

          {/* Main content area */}
          <main className="flex-1">
            {children}
          </main>

          {/* Modern Dark Footer */}
          <footer className="bg-black/90 backdrop-blur-xl text-white/70 border-t border-white/10">
            <div className="container mx-auto px-4 py-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Brand column */}
                <div>
                  <h2 className="text-xl font-mono font-bold mb-4">
                    <span className="text-white">JUST</span> <span className="text-orange-400">TRAVEL</span>
                  </h2>
                  <p className="text-sm text-white/50">
                    AI-powered travel planning that adapts to your unique preferences
                    and dietary requirements.
                  </p>
                </div>

                {/* Quick links */}
                <div>
                  <h3 className="text-lg font-mono font-bold mb-4 text-orange-400">
                    Quick Links
                  </h3>
                  <ul className="space-y-2 text-sm">
                    <li>
                      <a href="#plan" className="text-white/50 hover:text-orange-400 no-underline transition-colors">
                        Plan a Trip
                      </a>
                    </li>
                    <li>
                      <a href="/my-itineraries" className="text-white/50 hover:text-orange-400 no-underline transition-colors">
                        My Trips
                      </a>
                    </li>
                  </ul>
                </div>

                {/* Contact */}
                <div>
                  <h3 className="text-lg font-mono font-bold mb-4 text-orange-400">
                    Connect
                  </h3>
                  <p className="text-sm text-white/50 mb-2">
                    Built with AI Agents
                  </p>
                  <p className="text-sm text-white/30">
                    Powered by Gemini + FastAPI
                  </p>
                </div>
              </div>

              {/* Copyright */}
              <div className="mt-8 pt-4 border-t border-white/10 text-center text-sm text-white/30">
                <p>&copy; 2025 Just Travel. Built for the Hackathon.</p>
              </div>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  )
}
