# How to Run Backend and Frontend

Complete guide for running the Autonomous QA Inspection Platform.

---

## 🚀 Quick Start (5 minutes)

### Terminal 1: Backend (Python)
```bash
cd Subdomain_Enumeration_tool
pip install -r requirements.txt
python main.py --help
```

### Terminal 2: Frontend (React)
```bash
cd Subdomain_Enumeration_tool/frontend
npm install
npm run dev
```

Then open:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000 (when running)

---

## 📋 Detailed Setup

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** (includes npm)
- **Git**

### Verify Versions

```powershell
# Check Python
python --version          # Should be 3.8+
pip --version            # Should be 20.0+

# Check Node & npm
node --version           # Should be 16+
npm --version            # Should be 8+
```

---

## 🔧 Backend Setup

### Step 1: Install Python Dependencies

```bash
# Navigate to project root
cd Subdomain_Enumeration_tool

# Install requirements
pip install -r requirements.txt
```

**What's Installed:**
- httpx - HTTP client
- BeautifulSoup4 - HTML parsing
- Playwright - Browser automation for QA
- requests - HTTP library

### Step 2: View Available Commands

```bash
python main.py --help
```

**Output:**
```
usage: main.py [-h] [-u URL] [-d DEPTH] [-m MODE] [--wayback] [--bruteforce] [--validate-ssl]

Autonomous QA Web Inspection Tool

options:
  -h, --help                    Show this help message
  -u URL, --url URL             Target URL (required)
  -d DEPTH, --depth DEPTH       Crawl depth (default: 2)
  -m MODE, --mode MODE          Mode: crawl|qc|full (default: crawl)
  --wayback                     Enable Wayback Machine
  --bruteforce                  Enable brute force mode
  --validate-ssl                Validate SSL certificates
```

### Step 3: Run Backend

```bash
# Simple crawl
python main.py -u https://example.com

# Full QA inspection
python main.py -u https://example.com -m full

# With Wayback Machine
python main.py -u https://example.com --wayback

# Brute force paths
python main.py -u https://example.com --bruteforce

# Full inspection with all features
python main.py -u https://example.com -m full --wayback --bruteforce
```

### Backend Architecture

```
Backend (Python)
├── main.py              ← Entry point
├── cli.py               ← CLI argument parser
├── core/
│   ├── crawler.py       ← Live crawling
│   ├── js_parser.py     ← JavaScript analysis
│   ├── wayback.py       ← Wayback Machine
│   ├── bruteforce.py    ← Path brute force
│   ├── validator.py     ← URL validation
│   └── utils.py         ← Utilities
└── qa_engine/
    ├── main.py          ← QA orchestrator
    ├── browser_analyzer.py
    ├── structure_detector.py
    ├── page_classifier.py
    ├── issue_detector.py
    ├── graph_builder.py
    └── scorer.py
```

---

## 🎨 Frontend Setup

### Step 1: Install Node Dependencies

```bash
# Navigate to frontend
cd frontend

# Install npm packages
npm install
```

**What's Installed:**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- TailwindCSS - Styling
- React Router - Navigation
- Recharts - Charting
- ReactFlow - Graph visualization

### Step 2: View Available Commands

```bash
npm run
```

**Available Scripts:**
- `npm run dev` - Start dev server
- `npm run build` - Production build
- `npm run preview` - Preview production build

### Step 3: Run Frontend

```bash
# Start development server
npm run dev
```

**Output:**
```
  VITE v5.4.21  ready in 592 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 4: Access Frontend

Open browser and navigate to:
- **http://localhost:5173**

### Frontend Architecture

```
Frontend (React + TypeScript)
├── src/
│   ├── App.tsx                 ← Main app
│   ├── main.tsx                ← Entry point
│   ├── config/
│   │   └── routes.tsx          ← Routing config
│   ├── services/
│   │   └── hygieneService.ts   ← Data layer
│   ├── utils/
│   │   └── hygieneUtils.ts     ← Business logic
│   ├── components/
│   │   ├── common/             ← Reusable UI
│   │   └── hygiene/            ← Domain components
│   ├── pages/
│   │   ├── HygieneDashboard.tsx
│   │   ├── PageDetailView.tsx
│   │   └── ...
│   ├── hooks/
│   │   └── useHygieneData.ts   ← Data hook
│   ├── types/
│   │   └── hygiene.ts          ← Types
│   └── data/
│       └── mock.ts             ← Mock data
├── public/
├── index.html
└── package.json
```

---

## 🔗 Integration (Backend + Frontend)

### Current Status
- **Frontend**: Using mock data
- **Backend**: Standalone CLI tool

### To Connect Frontend to Backend API

1. **Start Backend with API Mode** (Future Enhancement)
   ```bash
   python main.py --api --port 8000
   ```

2. **Update Service Configuration**
   ```typescript
   // src/hooks/useHygieneData.ts
   const { pages } = useHygieneData({
     sourceType: 'rest',  // Change from 'mock' to 'rest'
     apiBaseUrl: 'http://localhost:8000'
   })
   ```

3. **Start Frontend**
   ```bash
   npm run dev
   ```

---

## 📊 Running Both Simultaneously

### Recommended Setup: 2 Terminals

**Terminal 1: Backend**
```bash
cd Subdomain_Enumeration_tool
python main.py -u https://example.com -m full
```

**Terminal 2: Frontend**
```bash
cd Subdomain_Enumeration_tool/frontend
npm run dev
```

### Alternative: 3 Terminals (Better)

**Terminal 1: Backend API Server**
```bash
cd Subdomain_Enumeration_tool
python -m http.server 8000  # Simple server for mock data
```

**Terminal 2: Frontend Dev Server**
```bash
cd Subdomain_Enumeration_tool/frontend
npm run dev
```

**Terminal 3: Run Commands**
```bash
cd Subdomain_Enumeration_tool
python main.py --help
python main.py -u https://example.com -m full
```

---

## 🧪 Testing

### Backend Testing

```bash
# Run test script
python test_tool.py

