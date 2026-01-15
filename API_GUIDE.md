# 🚀 Running Backend API + Frontend

Now the "Start Scan" button actually works! Here's how to set it up:

---

## ⚡ Quick Start (2 terminals)

### Terminal 1: Backend API Server
```powershell
# Make sure you're in the venv
.\venv\Scripts\Activate.ps1

# Install dependencies (if not done)
pip install -r requirements.txt

# Start the API server
python api.py
```

**You should see:**
```
 * Running on http://127.0.0.1:8000
 * Serving Flask app 'api'
 * DEBUG mode: on
```

### Terminal 2: Frontend
```powershell
cd frontend
npm run dev
```

**You should see:**
```
➜  Local:   http://localhost:5173/
```

---

## 🎯 Now Test It!

1. Open **http://localhost:5173** in browser
2. Go to **"New Scan"** page
3. Enter a URL: `https://cvr.ac.in` (or any website)
4. Click **"Start Scan"** button
5. It will call the backend API and create a scan

---

## 🔧 What Happens When You Click "Start Scan"

```
Frontend (React)
     ↓
Sends HTTP POST to: http://localhost:8000/api/scan
     ↓
Backend (Flask API)
     ↓
Returns scan_id and status
     ↓
Frontend redirects to: /active (Active Scans page)
```

---

## 📊 API Endpoints Available

### Health Check
```bash
curl http://localhost:8000/api/health
# Returns: {"status": "ok", "service": "url-enumeration-api"}
```

### Start a Scan
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "depth": 2,
    "mode": "full",
    "wayback": true,
    "bruteforce": false
  }'
```

### Get Scan Status
```bash
curl http://localhost:8000/api/scan/scan_12345
```

### Cancel Scan
```bash
curl -X DELETE http://localhost:8000/api/scan/scan_12345
```

---

## 📁 New Files

- **`api.py`** - Flask REST API server
- **Updated `requirements.txt`** - Added flask and flask-cors
- **Updated `NewScan.tsx`** - Now sends requests to API

---

## 🧪 Test Requests

### Using PowerShell
```powershell
$body = @{
    url = "https://cvr.ac.in"
    depth = 2
    mode = "full"
    wayback = $true
    bruteforce = $false
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/scan" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

### Using curl (if installed)
```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"url":"https://cvr.ac.in"}'
```

---

## ✅ Troubleshooting

### "Address already in use"
```powershell
# Port 8000 is already taken, use different port
python api.py --port 9000
```

### "ModuleNotFoundError: No module named 'flask'"
```powershell
# Install Flask
pip install flask flask-cors
```

### Frontend can't reach API
```powershell
# Make sure backend is running on port 8000
# Check: http://localhost:8000/api/health should return {"status": "ok"}
```

### CORS errors in browser console
```
# This is already fixed with flask-cors
# Make sure you're running the latest api.py
```

---

## 🔄 Development Workflow

1. **Backend Running** (Terminal 1)
   ```
   python api.py
   ```

2. **Frontend Running** (Terminal 2)
   ```
   npm run dev
   ```

3. **Make Changes**
   - Edit `api.py` → Auto-reload (Flask debug mode)
   - Edit `NewScan.tsx` → Auto-reload (Vite)

4. **Test in Browser**
   - http://localhost:5173 → Click "Start Scan"

---

## 🎉 You Now Have

✅ Functional "Start Scan" button  
✅ Frontend-to-Backend communication  
✅ REST API with multiple endpoints  
✅ Error handling and validation  
✅ Ready for real scan implementation  

---

## 📈 Next Steps

The placeholder API currently returns mock responses. To make it actually scan:

1. **Integrate URLEnumerator** into `api.py`
2. **Implement async scanning** with job queues
3. **Add real results** from backend analysis
4. **Implement WebSocket** for live progress updates

See `api.py` comments (TODO) for integration points.

---

**Status**: ✅ API + Frontend integration ready!
