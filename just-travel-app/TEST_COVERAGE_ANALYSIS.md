# Just Travel - Test Coverage Analysis & Recommendations

## 📊 Current Test Coverage

### Summary
- **Total Tests:** 52
- **Frontend Tests:** 17 (PWA features)
- **Backend Tests:** 35 (agents, tools, optimizations)
- **Status:** ✅ Basic coverage exists, but **critical gaps** remain

---

## ✅ What's Currently Tested

### Frontend (17 tests)
**File:** `frontend/test-pwa.js`

1. ✅ Manifest file exists and valid JSON
2. ✅ All 10 icon files exist
3. ✅ Service worker file exists
4. ✅ Workbox runtime exists
5. ✅ Offline storage module exists
6. ✅ Sync manager module exists
7. ✅ Online status hook exists
8. ✅ Offline banner component exists
9. ✅ Install prompt component exists
10. ✅ My Itineraries page exists
11. ✅ Offline fallback page exists
12. ✅ Layout has PWA configuration
13. ✅ Main page has offline support
14. ✅ NavHeader has My Trips link
15. ✅ next.config has PWA configuration
16-17. Additional syntax checks

**Coverage:** ~60% (Static file checks, no runtime/behavior testing)

### Backend (35 tests)

**File:** `tests/verify_new_features.py` (22 tests)
- ✅ Profiler greeting short-circuit
- ✅ Password validation rules
- ✅ WeatherTools mock/advisory/fallback
- ✅ Guest-mode get_optional_user contract
- ✅ Preference panel integration

**File:** `tests/verify_booking.py` (2 tests)
- ✅ Booking tools mock detection
- ✅ Booking API fallback

**File:** `tests/verify_creative.py` (2 tests)
- ✅ Creative director imports
- ✅ Image generation mock

**File:** `tests/verify_trend_loop.py` (1 test)
- ✅ TrendSpotter mock detection

**File:** `test_optimizations.py` (8 tests)
- ✅ Phase 1-3 imports
- ✅ Weather/itinerary cache
- ✅ Database schema
- ✅ API endpoints
- ✅ Redis connection (optional)

**Coverage:** ~40% (Module imports, basic functionality, no E2E)

---

## ❌ Critical Gaps (High Priority)

### 1. **API Endpoint Tests** 🔴 CRITICAL
**Missing:**
- `/api/chat` - Main agent workflow
- `/api/itinerary/save` - Save functionality
- `/api/itinerary/list` - NEW endpoint (not tested!)
- `/api/media-status/{id}` - Background tasks
- `/api/auth/*` - All auth endpoints
- `/api/upload` - File uploads

**Why Critical:**
- No integration tests for API
- Breaking changes won't be caught
- Response format changes undetected

**Recommended:**
```python
# tests/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient

def test_chat_endpoint_requires_preferences():
    response = client.post("/api/chat", json={
        "message": "Plan a trip",
        "preferences": {}
    })
    assert response.status_code == 200
    assert "message" in response.json()

def test_itinerary_list_requires_auth():
    response = client.get("/api/itinerary/list")
    assert response.status_code == 401

def test_save_itinerary_offline_support():
    # Test with media_task_id
    response = client.post("/api/itinerary/save", json={
        "destination": "Paris",
        "summary": "Test trip",
        "itinerary_data": {},
        "creative_assets": {},
        "media_task_id": "test-task-123"
    })
    assert response.status_code == 200
    assert response.json()["id"] is not None
```

### 2. **Offline/Online Behavior** 🔴 CRITICAL
**Missing:**
- IndexedDB save/retrieve operations
- Service worker caching behavior
- Offline → Online sync flow
- Background task polling
- Queue management

**Why Critical:**
- Core PWA functionality untested
- Sync failures won't be detected
- Data loss risks

**Recommended:**
```javascript
// frontend/__tests__/offline-storage.test.js
import { offlineStorage } from '../lib/offline-storage'

describe('OfflineStorage', () => {
  beforeEach(async () => {
    await offlineStorage.clearAll()
  })

  test('saves itinerary to IndexedDB', async () => {
    await offlineStorage.saveItinerary({
      id: 'test-1',
      destination: 'Tokyo',
      summary: 'Test trip',
      itinerary_data: {},
      creative_assets: {}
    })

    const itineraries = await offlineStorage.getAllItineraries()
    expect(itineraries).toHaveLength(1)
    expect(itineraries[0].destination).toBe('Tokyo')
  })

  test('auto-cleanup old entries', async () => {
    // Save 51 itineraries (max is 50)
    for (let i = 0; i < 51; i++) {
      await offlineStorage.saveItinerary({
        id: `test-${i}`,
        destination: `City ${i}`,
        summary: 'Test',
        itinerary_data: {},
        creative_assets: {}
      })
    }

    const all = await offlineStorage.getAllItineraries()
    expect(all).toHaveLength(50) // Oldest removed
  })
})
```

