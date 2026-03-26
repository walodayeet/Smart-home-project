# 🏠 Smart Home Web App

A full-stack smart home control system with React frontend and FastAPI backend, featuring face recognition, device control, voice commands, and live camera feeds.

## 🚀 Features

- **📹 Live Camera Feeds**: View multiple camera streams with auto-refresh
- **🔒 Device Control**: Manage locks, lights, and blinds remotely
- **🎙️ Voice Commands**: Control devices using natural language
- **👤 Face Recognition**: Upload images for simulated face recognition (demo mode)
- **📱 Mobile-First Design**: Responsive PWA with iOS/Android support
- **⚡ Real-time Updates**: WebSocket connection for live device status
- **🎨 Modern UI**: Tailwind CSS with smooth animations

---

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

---

## 🛠️ Local Development

### 1. Clone and Navigate

```bash
cd web-app
```

### 2. Set Up Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env and change SECRET_KEY for production
```

### 3. Set Up Frontend

```bash
cd ../frontend
npm install
```

### 4. Run Development Servers

**Terminal 1 (Backend):**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser.

---

## 🐳 Docker Deployment (Dokploy with Nixpacks)

### Option 1: Nixpacks (Recommended - Zero Config)

Dokploy auto-detects the stack using `nixpacks.json`:

1. **Push to Git**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **In Dokploy Dashboard**:
   - Create new service
   - Connect your Git repo
   - Set branch to `main`
   - Set root directory to `web-app/`
   - Dokploy auto-detects Nixpacks config
   - Add environment variables (see below)
   - Deploy!

### Option 2: Manual Dockerfile

Create `Dockerfile` in `web-app/`:

```dockerfile
FROM node:18 as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./backend/static

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔐 Environment Variables (Dokploy)

Set these in Dokploy's environment variables section:

```env
SECRET_KEY=your-super-secret-key-change-this
CORS_ORIGINS=["https://yourdomain.com"]
PROJECT_NAME=Smart Home API
```

---

## 📱 Demo Strategy: Connecting to Recognition System

The app currently runs in **demo mode** with simulated responses. Here's how to demonstrate the connection:

### 1. **Upload & Recognize Demo** (Current Implementation)
- Navigate to Dashboard
- Upload any image
- System returns simulated recognition results:
  - 50% chance: Recognized owner/family member
  - 30% chance: Unknown person (alert)
  - 20% chance: Masked detection

### 2. **Future: Connect to Real Recognition System**

When you have a real face recognition service, update `backend/app/services/mock_recognition.py`:

```python
# Replace MockRecognitionService with real API calls
import httpx

class RecognitionService:
    def __init__(self):
        self.api_url = os.getenv("RECOGNITION_API_URL")
    
    async def recognize(self, image: Image.Image) -> RecognitionResult:
        # Convert image to bytes
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        
        # Call your recognition API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/recognize",
                files={"image": buffer.getvalue()}
            )
            data = response.json()
        
        return RecognitionResult(**data)
```

### 3. **WebSocket Live Feed** (Future Enhancement)

For real-time camera recognition:

```python
# backend/app/main.py - Add camera stream endpoint
@app.websocket("/ws/camera/{camera_id}")
async def camera_stream(websocket: WebSocket, camera_id: str):
    await websocket.accept()
    
    # Stream frames from real camera
    cap = cv2.VideoCapture(camera_id)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run recognition
        result = await recognition_service.recognize(frame)
        
        # Send frame + recognition result
        await websocket.send_json({
            "frame": encode_frame(frame),
            "recognition": result.dict()
        })
```

---

## 📊 API Endpoints

### Recognition
- `POST /api/recognition/upload` - Upload image for recognition
- `GET /api/recognition/recent` - Get recent recognition events

### Devices
- `GET /api/devices` - List all devices
- `POST /api/devices/{id}/toggle` - Toggle device on/off
- `POST /api/devices/{id}/command` - Send custom command

### Cameras
- `GET /api/cameras` - List all cameras
- `GET /api/cameras/{id}/snapshot` - Get camera snapshot

### Voice
- `POST /api/voice/command` - Process voice command

### System
- `GET /api/health` - Health check
- `GET /api/system/status` - System status
- `WS /ws` - WebSocket for real-time updates

---

## 🎨 Tech Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Zustand (state management)
- Lucide React (icons)
- PWA support

**Backend:**
- FastAPI
- Python 3.11
- Pydantic
- WebSockets
- Pillow (image processing)

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

---

## 📝 Architecture Notes

### Demo Mode Behavior
- **Mock Recognition**: Random results with realistic delays
- **Simulated Cameras**: Generated placeholder images with timestamps
- **Device Manager**: In-memory state management
- **WebSocket**: Broadcasts device state changes

### Production Considerations
1. Replace `MockRecognitionService` with real ML inference
2. Connect to actual camera RTSP/HTTP streams
3. Add authentication (JWT tokens)
4. Use Redis for device state persistence
5. Add rate limiting and security headers
6. Configure HTTPS/TLS for WebSocket

---

## 🐛 Troubleshooting

**Frontend not connecting to backend:**
- Check Vite proxy config in `vite.config.ts`
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/core/config.py`

**Voice control not working:**
- Use Chrome or Edge (Safari has limited support)
- Grant microphone permissions
- HTTPS required for production (WebRTC)

**WebSocket connection fails:**
- Check firewall rules
- Ensure WebSocket is not blocked by reverse proxy
- Use `wss://` for HTTPS deployments

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with ❤️ for modern smart homes**
