# 🚀 Getting Started - Step by Step

Quick visual guide to get everything running.

---

## ⏱️ Time Required: ~5 minutes

---

## 🔍 Prerequisites Check

```powershell
# Open PowerShell and check these versions:

python --version          # Need: 3.8 or higher
pip --version            # Need: 20.0 or higher
node --version           # Need: 16 or higher
npm --version            # Need: 8 or higher
```

If any are missing, install them:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

## 🎬 Step 1: Backend Setup (2 min)

### Option A: Using Command Palette (VS Code)

1. Open Terminal in VS Code
2. Navigate to project root:
   ```powershell
   cd C:\Users\sruja\OneDrive\Documents\GitHub\Subdomain_Enumeration_tool
   ```

3. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Verify installation:
   ```powershell
   python main.py --help
   ```

### What You Should See:
```
usage: main.py [-h] [-u URL] [-d DEPTH] [-m MODE] [--wayback] [--bruteforce]
...
```

---

## 🎨 Step 2: Frontend Setup (2 min)

### In Same Terminal:

1. Navigate to frontend:
   ```powershell
   cd frontend
   ```

2. Install npm dependencies:
   ```powershell
   npm install
   ```

   _Wait for it to finish... (shows "added X packages")_

3. Start dev server:
   ```powershell
   npm run dev
   ```

### What You Should See:
```
  VITE v5.4.21  ready in 592 ms

  ➜  Local:   http://localhost:5173/
```

---

## 🌐 Step 3: Open Frontend (1 min)

Open your browser and go to:
```
http://localhost:5173
```

### You Should See:
- AutoTest logo in top-left
- Sidebar with navigation items
- Hygiene Dashboard content
- Mock data displaying

---

## 🖥️ Step 4: Run Backend (Optional)

### Open NEW PowerShell Terminal:

1. Navigate to project:
   ```powershell
   cd C:\Users\sruja\OneDrive\Documents\GitHub\Subdomain_Enumeration_tool
   ```

2. Run a simple scan:
   ```powershell
   python main.py -u https://httpbin.org -d 1
   ```

3. Or see all options:
   ```powershell
   python main.py --help
   ```

---

## 📊 Final Setup

You should now have:

### Terminal 1 (Frontend)
```
✅ npm run dev
   Local: http://localhost:5173
```

### Terminal 2 (Backend - Optional)
```
✅ python main.py [options]
   Running URL enumeration
```

### Browser
```
✅ http://localhost:5173
   Dashboard showing mock data
```

---

## 🎯 Common Tasks

### View Dashboard
```
→ Open http://localhost:5173 in browser
→ Click "Hygiene Dashboard" in sidebar
→ See mock data and statistics
```

### Click a Page
```
→ Click any page URL in "Worst Performing Pages"
→ See detailed page information
→ See all issues detected
```

### Run Backend Scan
```
→ In Terminal 2, run: python main.py -u https://example.com
→ See crawled URLs and analysis
```

### Stop Everything
```
→ Terminal 1: Press Ctrl+C (stop frontend)
→ Terminal 2: Press Ctrl+C (stop backend)
```

---

## ❌ Common Issues & Fixes

### "npm: command not found"
```powershell
# Install Node.js from https://nodejs.org/
# Then restart terminal and try again
```

### "python: command not found"
```powershell
# Install Python from https://www.python.org/
# Add to PATH if needed
```

### "Port 5173 already in use"
```powershell
# Use different port
npm run dev -- --port 3000
```

### "Module not found" error
```powershell
# Reinstall dependencies
pip install -r requirements.txt
npm install
```

---

## 🎓 What Each Part Does

| Component | What It Does | Access At |
|-----------|-------------|-----------|
| **Frontend** | Shows UI dashboard | http://localhost:5173 |
| **Backend** | Crawls URLs, analyzes pages | Command line |
| **Mock Data** | Test data for frontend | Frontend only |
| **Services** | Handles data fetching | Backend integration |

---

## 📚 Next: Explore Features

### 1. Hygiene Dashboard ✅
- View overall health
- See worst pages
- Check statistics

### 2. Page Details
- Click any page in worst list
- See detailed issues
- View severity levels

### 3. Navigation
- Try different dashboard pages
- Click sidebar items
- View mock data

### 4. Backend
- Run URL enumeration
- See discovered URLs
- Check analysis results

---

## 🎉 You're Ready!

Everything is set up and running. Start exploring the platform!

### Quick Links:
- Frontend: http://localhost:5173
- Documentation: See RUN_GUIDE.md for full details
- Issues: Check troubleshooting section

---

## 💡 Pro Tips

1. **Keep dev server running** - It auto-reloads on changes
2. **Check browser console** - F12 for logs and errors
3. **Use mock data first** - Good for testing UI
4. **Scale up gradually** - Start with single URLs

---

**Status**: ✅ Setup Complete  
**Ready to Use**: Yes  
**Time Spent**: ~5 minutes  
**What's Next**: Explore the dashboard!