### 3. **Authentication Flow** 🟡 IMPORTANT
**Missing:**
- Login/register endpoints
- JWT token validation
- Cookie management
- Google OAuth flow
- Session expiration
- Guest mode behavior

**Recommended:**
```python
# tests/test_auth.py
def test_register_requires_strong_password():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "weak",  # Should fail
        "full_name": "Test User"
    })
    assert response.status_code == 422

def test_login_sets_cookies():
    # Register first
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "StrongP@ss123",
        "full_name": "Test"
    })

    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "StrongP@ss123"
    })

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

def test_guest_mode_allows_chat():
    response = client.post("/api/chat", json={
        "message": "Plan a trip",
        "preferences": {}
    })
    # Should work without auth
    assert response.status_code == 200
```

### 4. **Database Operations** 🟡 IMPORTANT
**Missing:**
- CRUD operations for Itinerary
- User relationship integrity
- Media fields (poster_url, video_url, media_status)
- Concurrent access handling
- Database migrations

**Recommended:**
```python
# tests/test_database.py
import pytest
from database import Itinerary, User
from sqlmodel import Session

@pytest.fixture
async def test_user(session):
    user = User(email="test@example.com", hashed_password="...")
    session.add(user)
    await session.commit()
    return user

async def test_save_itinerary_with_media_fields(session, test_user):
    itinerary = Itinerary(
        user_id=test_user.id,
        destination="Paris",
        summary="Test",
        data={},
        creative_assets={},
        media_task_id="task-123",
        media_status="generating"
    )
    session.add(itinerary)
    await session.commit()

    assert itinerary.id is not None
    assert itinerary.media_status == "generating"

async def test_list_user_itineraries(session, test_user):
    # Create 3 itineraries
    for i in range(3):
        itin = Itinerary(
            user_id=test_user.id,
            destination=f"City {i}",
            summary="Test",
            data={},
            creative_assets={}
        )
        session.add(itin)
    await session.commit()

    # Query
    result = await session.execute(
        select(Itinerary).where(Itinerary.user_id == test_user.id)
    )
    itineraries = result.scalars().all()

    assert len(itineraries) == 3
```

---

## ⚠️ Medium Priority Gaps

### 5. **Agent Workflow E2E** 🟡
**Missing:**
- Full 6-agent pipeline test
- Agent communication validation
- Error handling between agents
- Timeout behavior
- Fallback mechanisms

**Recommended:**
```python
# tests/test_agent_workflow.py
async def test_full_agent_pipeline():
    """Test Profiler → Research → Optimizer → Creative"""
    manager = AntigravityAgentManager()

    response = await manager.orchestrate(
        message="Plan a 3-day trip to Tokyo",
        preferences={"budget_per_day_usd": 200}
    )

    assert response.status == "success"
    assert response.data["itinerary"] is not None
    assert "destination" in response.data["itinerary"]
    assert response.creative is not None
```

### 6. **Background Tasks (Redis)** 🟡
**Missing:**
- Task creation and storage
- Status updates
- Task expiration (TTL)
- Failed task handling
- Concurrent task management

**Recommended:**
```python
# tests/test_background_tasks.py
import asyncio
from tasks import start_background_task, get_task_status

async def test_media_generation_task():
    task_id = "test-task-123"

    # Start background task
    start_background_task(task_id, {
        "destination": "Paris",
        "summary": "Test"
    })

    # Wait a bit
    await asyncio.sleep(2)

    # Check status
    status = await get_task_status(task_id)
    assert status is not None
    assert status["status"] in ["generating", "completed"]

async def test_task_ttl_expiration():
    """Tasks should expire after 1 hour"""
    # Implementation depends on Redis mock
    pass
```

### 7. **Frontend Component Tests** 🟡
**Missing:**
- Component rendering (React Testing Library)
- User interactions (click, type, submit)
- State management
- Hook behavior
- Error boundaries

**Recommended:**
```javascript
// frontend/__tests__/components/OfflineBanner.test.tsx
import { render, screen } from '@testing-library/react'
import OfflineBanner from '../components/OfflineBanner'

// Mock useOnlineStatus hook
jest.mock('../hooks/useOnlineStatus', () => ({
  useOnlineStatus: jest.fn()
}))

test('shows banner when offline', () => {
  useOnlineStatus.mockReturnValue(false)
  render(<OfflineBanner />)

  expect(screen.getByText(/you're offline/i)).toBeInTheDocument()
})

test('hides banner when online', () => {
  useOnlineStatus.mockReturnValue(true)
  const { container } = render(<OfflineBanner />)

  expect(container.firstChild).toBeNull()
})
```

---

## ℹ️ Low Priority (Nice to Have)

### 8. **Performance Tests**
- Response time benchmarks
- Load testing
- Memory usage monitoring
- Cache hit rates

### 9. **Security Tests**
- SQL injection attempts
- XSS prevention
- CSRF protection
- Rate limiting validation

