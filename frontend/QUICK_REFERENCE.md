# Quick Reference Guide - Refactored Architecture

## 📖 Quick Links

- **Full Report**: [REFACTORING_REPORT.md](./REFACTORING_REPORT.md)
- **Implementation Guide**: [HYGIENE_DASHBOARD.md](./HYGIENE_DASHBOARD.md)

---

## 🗂️ File Organization

### Where to Put New Code

| Type | Location | Example |
|------|----------|---------|
| **Business Logic** | `utils/` | Sorting, filtering, calculations |
| **API Calls** | `services/` | REST, WebSocket, data fetching |
| **Reusable UI** | `components/common/` | Buttons, cards, spinners |
| **Domain UI** | `components/[domain]/` | Feature-specific components |
| **Pages** | `pages/` | Full page components |
| **Routes** | `config/routes.tsx` | Navigation configuration |
| **Data Hooks** | `hooks/` | Custom React hooks |
| **Types** | `types/` | TypeScript interfaces |

---

## 🔧 Common Tasks

### Add a New Page

1. Create page component in `pages/`
2. Add route to `config/routes.tsx`:
```typescript
{ path: '/mypage', element: MyPage }
```
3. Add nav item to `config/routes.tsx`:
```typescript
{ key: 'mypage', label: 'My Page', path: '/mypage' }
```

### Add Business Logic

1. Create function in `utils/`:
```typescript
export function myCalculation(data: Data[]): Result {
  // Pure function - no side effects
  return result
}
```
2. Import in component:
```typescript
import { myCalculation } from '../utils/myUtils'
```

### Add Reusable Component

1. Create in `components/common/`:
```typescript
export const MyComponent: React.FC<Props> = (props) => {
  return <div>...</div>
}
```
2. Export from index:
```typescript
export { MyComponent } from './MyComponent'
```

### Switch Data Source

```typescript
// Mock (default)
const data = useHygieneData()

// REST API
const data = useHygieneData({ sourceType: 'rest' })

// WebSocket
const data = useHygieneData({ sourceType: 'websocket' })
```

### Add New Data Service

1. Create service in `services/`:
```typescript
export class MyDataService {
  async fetchData(): Promise<Data[]> {
    // Implementation
  }
}
```

---

## 📦 Import Patterns

### Components
```typescript
// Common UI components
import { LoadingSpinner, ErrorMessage, StatCard } from '../components/common'

// Domain components
import { WorstPagesTable, HygieneStatsGrid } from '../components/hygiene'
```

### Utilities
```typescript
import { calculateHygieneStats, getWorstPages } from '../utils/hygieneUtils'
```

### Services
```typescript
import { hygieneService } from '../services/hygieneService'
```

### Types
```typescript
import { PageHygieneData, getScoreColor } from '../types/hygiene'
```

### Configuration
```typescript
import { NAV_ITEMS, ROUTES } from '../config/routes'
```

---

## 🎨 Component Patterns

### Page Component Template
```typescript
import React from 'react'
import { LoadingSpinner, ErrorMessage, SectionHeader } from '../components/common'
import { useMyData } from '../hooks/useMyData'
import { calculateStats } from '../utils/myUtils'

export const MyPage: React.FC = () => {
  const { data, loading, error, refetch } = useMyData()
  
  // Derive data using utils
  const stats = calculateStats(data)
  
  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error} onRetry={refetch} />
  
  return (
    <div className="space-y-6">
      <SectionHeader title="My Page" subtitle="Description" />
      {/* Content */}
    </div>
  )
}
```

### Reusable Component Template
```typescript
import React from 'react'

interface MyComponentProps {
  data: Data[]
  onAction?: (item: Data) => void
}

export const MyComponent: React.FC<MyComponentProps> = ({ data, onAction }) => {
  return (
    <div className="card p-4">
      {data.map(item => (
        <div key={item.id} onClick={() => onAction?.(item)}>
          {item.name}
        </div>
      ))}
    </div>
  )
}
```

### Service Template
```typescript
export class MyService {
  private config: Config
  
  constructor(config: Config) {
    this.config = config
  }
  
  async fetchData(): Promise<Data[]> {
    // Implementation
    const response = await fetch(this.config.apiUrl)
    return response.json()
  }
}
```

### Hook Template
```typescript
import { useState, useEffect } from 'react'
import { myService } from '../services/myService'

export function useMyData() {
  const [state, setState] = useState({
    data: [],
    loading: true,
    error: null
  })
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await myService.fetchData()
        setState({ data, loading: false, error: null })
      } catch (error) {
        setState(prev => ({ ...prev, loading: false, error: error.message }))
      }
    }
    fetchData()
  }, [])
  
  return state
}
```

