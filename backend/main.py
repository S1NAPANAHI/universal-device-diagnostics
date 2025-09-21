"""Universal Device Diagnostics - Main FastAPI Application"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import platform
import sys
import os
import importlib.util
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../agents'))

app = FastAPI(
    title="Universal Device Diagnostics API",
    description="AI-powered cross-platform device diagnostic and repair assistant",
    version="0.1.0"
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DeviceInfo(BaseModel):
    id: str
    device_class: str
    make: Optional[str] = None
    model: Optional[str] = None
    os: str
    os_version: str
    capabilities: List[str]
    connected_at: datetime

class TestResult(BaseModel):
    test_id: str
    category: str
    status: str  # pass, warn, fail, error
    metrics: Dict[str, Any] = {}
    explanation: str
    confidence: float
    advisories: List[str] = []
    timestamp: datetime

class DiagnosticRequest(BaseModel):
    device_id: str
    tests: List[str]
    options: Dict[str, Any] = {}

class DiagnosticResponse(BaseModel):
    device: DeviceInfo
    results: List[TestResult]
    summary: Dict[str, Any]
    report_id: str

# Global device registry
device_registry: Dict[str, DeviceInfo] = {}

@app.get("/")
async def root():
    """API root endpoint with basic info"""
    return {
        "message": "Universal Device Diagnostics API",
        "version": "0.1.0",
        "status": "active",
        "supported_platforms": ["Windows", "Android", "macOS", "iOS"]
    }

@app.get("/api/device/detect", response_model=DeviceInfo)
async def detect_device():
    """Detect current device and its diagnostic capabilities"""
    try:
        os_type = platform.system()
        device_id = f"device_{hash(platform.node())}_{int(datetime.now().timestamp())}"
        
        # Determine device capabilities based on OS
        capabilities = []
        device_class = "unknown"
        
        if os_type == "Windows":
            device_class = "laptop"
            capabilities = ["battery", "storage", "cpu", "memory", "network", "display"]
        elif os_type == "Linux":
            # Could be Android via ADB or regular Linux
            device_class = "laptop"  # Default, will enhance detection later
            capabilities = ["storage", "cpu", "memory", "network"]
        elif os_type == "Darwin":
            device_class = "laptop"
            capabilities = ["battery", "storage", "cpu", "memory", "network", "display"]
        
        device_info = DeviceInfo(
            id=device_id,
            device_class=device_class,
            os=os_type,
            os_version=platform.version(),
            capabilities=capabilities,
            connected_at=datetime.now()
        )
        
        # Register device
        device_registry[device_id] = device_info
        
        logger.info(f"Detected device: {device_class} running {os_type}")
        return device_info
        
    except Exception as e:
        logger.error(f"Device detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Device detection failed: {str(e)}")

@app.get("/api/device/{device_id}/capabilities")
async def get_device_capabilities(device_id: str):
    """Get available diagnostic tests for a specific device"""
    if device_id not in device_registry:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = device_registry[device_id]
    
    # Define available tests per capability
    test_definitions = {
        "battery": [
            {"id": "battery.health", "name": "Battery Health Check", "duration": "30s"},
            {"id": "battery.charging", "name": "Charging System Test", "duration": "60s"}
        ],
        "storage": [
            {"id": "storage.health", "name": "Storage Health (SMART)", "duration": "45s"},
            {"id": "storage.speed", "name": "Storage Performance Test", "duration": "120s"}
        ],
        "cpu": [
            {"id": "cpu.stress", "name": "CPU Stress Test", "duration": "60s"},
            {"id": "cpu.temperature", "name": "CPU Temperature Check", "duration": "30s"}
        ],
        "memory": [
            {"id": "memory.test", "name": "RAM Health Check", "duration": "90s"}
        ],
        "network": [
            {"id": "network.connectivity", "name": "Network Connectivity", "duration": "30s"},
            {"id": "network.speed", "name": "Network Speed Test", "duration": "60s"}
        ],
        "display": [
            {"id": "display.pixels", "name": "Pixel Test", "duration": "manual"},
            {"id": "display.touch", "name": "Touch Response Test", "duration": "manual"}
        ]
    }
    
    available_tests = []
    for capability in device.capabilities:
        if capability in test_definitions:
            available_tests.extend(test_definitions[capability])
    
    return {
        "device_id": device_id,
        "capabilities": device.capabilities,
        "available_tests": available_tests
    }

@app.post("/api/diagnostics/run", response_model=DiagnosticResponse)
async def run_diagnostics(request: DiagnosticRequest, background_tasks: BackgroundTasks):
    """Run diagnostic tests on the specified device"""
    if request.device_id not in device_registry:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device = device_registry[request.device_id]
    results = []
    
    try:
        # Import and run platform-specific diagnostic agents
        if device.os == "Windows":
            from agents.windows.diagnostics import run_windows_diagnostics
            results = await run_windows_diagnostics(request.tests)
        elif device.os == "Linux":
            # For Android devices connected via ADB
            from agents.android.diagnostics import run_android_diagnostics
            results = await run_android_diagnostics(request.tests)
        elif device.os == "Darwin":
            from agents.macos.diagnostics import run_macos_diagnostics
            results = await run_macos_diagnostics(request.tests)
        
        # Generate summary
        passed = len([r for r in results if r.status == "pass"])
        warnings = len([r for r in results if r.status == "warn"])
        failed = len([r for r in results if r.status == "fail"])
        errors = len([r for r in results if r.status == "error"])
        
        summary = {
            "total_tests": len(results),
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "errors": errors,
            "health_score": round((passed / len(results)) * 100, 1) if results else 0,
            "overall_status": "healthy" if failed == 0 and errors == 0 else "issues_detected"
        }
        
        report_id = f"report_{device.id}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Diagnostic completed for {device.id}: {summary}")
        
        return DiagnosticResponse(
            device=device,
            results=results,
            summary=summary,
            report_id=report_id
        )
        
    except ImportError as e:
        logger.error(f"Diagnostic agent not found: {str(e)}")
        raise HTTPException(status_code=501, detail=f"Diagnostics not implemented for {device.os}")
    except Exception as e:
        logger.error(f"Diagnostic execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diagnostic execution failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_devices": len(device_registry)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)