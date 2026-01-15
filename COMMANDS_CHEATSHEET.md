# ⚡ Quick Commands Cheat Sheet

Copy-paste ready commands to run everything.

---

## 🔥 The Absolute Quickest Way (2 terminals)

### Terminal 1: Frontend
```powershell
cd frontend
npm install
npm run dev
```

Then open: **http://localhost:5173**

### Terminal 2: Backend (Optional)
```powershell
pip install -r requirements.txt
python main.py -u https://example.com -m full
```

---

## 📋 Full Commands by Task

### Initial Setup (One Time)

```powershell
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

### Running Backend

```powershell
# Help/Documentation
python main.py --help

# Simple crawl
python main.py -u https://example.com

# Full QA inspection
python main.py -u https://example.com -m full

# With Wayback Machine
python main.py -u https://example.com --wayback

# Brute force paths
python main.py -u https://example.com --bruteforce

# All features enabled
python main.py -u https://example.com -m full --wayback --bruteforce

# Custom depth
python main.py -u https://example.com -d 3
```

### Running Frontend

```powershell
cd frontend

# Start development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Use different port
npm run dev -- --port 3000
```

---

## 🎯 Typical Development Workflow

```powershell
# Terminal 1: Start frontend (stays running)
cd frontend
npm run dev

# Terminal 2: Run backend commands as needed
cd ..
python main.py -u https://example.com

# Browser: Open and test
# http://localhost:5173
```

---

## 🔄 Stop Everything

```powershell
# Press Ctrl+C in each terminal to stop
```

---

## ✅ Verify Installation

```powershell
# Check Python
python --version
pip list | findstr "httpx beautifulsoup4 playwright requests"

# Check Node
node --version
npm list react react-dom react-router-dom

# Check frontend
cd frontend
npm run build  # Should say "built in X.XXs"
```

---

## 🐛 Troubleshooting Quick Fixes

```powershell
# Python: Re-install dependencies
pip install -r requirements.txt --upgrade --force-reinstall

# Node: Clean install
cd frontend
rm -r node_modules package-lock.json
npm install

# Port conflict: Use different port
npm run dev -- --port 3000

# Clear Python cache
py -3 -B main.py --help
```

---

## 📊 Sample Backend Commands

```powershell
# Test with httpbin (good for testing)
python main.py -u https://httpbin.org -d 1

# Test with real site
python main.py -u https://github.com -d 1

# Detailed crawl
python main.py -u https://example.com -d 2 -m full --wayback

# Just JavaScript analysis
python main.py -u https://example.com -d 1
```

---

## 🌐 Access Points

```
Frontend:      http://localhost:5173
Backend API:   http://localhost:8000 (when running API mode)
```

---

## 📱 Environment Variables (Optional)

```powershell
# Set Python path (if needed)
$env:PYTHONPATH = "."

# Set Node env
$env:NODE_ENV = "development"
```

---

## 💾 Database/Storage

Current setup uses:
- **Mock data**: Embedded in frontend
- **No database**: File-based (future enhancement)
- **No backend API**: Direct CLI (future enhancement)

---

## 🎓 Command Breakdown

### `npm run dev`
- Starts Vite dev server
- Hot module reloading enabled
- Serves on port 5173
- Shows mock data

### `python main.py -u URL -m full --wayback --bruteforce`
- `-u URL` = target URL to scan
- `-m full` = full QA mode (crawl + analyze)
- `--wayback` = include historical URLs
- `--bruteforce` = test common paths

---

## 🚀 One-Command Setups

```powershell
# Complete fresh setup
pip install -r requirements.txt; cd frontend; npm install; npm run dev

# Just run backend
python main.py -u https://example.com -m full

# Just run frontend
cd frontend; npm run dev
```

---

## 📞 Getting Help

```powershell
# Help for backend
python main.py --help

# Help for npm
npm --help
npm run

# Check versions
python --version
npm --version
node --version
pip --version
```

---

## 🎯 Development Cycle

1. **Start**: `npm run dev` (Terminal 1)
2. **Edit**: Make changes to code
3. **Reload**: Frontend auto-reloads
4. **Test**: http://localhost:5173
5. **Backend**: `python main.py ...` (Terminal 2)

---

**Last Updated**: January 15, 2026
