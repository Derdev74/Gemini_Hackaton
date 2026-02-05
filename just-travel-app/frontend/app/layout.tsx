/**
 * Root Layout Component
 * =====================
 *
 * This is the root layout for the Just Travel application.
 * It wraps all pages and provides common structure including:
 * - HTML document setup
 * - Global styles
 * - Meta information
 * - Common UI elements (header, footer if needed)
 */

import type { Metadata } from 'next'
import NavHeader from '../components/NavHeader'
import './globals.css'

/**
 * Metadata configuration for SEO and browser display
 */
export const metadata: Metadata = {
  title: 'Just Travel - AI-Powered Travel Planning',
  description: 'Plan your perfect trip with AI-powered recommendations for destinations, accommodations, and experiences tailored to your preferences.',
  keywords: ['travel', 'AI', 'trip planning', 'itinerary', 'vacation', 'travel agent'],
  authors: [{ name: 'Just Travel Team' }],
  openGraph: {
    title: 'Just Travel - AI-Powered Travel Planning',
    description: 'Your personal AI travel assistant for the perfect trip',
    type: 'website',
  },
}

/**
 * Root layout component that wraps all pages
 *
 * @param children - Child components/pages to render
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen flex flex-col">
        <NavHeader />

        {/* Main content area */}
        <main className="flex-1">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-brutal-black text-brutal-white border-t-4 border-brutal-yellow">
          <div className="container mx-auto px-4 py-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Brand column */}
              <div>
                <h2 className="text-xl font-mono font-bold mb-4">
                  <span className="text-brutal-yellow">JUST</span> TRAVEL
                </h2>
                <p className="text-sm opacity-80">
                  AI-powered travel planning that adapts to your unique preferences
                  and dietary requirements.
                </p>
              </div>

              {/* Quick links */}
              <div>
                <h3 className="text-lg font-mono font-bold mb-4 text-brutal-yellow">
                  Quick Links
                </h3>
                <ul className="space-y-2 text-sm">
                  <li>
                    <a href="#" className="opacity-80 hover:opacity-100 hover:text-brutal-yellow no-underline">
                      Plan a Trip
                    </a>
                  </li>
                  <li>
                    <a href="#" className="opacity-80 hover:opacity-100 hover:text-brutal-yellow no-underline">
                      Browse Destinations
                    </a>
                  </li>
                  <li>
                    <a href="#" className="opacity-80 hover:opacity-100 hover:text-brutal-yellow no-underline">
                      Travel Tips
                    </a>
                  </li>
                </ul>
              </div>

              {/* Contact */}
              <div>
                <h3 className="text-lg font-mono font-bold mb-4 text-brutal-yellow">
                  Connect
                </h3>
                <p className="text-sm opacity-80 mb-2">
                  Built with AI Agents
                </p>
                <p className="text-sm opacity-60">
                  Phase 1 - Foundation
                </p>
              </div>
            </div>

            {/* Copyright */}
            <div className="mt-8 pt-4 border-t border-brutal-white/20 text-center text-sm opacity-60">
              <p>&copy; 2024 Just Travel. Built for the Hackathon.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