# Or manually test
python main.py -u https://httpbin.org -d 1
```

### Frontend Testing

```bash
# Navigate to frontend
cd frontend

# Start dev server
npm run dev

# Open http://localhost:5173 in browser
# Test navigation, check console for errors
```

---

## 📱 Access Points

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:5173 | UI Dashboard |
| **Backend API** | http://localhost:8000 | Data & operations |
| **Mock Data** | Embedded | Frontend mock data |

---

## 🛠️ Troubleshooting

### Backend Issues

**Python not found**
```bash
# Add to PATH or use full path
C:\Python311\python.exe main.py --help
```

**Missing dependencies**
```bash
pip install -r requirements.txt --upgrade
```

**Port already in use**
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Frontend Issues

**npm not found**
```bash
# Install Node.js from https://nodejs.org/
# Then retry: npm install
```

**Node modules corrupted**
```bash
# Clean install
rm -r node_modules package-lock.json
npm install
```

**Port 5173 already in use**
```bash
# Use different port
npm run dev -- --port 3000
```

---

## 📈 Development Workflow

### Making Changes

1. **Backend Changes**
   - Edit files in `core/` or `qa_engine/`
   - Run: `python main.py ...`
   - No build needed (Python)

2. **Frontend Changes**
   - Edit files in `src/`
   - Dev server auto-reloads
   - View changes at http://localhost:5173

### Building for Production

**Frontend Build**
```bash
cd frontend
npm run build

# Output: frontend/dist/
# To preview: npm run preview
```

**Backend Packaging**
```bash
# Create executable (future enhancement)
# pyinstaller main.py --onefile
```

---

## 📚 Configuration Files

### Backend
- `requirements.txt` - Python dependencies
- `main.py` - Entry point
- `cli.py` - Command-line interface

### Frontend
- `package.json` - Node dependencies
- `vite.config.ts` - Build configuration
- `tailwind.config.cjs` - Styling config
- `tsconfig.json` - TypeScript config

---

## 🚀 Performance Tips

### Backend
- Use `--depth 1` for faster crawling
- Omit `--wayback` if not needed
- Use `--validate-ssl` for HTTPS only sites

### Frontend
- Dev server is optimized (hot reload)
- Build is optimized (tree-shaking, minification)
- Mock data loads instantly

---

## 📝 Logs and Output

### Backend Output
```
[*] Starting URL enumeration...
[+] Found 25 URLs via crawling
[+] Found 15 URLs via Wayback Machine
[+] Found 8 URLs via brute force
[✓] Validation complete: 40 URLs confirmed
```

### Frontend Console
```
Loading hygiene data...
[HygieneService] Fetching from mock data
Dashboard initialized successfully
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Backend runs without errors (`python main.py --help`)
- [ ] Frontend runs without errors (`npm run dev`)
- [ ] Frontend loads at http://localhost:5173
- [ ] No console errors in browser

---

## 🎯 Next Steps

1. **Run Backend**: `python main.py -u https://example.com`
2. **Run Frontend**: `npm run dev`
3. **Access Dashboard**: http://localhost:5173
4. **Explore Features**: Click through pages and view data
5. **Make Changes**: Edit code and see hot-reload

---

## 📞 Quick Commands Reference

```bash
# Backend
python main.py --help                    # Show help
python main.py -u https://example.com    # Run crawler
python main.py -u https://example.com -m full  # Full QA

# Frontend
npm install                              # Install deps
npm run dev                              # Start dev server
npm run build                            # Production build
npm run preview                          # Preview build
```

---

**Status**: ✅ Ready to Run  
**Backend**: ✅ Python CLI Ready  
**Frontend**: ✅ React Dev Server Ready  
**Integration**: Ready (Mock data currently)
