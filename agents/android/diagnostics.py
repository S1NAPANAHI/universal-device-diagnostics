"""Android Diagnostic Agent

Uses ADB (Android Debug Bridge) commands to perform hardware diagnostics:
- Battery health and charging status
- Storage space and health
- Sensor functionality
- Network connectivity
- System performance metrics

Requires ADB to be installed and device connected with USB debugging enabled.
"""

import subprocess
import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TestResult:
    def __init__(self, test_id: str, category: str, status: str, 
                 metrics: Dict[str, Any] = None, explanation: str = "", 
                 confidence: float = 0.0, advisories: List[str] = None):
        self.test_id = test_id
        self.category = category
        self.status = status
        self.metrics = metrics or {}
        self.explanation = explanation
        self.confidence = confidence
        self.advisories = advisories or []
        self.timestamp = datetime.now()

def run_adb_command(cmd: List[str], timeout: int = 30) -> tuple:
    """Run ADB command and return output, error, return_code"""
    try:
        full_cmd = ["adb"] + cmd
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "ADB command timed out", -1
    except FileNotFoundError:
        return "", "ADB not found. Please install Android SDK platform-tools", -1
    except Exception as e:
        return "", str(e), -1

def check_adb_connection() -> bool:
    """Check if ADB is available and device is connected"""
    stdout, stderr, code = run_adb_command(["devices"])
    if code != 0:
        return False
    
    # Check if any device is connected
    lines = stdout.split('\n')
    for line in lines[1:]:  # Skip header
        if line.strip() and '\tdevice' in line:
            return True
    return False

def test_android_battery() -> TestResult:
    """Test Android battery health using ADB"""
    try:
        if not check_adb_connection():
            return TestResult(
                "battery.health", "power", "error",
                explanation="No Android device connected via ADB",
                advisories=["Enable USB debugging and connect device"]
            )
        
        # Get battery information
        stdout, stderr, code = run_adb_command([
            "shell", "dumpsys", "battery"
        ])
        
        if code != 0:
            return TestResult(
                "battery.health", "power", "error",
                explanation="Could not retrieve battery information",
                advisories=["Check ADB permissions"]
            )
        
        # Parse battery dumpsys output
        battery_info = {}
        for line in stdout.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                battery_info[key.strip()] = value.strip()
        
        # Extract key metrics
        level = int(battery_info.get('level', 0))
        health = battery_info.get('health', 'Unknown')
        status = battery_info.get('status', 'Unknown')
        temperature = battery_info.get('temperature', '0')
        voltage = battery_info.get('voltage', '0')
        
        # Convert temperature (usually in tenths of degrees Celsius)
        temp_celsius = float(temperature) / 10 if temperature.isdigit() else 0
        voltage_mv = int(voltage) if voltage.isdigit() else 0
        
        # Determine health status
        health_status = "pass"
        explanation = f"Battery level: {level}%, Health: {health}"
        advisories = []
        
        if health.lower() != 'good':
            health_status = "warn"
            explanation += ". Battery health is not optimal."
            advisories.append("Consider battery replacement if issues persist")
        
        if temp_celsius > 40:
            health_status = "warn"
            advisories.append(f"Battery temperature is high ({temp_celsius}°C)")
        
        if temp_celsius > 50:
            health_status = "fail"
            advisories.append("Critical: Battery overheating detected")
        
        if level < 15 and status.lower() != 'charging':
            advisories.append("Battery level is low, consider charging")
        
        return TestResult(
            "battery.health", "power", health_status,
            metrics={
                "level_percentage": level,
                "health": health,
                "status": status,
                "temperature_celsius": round(temp_celsius, 1),
                "voltage_mv": voltage_mv
            },
            explanation=explanation,
            confidence=0.90,
            advisories=advisories
        )
        
    except Exception as e:
        logger.error(f"Android battery test failed: {str(e)}")
        return TestResult(
            "battery.health", "power", "error",
            explanation=f"Battery test failed: {str(e)}"
        )

