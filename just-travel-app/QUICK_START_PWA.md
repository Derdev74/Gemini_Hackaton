# Just Travel PWA - Quick Start Guide

## 🚀 Start the Application

### Option 1: Development Mode
```bash
# Terminal 1: Backend
cd just-travel-app
uvicorn main:app --reload

# Terminal 2: Frontend
cd just-travel-app/frontend
npm run dev
```
Visit: http://localhost:3000

### Option 2: Production Mode
```bash
# Terminal 1: Backend
cd just-travel-app
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (Production Build)
cd just-travel-app/frontend
npm run build
npm start
```
Visit: http://localhost:3000

### Option 3: Docker (Full Stack)
```bash
cd just-travel-app
docker-compose up --build
```
Visit: http://localhost:3000

---

## 🧪 Testing the PWA Features

### 1. Test Manifest & Icons
1. Open Chrome DevTools (F12)
2. Go to **Application** tab
3. Click **Manifest** in sidebar
4. Verify:
   - ✓ Name: "Just Travel - AI-Powered Travel Planning"
   - ✓ 10 icons (72px to 512px)
   - ✓ Theme color: #FF9F43
   - ✓ Display: standalone

### 2. Test Service Worker
1. In DevTools **Application** tab
2. Click **Service Workers**
3. Verify:
   - ✓ Status: Activated and running
   - ✓ Source: /sw.js
   - ✓ Scope: /

### 3. Test Offline Mode
1. Plan a trip and save it
2. Open DevTools → **Network** tab
3. Check "**Offline**" checkbox
4. Navigate to "**My Trips**" in header
5. Verify:
   - ✓ Offline banner appears at top
   - ✓ Saved itinerary loads successfully
   - ✓ Can expand and view details

### 4. Test Install Prompt
1. Visit app (first time)
2. Wait 3 seconds
3. Verify:
   - ✓ Orange install prompt appears bottom-right
   - ✓ Shows "Install Just Travel" message
   - ✓ Has "Install" and "Not Now" buttons

### 5. Test Offline Save & Sync
1. Plan a trip while **online**
2. Go **offline** (DevTools → Network → Offline)
3. Click "**Save**" button
4. Verify message: "💾 Saved offline. Will sync when you're back online."
5. Go back **online** (uncheck Offline)
6. Verify message: "✅ All offline saves have been synced!"

### 6. Test Chat Disabled Offline
1. Go offline
2. Try typing in chat input
3. Verify:
   - ✓ Input is disabled
   - ✓ Placeholder: "You're offline - chat unavailable"
   - ✓ Send button shows 📡 icon

---

## 📱 Install on Mobile Devices

### iOS (Safari)
1. Open http://localhost:3000 in **Safari**
2. Tap **Share** button (⬆️)
3. Scroll down → "**Add to Home Screen**"
4. Tap "**Add**"
5. App icon appears on home screen
6. Open from home screen (runs in standalone mode)

### Android (Chrome)
1. Open app in **Chrome**
2. Automatic install prompt appears
3. Tap "**Install**"
4. OR tap menu (⋮) → "**Add to Home screen**"
5. App installs to home screen

### Desktop (Chrome, Edge, Brave)
1. Look for **install icon** (⊕) in address bar
2. Click it
3. Click "**Install**"
4. App opens in standalone window

---

## 🔍 Verify IndexedDB Storage

1. DevTools → **Application** tab
2. Expand **IndexedDB** in sidebar
3. Expand **just-travel-db**
4. Click **itineraries** object store
5. See saved itineraries with fields:
   - id
   - destination
   - summary
   - itinerary_data
   - creative_assets
   - saved_at
   - last_accessed

---

## 📊 Check Cache Storage

1. DevTools → **Application** tab
2. Click **Cache Storage**
3. Verify caches:
   - **next-static-resources** (JS, CSS)
   - **app-shell** (HTML pages)
   - **api-itineraries** (API responses)
   - **static-images** (icons, images)

---

## 🧹 Clear PWA Data (If Needed)

### Clear All PWA Data
1. DevTools → **Application** tab
2. Click "**Clear storage**" in sidebar
3. Check all boxes:
   - Local and session storage
   - IndexedDB
   - Cache storage
   - Service Workers
4. Click "**Clear site data**"

### Unregister Service Worker
1. DevTools → **Application** → **Service Workers**
2. Click "**Unregister**"

---

## 🐛 Troubleshooting

### Issue: Service Worker Not Registering
**Solution:**
- Ensure production build: `npm run build && npm start`
- Check console for errors
- Verify `/sw.js` exists in `public/` directory
- PWA is disabled in development mode by design

### Issue: Icons Not Loading
**Solution:**
- Check all 10 icon files exist in `public/icons/`
- Run: `cd frontend && ls -la public/icons/`
- Rebuild if missing: `cd ../.. && python generate_icons.py`

### Issue: Install Prompt Not Showing
**Solution:**
- Wait 3 seconds after page load
- Check localStorage: `localStorage.getItem('pwa-install-dismissed')`
- Clear if dismissed: `localStorage.removeItem('pwa-install-dismissed')`
- iOS Safari: No auto-prompt (manual only)

### Issue: Offline Mode Not Working
**Solution:**
- Verify service worker is active
- Check IndexedDB has data: DevTools → Application → IndexedDB
- Ensure you saved itineraries while online first
- Clear cache and try again

### Issue: Build Fails with TypeScript Errors
**Solution:**
```bash
cd frontend
npm install minimatch
npm run build
```

---

## 📈 Performance Tips

### Optimize Load Times
1. Enable **compression** on server (gzip/brotli)
2. Use **CDN** for static assets
3. Enable **HTTP/2**
4. Set proper **cache headers**

### Monitor Storage Usage
```javascript
// In browser console
navigator.storage.estimate().then(estimate => {
  console.log('Storage used:', estimate.usage);
  console.log('Storage quota:', estimate.quota);
  console.log('Percentage:', (estimate.usage / estimate.quota * 100).toFixed(2) + '%');
});
```

### Clear Old Itineraries
IndexedDB auto-cleans entries:
- **Older than 30 days:** Automatically deleted
- **Max 50 entries:** Oldest removed when exceeded

---

## 🎓 User Instructions

### How to Save Itineraries Offline
1. Plan a trip using the chat
2. Click "**Save**" button
3. Works online or offline!
4. If offline, syncs automatically when reconnected

### How to View Saved Trips
1. Click "**My Trips**" in navigation
2. See all saved itineraries
3. Works 100% offline
4. Click trip to expand and view details

### How to Delete Saved Trips
1. Go to "My Trips"
2. Click 🗑️ trash icon on any trip
3. Confirm deletion
4. Removed from IndexedDB and backend

---

## 🔒 Security Notes

- **HTTPS Required:** PWA requires HTTPS in production
- **Cookies:** Auth uses HttpOnly cookies (secure)
- **Origin Isolation:** IndexedDB per-origin only
- **Service Worker:** Same-origin policy enforced

---

## 📞 Need Help?

1. **Check Test Report:** `TEST_REPORT.md`
2. **Read Implementation Summary:** `PWA_IMPLEMENTATION_SUMMARY.md`
3. **Review Plan:** `/home/a_y_o/.claude/plans/iterative-toasting-stearns.md`
4. **Run Tests:** `cd frontend && node test-pwa.js`

---

**Quick Start Guide**
**Version:** 1.0
**Last Updated:** February 6, 2026
