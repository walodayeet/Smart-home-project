from contextlib import asynccontextmanager
import asyncio
import base64
from datetime import datetime, timedelta
from io import BytesIO
import json
import random
from typing import List, Optional

from fastapi import FastAPI, File, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

from app.core.config import settings
from app.models.schemas import (
    AccessLogEntry,
    CameraFeed,
    DeviceCommand,
    DeviceStatus,
    FaceVerificationResponse,
    RecognitionResult,
    SystemStatus,
    ToggleDeviceRequest,
    VoiceCommand,
)
from app.services.device_manager import DeviceManager
from app.services.face_verification import FaceVerificationService
from app.services.mock_recognition import MockRecognitionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Smart Home API starting up...")
    app.state.recognition_service = MockRecognitionService()
    app.state.device_manager = DeviceManager()
    app.state.face_verification_service = FaceVerificationService(
        recognition_service=app.state.recognition_service,
        device_manager=app.state.device_manager,
        verification_ttl_seconds=settings.FACE_VERIFICATION_TTL_SECONDS,
        min_confidence=settings.FACE_MIN_CONFIDENCE,
        authorized_person_ids=settings.FACE_AUTHORIZED_PERSON_IDS,
    )
    app.state.camera_task = None
    yield
    # Shutdown
    print("🛑 Smart Home API shutting down...")
    if app.state.camera_task:
        app.state.camera_task.cancel()


app = FastAPI(
    title="Smart Home API",
    description="Backend API for Smart Home Control System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected WebSocket clients
connected_clients: List[WebSocket] = []


@app.get("/")
async def root():
    return {"message": "Smart Home API", "version": "1.0.0", "status": "running"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "recognition": "mock",
            "cameras": "simulated",
            "devices": "active",
        },
    }


# ==================== RECOGNITION ENDPOINTS ====================


@app.post("/api/recognition/upload", response_model=RecognitionResult)
async def recognize_from_upload(file: UploadFile = File(...)):
    """
    Upload an image for face recognition.
    Returns mock recognition results for demo purposes.
    """
    try:
        # Read and process image
        contents = await file.read()
        image = Image.open(BytesIO(contents))

        # Simulate processing delay
        await asyncio.sleep(0.5 + random.random() * 0.5)

        # Get mock recognition result
        result = app.state.recognition_service.recognize(image)

        return result
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"error": f"Failed to process image: {str(e)}"}
        )


@app.get("/api/recognition/recent")
async def get_recent_recognitions(limit: int = 10):
    """Get recent recognition events."""
    return app.state.recognition_service.get_recent_events(limit)


@app.post("/api/verification/face", response_model=FaceVerificationResponse)
async def verify_face_for_action(
    file: UploadFile = File(...),
    device_id: Optional[str] = Form(default=None),
    action: Optional[str] = Form(default=None),
):
    """Verify a face image and issue a short-lived token for protected actions."""
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        verification = app.state.face_verification_service.verify_face(
            image=image,
            device_id=device_id,
            action=action,
        )
        return FaceVerificationResponse(**verification)
    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to verify face: {str(exc)}"},
        )


# ==================== CAMERA ENDPOINTS ====================


@app.get("/api/cameras")
async def get_cameras():
    """Get list of available cameras."""
    return [
        {
            "id": "cam_front_door",
            "name": "Front Door",
            "location": "Entrance",
            "status": "online",
            "resolution": "1920x1080",
            "fps": 30,
        },
        {
            "id": "cam_backyard",
            "name": "Backyard",
            "location": "Garden",
            "status": "online",
            "resolution": "1920x1080",
            "fps": 30,
        },
        {
            "id": "cam_garage",
            "name": "Garage",
            "location": "Garage Entrance",
            "status": "online",
            "resolution": "1280x720",
            "fps": 25,
        },
    ]


@app.get("/api/cameras/{camera_id}/snapshot")
async def get_camera_snapshot(camera_id: str):
    """Get a snapshot from a specific camera."""
    # Generate a mock snapshot (colored placeholder)
    colors = {
        "cam_front_door": (100, 150, 200),
        "cam_backyard": (50, 180, 100),
        "cam_garage": (180, 100, 150),
    }

    color = colors.get(camera_id, (100, 100, 100))
    img = Image.new("RGB", (640, 480), color)

    # Add timestamp
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(img)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, 10), f"{camera_id} - {timestamp}", fill=(255, 255, 255))

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return {
        "camera_id": camera_id,
        "timestamp": datetime.now().isoformat(),
        "image": f"data:image/jpeg;base64,{img_str}",
    }


# ==================== DEVICE CONTROL ENDPOINTS ====================


@app.get("/api/devices")
async def get_devices():
    """Get status of all devices."""
    return app.state.device_manager.get_all_devices()


@app.get("/api/devices/{device_id}")
async def get_device(device_id: str):
    """Get status of a specific device."""
    device = app.state.device_manager.get_device(device_id)
    if not device:
        return JSONResponse(status_code=404, content={"error": "Device not found"})
    return device


