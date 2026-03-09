from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(
    prefix="/device",
    tags=["device"]
)

# temporary memory storage
devices = []


# --------------------------------
# Register Device
# --------------------------------
@router.post("/register")
def register_device(device: dict):

    devices.append(device)

    return {
        "message": "device registered",
        "device": device
    }


# --------------------------------
# List Devices
# --------------------------------
@router.get("/list")
def list_devices():

    return {
        "devices": devices
    }


# --------------------------------
# Scan WiFi Networks from Device
# --------------------------------
@router.get("/wifi-scan")
def wifi_scan(ip: str):

    try:

        response = requests.get(
            f"http://{ip}/scan_wifi",
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"wifi scan failed: {str(e)}"
        )


# --------------------------------
# Setup WiFi on Device
# --------------------------------
@router.post("/wifi-setup")
def wifi_setup(data: dict):

    ip = data.get("ip")

    if not ip:
        raise HTTPException(
            status_code=400,
            detail="device ip required"
        )

    try:

        response = requests.post(
            f"http://{ip}/setup_wifi",
            json=data,
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"wifi setup failed: {str(e)}"
        )


# --------------------------------
# Send Action to Device
# --------------------------------
@router.post("/action")
def device_action(data: dict):

    ip = data.get("ip")

    if not ip:
        raise HTTPException(
            status_code=400,
            detail="device ip required"
        )

    try:

        response = requests.post(
            f"http://{ip}/action",
            json=data,
            timeout=5
        )

        return response.json()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"device action failed: {str(e)}"
        )