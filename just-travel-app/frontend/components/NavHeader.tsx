'use client'

import { useState } from 'react'

export default function NavHeader() {
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 bg-brutal-yellow border-b-4 border-brutal-black">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <a href="/" className="no-underline">
            <h1 className="text-2xl md:text-3xl font-mono font-bold tracking-tight">
              <span className="text-brutal-black">JUST</span>
              <span className="bg-brutal-black text-brutal-white px-2 ml-1">TRAVEL</span>
            </h1>
          </a>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="font-mono font-bold uppercase text-sm hover:text-brutal-pink no-underline">
              Features
            </a>
            <a href="#how-it-works" className="font-mono font-bold uppercase text-sm hover:text-brutal-pink no-underline">
              How It Works
            </a>
            <a href="#chat" className="btn-brutal-pink text-sm">
              Start Planning
            </a>
          </div>

          {/* Hamburger */}
          <button
            className="md:hidden p-2 border-2 border-brutal-black bg-brutal-white"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="square"
                strokeWidth={3}
                d={mobileOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
              />
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileOpen && (
          <div className="md:hidden mt-4 flex flex-col gap-3 border-t-2 border-brutal-black pt-4">
            <a href="#features" onClick={() => setMobileOpen(false)} className="font-mono font-bold uppercase text-sm hover:text-brutal-pink no-underline">
              Features
            </a>
            <a href="#how-it-works" onClick={() => setMobileOpen(false)} className="font-mono font-bold uppercase text-sm hover:text-brutal-pink no-underline">
              How It Works
            </a>
            <a href="#chat" onClick={() => setMobileOpen(false)} className="btn-brutal-pink text-sm w-fit">
              Start Planning
            </a>
          </div>
        )}
      </nav>
    </header>
  )
}