def test_android_storage() -> TestResult:
    """Test Android storage space and health"""
    try:
        if not check_adb_connection():
            return TestResult(
                "storage.health", "storage", "error",
                explanation="No Android device connected via ADB"
            )
        
        # Get storage information
        stdout, stderr, code = run_adb_command([
            "shell", "df", "/data"
        ])
        
        if code != 0:
            # Try alternative command
            stdout, stderr, code = run_adb_command([
                "shell", "dumpsys", "diskstats"
            ])
        
        if code != 0:
            return TestResult(
                "storage.health", "storage", "error",
                explanation="Could not retrieve storage information"
            )
        
        # Parse df output (simplified)
        lines = stdout.split('\n')
        storage_info = None
        
        for line in lines:
            if '/data' in line or 'userdata' in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        total_kb = int(parts[1]) if parts[1].isdigit() else 0
                        used_kb = int(parts[2]) if parts[2].isdigit() else 0
                        available_kb = int(parts[3]) if parts[3].isdigit() else 0
                        
                        total_gb = round(total_kb / (1024 * 1024), 1)
                        used_gb = round(used_kb / (1024 * 1024), 1)
                        available_gb = round(available_kb / (1024 * 1024), 1)
                        usage_percentage = round((used_kb / total_kb) * 100, 1) if total_kb > 0 else 0
                        
                        storage_info = {
                            "total_gb": total_gb,
                            "used_gb": used_gb,
                            "available_gb": available_gb,
                            "usage_percentage": usage_percentage
                        }
                        break
                    except (ValueError, ZeroDivisionError):
                        continue
        
        if not storage_info:
            return TestResult(
                "storage.health", "storage", "error",
                explanation="Could not parse storage information"
            )
        
        # Determine storage health
        usage_pct = storage_info["usage_percentage"]
        status = "pass" if usage_pct < 80 else "warn" if usage_pct < 90 else "fail"
        
        explanations = {
            "pass": f"Storage usage is healthy at {usage_pct}%. {storage_info['available_gb']} GB available.",
            "warn": f"Storage is getting full at {usage_pct}% usage. Consider cleanup.",
            "fail": f"Storage is critically full at {usage_pct}% usage. Immediate cleanup needed."
        }
        
        advisories = []
        if usage_pct > 85:
            advisories.append("Clear cache, photos, or unused apps")
        if usage_pct > 90:
            advisories.append("Critical: Free up space to avoid app crashes")
        
        return TestResult(
            "storage.health", "storage", status,
            metrics=storage_info,
            explanation=explanations[status],
            confidence=0.85,
            advisories=advisories
        )
        
    except Exception as e:
        logger.error(f"Android storage test failed: {str(e)}")
        return TestResult(
            "storage.health", "storage", "error",
            explanation=f"Storage test failed: {str(e)}"
        )

def test_android_sensors() -> TestResult:
    """Test Android sensors functionality"""
    try:
        if not check_adb_connection():
            return TestResult(
                "sensors.test", "sensors", "error",
                explanation="No Android device connected via ADB"
            )
        
        # Get available sensors
        stdout, stderr, code = run_adb_command([
            "shell", "dumpsys", "sensorservice"
        ])
        
        if code != 0:
            return TestResult(
                "sensors.test", "sensors", "error",
                explanation="Could not retrieve sensor information"
            )
        
        # Parse sensor information
        sensors_found = []
        common_sensors = [
            'accelerometer', 'gyroscope', 'magnetometer', 
            'proximity', 'light', 'pressure', 'temperature'
        ]
        
        stdout_lower = stdout.lower()
        for sensor in common_sensors:
            if sensor in stdout_lower:
                sensors_found.append(sensor)
        
        sensor_count = len(sensors_found)
        
        # Determine sensor health
        if sensor_count >= 5:
            status = "pass"
            explanation = f"Found {sensor_count} sensors working properly: {', '.join(sensors_found[:5])}"
        elif sensor_count >= 3:
            status = "warn"
            explanation = f"Found {sensor_count} sensors. Some sensors may not be available."
        else:
            status = "fail"
            explanation = f"Only {sensor_count} sensors detected. Device may have sensor issues."
        
        advisories = []
        if sensor_count < 3:
            advisories.append("Check if device requires sensor calibration")
        
        return TestResult(
            "sensors.test", "sensors", status,
            metrics={
                "sensors_found": sensors_found,
                "sensor_count": sensor_count
            },
            explanation=explanation,
            confidence=0.75,
            advisories=advisories
        )
        
    except Exception as e:
        logger.error(f"Android sensors test failed: {str(e)}")
        return TestResult(
            "sensors.test", "sensors", "error",
            explanation=f"Sensors test failed: {str(e)}"
        )