---

## 🧪 Testing Patterns

### Test Utilities
```typescript
import { myFunction } from '../utils/myUtils'

describe('myFunction', () => {
  it('should return expected result', () => {
    const result = myFunction(input)
    expect(result).toEqual(expected)
  })
})
```

### Test Components
```typescript
import { render, screen } from '@testing-library/react'
import { MyComponent } from '../components/MyComponent'

describe('MyComponent', () => {
  it('should render data', () => {
    render(<MyComponent data={mockData} />)
    expect(screen.getByText('Test')).toBeInTheDocument()
  })
})
```

### Test Services
```typescript
import { MyService } from '../services/myService'

describe('MyService', () => {
  it('should fetch data', async () => {
    const service = new MyService(config)
    const data = await service.fetchData()
    expect(data).toBeDefined()
  })
})
```

---

## 🎯 Best Practices

### ✅ DO

- Extract business logic to utilities
- Use common components for UI
- Keep components under 100 lines
- Use TypeScript strictly
- Write pure functions where possible
- Document complex logic
- Use configuration over hardcoding

### ❌ DON'T

- Put business logic in components
- Duplicate UI code
- Hardcode configuration values
- Mix concerns in modules
- Write large monolithic components
- Skip type definitions
- Couple components tightly

---

## 🔍 Debugging Tips

### Check Data Flow
```
Component → Hook → Service → API
```

### Enable Service Logs
```typescript
hygieneService.updateConfig({
  sourceType: 'mock',
  mockDelay: 0 // Faster testing
})
```

### Test Individual Layers
```typescript
// Test utility independently
const result = calculateStats(testData)

// Test service independently
const data = await hygieneService.fetchData()

// Test component independently
<MyComponent data={mockData} />
```

---

## 📊 Architecture Layers

```
┌─────────────────────────────────────┐
│         PAGES (Composition)          │
├─────────────────────────────────────┤
│       COMPONENTS (Presentation)      │
├─────────────────────────────────────┤
│         HOOKS (State Logic)          │
├─────────────────────────────────────┤
│       SERVICES (Data Access)         │
├─────────────────────────────────────┤
│      UTILS (Business Logic)          │
├─────────────────────────────────────┤
│        TYPES (Type Definitions)      │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Commands

```bash
# Development
npm run dev

# Build
npm run build

# Type check
npx tsc --noEmit

# Lint
npx eslint src/
```

---

## 📱 Component Library

### Common Components

| Component | Usage |
|-----------|-------|
| `LoadingSpinner` | `<LoadingSpinner message="..." />` |
| `ErrorMessage` | `<ErrorMessage title="..." message="..." />` |
| `StatCard` | `<StatCard label="..." value={...} />` |
| `Badge` | `<Badge variant="success">Text</Badge>` |
| `SectionHeader` | `<SectionHeader title="..." subtitle="..." />` |
| `EmptyState` | `<EmptyState message="..." />` |

### Hygiene Components

| Component | Usage |
|-----------|-------|
| `WorstPagesTable` | `<WorstPagesTable pages={...} />` |
| `HygieneStatsGrid` | `<HygieneStatsGrid stats={...} />` |

---

## 🔗 Key Files

| File | Purpose | When to Edit |
|------|---------|--------------|
| `config/routes.tsx` | Navigation config | Add/remove routes |
| `services/hygieneService.ts` | Data fetching | Change API integration |
| `utils/hygieneUtils.ts` | Business logic | Add calculations |
| `components/common/index.tsx` | UI library | Add reusable UI |
| `hooks/useHygieneData.ts` | Data hook | Change data behavior |
| `types/hygiene.ts` | Type definitions | Add/modify types |

---

## 💡 Pro Tips

1. **Start with utilities** - Write business logic as pure functions first
2. **Use common components** - Check `components/common/` before creating new ones
3. **Follow the layers** - Data flows from services → hooks → components
4. **Keep it small** - Break large components into smaller ones
5. **Test utilities first** - Easiest to test, highest ROI
6. **Configuration over code** - Use `config/` for declarative setup
7. **Types everywhere** - Never use `any`, always define types

---

## 🆘 Need Help?

1. Check [REFACTORING_REPORT.md](./REFACTORING_REPORT.md) for detailed architecture
2. Look at existing code for patterns
3. Follow the templates above
4. Keep components focused and small

---

**Last Updated**: January 15, 2026