### 10. **Accessibility Tests**
- ARIA labels
- Keyboard navigation
- Screen reader compatibility

---

## 📋 Recommended Test Suite Structure

```
just-travel-app/
├── frontend/
│   ├── __tests__/
│   │   ├── components/
│   │   │   ├── OfflineBanner.test.tsx
│   │   │   ├── InstallPrompt.test.tsx
│   │   │   └── NavHeader.test.tsx
│   │   ├── lib/
│   │   │   ├── offline-storage.test.ts
│   │   │   └── sync-manager.test.ts
│   │   ├── hooks/
│   │   │   └── useOnlineStatus.test.ts
│   │   └── pages/
│   │       ├── page.test.tsx
│   │       └── my-itineraries.test.tsx
│   ├── test-pwa.js (existing - keep)
│   └── jest.config.js (new)
│
├── tests/
│   ├── test_api_endpoints.py (NEW - CRITICAL)
│   ├── test_auth.py (NEW - CRITICAL)
│   ├── test_database.py (NEW - IMPORTANT)
│   ├── test_agent_workflow.py (NEW)
│   ├── test_background_tasks.py (NEW)
│   ├── verify_new_features.py (existing - keep)
│   ├── verify_booking.py (existing - keep)
│   ├── verify_creative.py (existing - keep)
│   └── verify_trend_loop.py (existing - keep)
│
├── test_optimizations.py (existing - keep)
├── pytest.ini (new)
└── conftest.py (new - shared fixtures)
```

---

## 🎯 Priority Action Plan

### Phase 1: Critical (Do First) 🔴
1. **API Endpoint Tests** (1-2 hours)
   - Test `/api/itinerary/list` (NEW endpoint!)
   - Test `/api/chat` basic flow
   - Test `/api/auth/*` endpoints

2. **Database Tests** (1 hour)
   - Test media fields
   - Test user relationships
   - Test list queries

### Phase 2: Important (Do Soon) 🟡
3. **Offline Storage Tests** (1-2 hours)
   - IndexedDB operations
   - Sync manager queue
   - Auto-cleanup

4. **Auth Flow Tests** (1 hour)
   - Login/register
   - Cookie management
   - Guest mode

### Phase 3: Nice to Have 🟢
5. **Component Tests** (2-3 hours)
   - React Testing Library setup
   - Component rendering
   - User interactions

6. **E2E Tests** (3-4 hours)
   - Full user workflows
   - Offline→Online transitions
   - Agent pipeline

---

## 🛠️ Setup Instructions

### Frontend Testing (Jest + React Testing Library)

```bash
cd frontend

# Install dependencies
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event jest-environment-jsdom

# Create jest.config.js
cat > jest.config.js << 'EOF'
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
}

module.exports = createJestConfig(customJestConfig)
EOF

# Create jest.setup.js
echo "import '@testing-library/jest-dom'" > jest.setup.js

# Add test script to package.json
npm set-script test "jest"
npm set-script test:watch "jest --watch"
```

### Backend Testing (pytest)

```bash
cd just-travel-app

# Already have pytest, add fixtures
cat > conftest.py << 'EOF'
import pytest
import asyncio
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    # In-memory test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def session(test_db):
    async with AsyncSession(test_db) as session:
        yield session
        await session.rollback()
EOF
```

---

## 📊 Coverage Goals

| Category | Current | Target | Priority |
|----------|---------|--------|----------|
| **API Endpoints** | 0% | 80% | 🔴 Critical |
| **Database** | 20% | 70% | 🔴 Critical |
| **Auth Flow** | 0% | 80% | 🟡 Important |
| **Offline Features** | 30% | 90% | 🟡 Important |
| **Components** | 0% | 60% | 🟢 Nice to have |
| **E2E Workflows** | 0% | 40% | 🟢 Nice to have |
| **Overall** | ~35% | **70%** | Target |

---

## ✅ My Recommendation

**TL;DR:** Yes, you should add more tests, but **focus on critical gaps first**.

### Immediate Action (2-3 hours):
1. ✅ **API endpoint tests** - Test the NEW `/api/itinerary/list` endpoint
2. ✅ **Database tests** - Verify media fields work correctly
3. ✅ **Auth tests** - Guest mode and save requiring auth

### This Week (5-10 hours):
4. ✅ **Offline storage tests** - IndexedDB operations are core PWA
5. ✅ **Sync manager tests** - Ensure no data loss
6. ✅ **Component tests** - At least critical components

### Why These Matter:
- **API tests** catch breaking changes before deployment
- **Database tests** prevent data corruption
- **Offline tests** are your PWA's core value prop
- **Auth tests** prevent security vulnerabilities

---

**Bottom Line:** With 52 tests, you have decent coverage of static checks and imports, but you're missing **runtime behavior tests** for your most critical features. I recommend adding ~20-30 more tests focusing on API endpoints, database operations, and offline functionality.

*Analysis completed: February 6, 2026*
*Current coverage: ~35% | Recommended target: 70%*