def test_android_connectivity() -> TestResult:
    """Test Android network connectivity"""
    try:
        if not check_adb_connection():
            return TestResult(
                "network.connectivity", "network", "error",
                explanation="No Android device connected via ADB"
            )
        
        # Check Wi-Fi status
        stdout, stderr, code = run_adb_command([
            "shell", "dumpsys", "wifi"
        ])
        
        if code != 0:
            return TestResult(
                "network.connectivity", "network", "error",
                explanation="Could not retrieve network information"
            )
        
        # Parse Wi-Fi information
        wifi_enabled = "Wi-Fi is enabled" in stdout or "mWifiEnabled: true" in stdout
        wifi_connected = "CONNECTED/CONNECTED" in stdout or "state: CONNECTED" in stdout
        
        # Check mobile data (simplified)
        mobile_stdout, mobile_stderr, mobile_code = run_adb_command([
            "shell", "dumpsys", "telephony.registry"
        ])
        
        mobile_data = "DATA_CONNECTED" in mobile_stdout if mobile_code == 0 else False
        
        # Determine connectivity status
        if wifi_connected or mobile_data:
            status = "pass"
            explanation = "Network connectivity is working."
            if wifi_connected:
                explanation += " Wi-Fi connected."
            if mobile_data:
                explanation += " Mobile data available."
        elif wifi_enabled:
            status = "warn"
            explanation = "Wi-Fi is enabled but not connected to a network."
        else:
            status = "fail"
            explanation = "No network connectivity detected."
        
        advisories = []
        if not wifi_connected and not mobile_data:
            advisories.append("Check Wi-Fi password or mobile data settings")
        
        return TestResult(
            "network.connectivity", "network", status,
            metrics={
                "wifi_enabled": wifi_enabled,
                "wifi_connected": wifi_connected,
                "mobile_data": mobile_data
            },
            explanation=explanation,
            confidence=0.80,
            advisories=advisories
        )
        
    except Exception as e:
        logger.error(f"Android connectivity test failed: {str(e)}")
        return TestResult(
            "network.connectivity", "network", "error",
            explanation=f"Connectivity test failed: {str(e)}"
        )

async def run_android_diagnostics(tests: List[str]) -> List[TestResult]:
    """Run requested diagnostic tests on Android device via ADB"""
    results = []
    
    # Map test IDs to functions
    test_functions = {
        "battery.health": test_android_battery,
        "storage.health": test_android_storage,
        "sensors.test": test_android_sensors,
        "network.connectivity": test_android_connectivity,
    }
    
    # Check ADB connection first
    if not check_adb_connection():
        for test_id in tests:
            results.append(TestResult(
                test_id, "unknown", "error",
                explanation="No Android device connected. Enable USB debugging and connect device.",
                advisories=[
                    "Install ADB (Android SDK platform-tools)",
                    "Enable Developer Options on your Android device",
                    "Enable USB Debugging in Developer Options",
                    "Connect device with USB cable and accept debugging prompt"
                ]
            ))
        return results
    
    for test_id in tests:
        if test_id in test_functions:
            logger.info(f"Running Android test: {test_id}")
            try:
                result = test_functions[test_id]()
                results.append(result)
            except Exception as e:
                logger.error(f"Test {test_id} failed: {str(e)}")
                results.append(TestResult(
                    test_id, "unknown", "error",
                    explanation=f"Test execution failed: {str(e)}"
                ))
        else:
            logger.warning(f"Unknown Android test: {test_id}")
            results.append(TestResult(
                test_id, "unknown", "error",
                explanation=f"Test not implemented: {test_id}"
            ))
    
    return results