@app.post("/api/devices/{device_id}/command")
async def send_device_command(device_id: str, command: DeviceCommand):
    """Send a command to a device."""
    if app.state.face_verification_service.requires_verification(
        device_id=device_id,
        action=command.action,
    ) and not app.state.face_verification_service.consume_token(
        token=command.verification_token,
        device_id=device_id,
        action=command.action,
    ):
        return JSONResponse(
            status_code=403,
            content={"error": "Face verification required for this action"},
        )

    result = app.state.device_manager.send_command(device_id, command)
    if not result:
        return JSONResponse(
            status_code=404, content={"error": "Device not found or command failed"}
        )

    # Broadcast update to all connected clients
    await broadcast_update(
        {"type": "device_update", "device_id": device_id, "status": result}
    )

    return result


@app.post("/api/devices/{device_id}/toggle")
async def toggle_device(device_id: str, request: Optional[ToggleDeviceRequest] = None):
    """Toggle a device on/off."""
    verification_token = request.verification_token if request else None
    if app.state.face_verification_service.requires_verification(
        device_id=device_id,
        toggle=True,
    ) and not app.state.face_verification_service.consume_token(
        token=verification_token,
        device_id=device_id,
        action="unlock",
    ):
        return JSONResponse(
            status_code=403,
            content={"error": "Face verification required for this action"},
        )

    result = app.state.device_manager.toggle_device(device_id)
    if not result:
        return JSONResponse(status_code=404, content={"error": "Device not found"})

    await broadcast_update(
        {"type": "device_update", "device_id": device_id, "status": result}
    )

    return result


# ==================== VOICE COMMAND ENDPOINTS ====================


@app.post("/api/voice/command")
async def process_voice_command(command: VoiceCommand):
    """Process a voice command."""
    text = command.text.lower()

    # Simple command parsing
    response = {
        "command": text,
        "action": None,
        "success": False,
        "message": "Command not recognized",
    }

    # Lock/unlock commands
    if "lock" in text and "door" in text:
        if "unlock" in text:
            result = app.state.device_manager.send_command(
                "door_lock", DeviceCommand(action="unlock")
            )
            response.update(
                {
                    "action": "unlock_door",
                    "success": True,
                    "message": "Front door unlocked",
                }
            )
        elif "lock" in text:
            result = app.state.device_manager.send_command(
                "door_lock", DeviceCommand(action="lock")
            )
            response.update(
                {"action": "lock_door", "success": True, "message": "Front door locked"}
            )

    # Light commands
    elif "light" in text or "lights" in text:
        if "on" in text:
            for device_id in ["living_room_light", "kitchen_light"]:
                app.state.device_manager.send_command(
                    device_id, DeviceCommand(action="turn_on")
                )
            response.update(
                {"action": "lights_on", "success": True, "message": "Lights turned on"}
            )
        elif "off" in text:
            for device_id in ["living_room_light", "kitchen_light"]:
                app.state.device_manager.send_command(
                    device_id, DeviceCommand(action="turn_off")
                )
            response.update(
                {
                    "action": "lights_off",
                    "success": True,
                    "message": "Lights turned off",
                }
            )

    # Blind commands
    elif "blind" in text or "blinds" in text:
        if "open" in text or "up" in text:
            app.state.device_manager.send_command(
                "bedroom_blinds", DeviceCommand(action="open")
            )
            response.update(
                {"action": "blinds_open", "success": True, "message": "Blinds opened"}
            )
        elif "close" in text or "down" in text:
            app.state.device_manager.send_command(
                "bedroom_blinds", DeviceCommand(action="close")
            )
            response.update(
                {"action": "blinds_close", "success": True, "message": "Blinds closed"}
            )

    # Broadcast device updates
    devices = app.state.device_manager.get_all_devices()
    await broadcast_update({"type": "devices_update", "devices": devices})

    return response


# ==================== ACCESS LOG ENDPOINTS ====================


@app.get("/api/access-log")
async def get_access_log(limit: int = 50):
    """Get access log entries."""
    return app.state.recognition_service.get_access_log(limit)


# ==================== WEBSOCKET ENDPOINTS ====================


async def broadcast_update(message: dict):
    """Broadcast a message to all connected WebSocket clients."""
    disconnected = []
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)

    # Remove disconnected clients
    for client in disconnected:
        if client in connected_clients:
            connected_clients.remove(client)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        # Send initial device status
        devices = app.state.device_manager.get_all_devices()
        await websocket.send_json({"type": "devices_update", "devices": devices})

        # Keep connection alive and handle client messages
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)

                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                continue
            except json.JSONDecodeError:
                continue

    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)


# ==================== SYSTEM STATUS ====================


@app.get("/api/system/status")
async def get_system_status():
    """Get overall system status."""
    devices = app.state.device_manager.get_all_devices()

    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "mode": "demo",
        "cameras_online": 3,
        "devices_online": sum(1 for d in devices if d.get("online", False)),
        "total_devices": len(devices),
        "recent_events": len(app.state.recognition_service.get_recent_events(5)),
    }
