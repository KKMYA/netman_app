# Netman – Network Interface Manager (v3.0)

> **Created by CALLET Alexis**  
> _This app is licensed under the MIT License._

---

## 📋 Overview

**Netman** is a Windows desktop application that lets users configure local network interfaces via a simple GUI. It supports:

- ✅ Static IPv4 address configuration
- ✅ Dynamic (DHCP) switching
- ✅ Optional gateway handling
- ✅ CIDR to netmask conversion

It is composed of:
1. A standalone graphical app: `Netman.exe`
2. A backend REST service: `network_backend_service_windows.py` (runs as a Windows service)

---

## 📦 Included Files

| File                                     | Description                                      |
|------------------------------------------|--------------------------------------------------|
| `Netman.exe`                             | Standalone desktop application (GUI)             |
| `logo.ico`                               | Icon used by the `.exe` and desktop shortcuts    |
| `logo.png`                               | Displayed in the UI header                       |
| `network_card_app.py`                    | Source code of the GUI (Tkinter)                 |
| `network_backend_service_windows.py`     | Backend service applying IP configurations       |
| `readme.txt` / `README.md`               | This documentation                               |

---

## ⚙️ Prerequisites

- Windows 10/11 (64-bit)
- Administrator rights (for backend service)
- **Python 3.11+** (only needed for backend installation)

---

## 📥 Backend Dependencies (Python)

To install required modules for the backend, open **PowerShell as Administrator** and run:

```
py -3.11 -m pip install flask psutil pywin32 requests
```

---

## 🔧 Backend Installation (Windows Service)

To install and run the backend as a service:

```
# Run as Administrator in PowerShell
py -3.11 network_backend_service_windows.py --startup auto install
py -3.11 network_backend_service_windows.py start
```

> ℹ️ `--startup auto` ensures the backend launches automatically on system boot.

### Service management

```
# Stop the service
py network_backend_service_windows.py stop

# Remove the service
py network_backend_service_windows.py remove
```

> The backend listens only on `127.0.0.1:8000` and does not require internet access.

---

## 🚀 Using the Application

1. Launch `Netman.exe`  
2. Select an active interface from the dropdown  
3. Enter IPv4, mask (CIDR or full netmask), and optional gateway  
4. Click:
   - **Apply** → for static IP configuration
   - **Enable DHCP** → to switch to dynamic mode

---

## 🔌 API & Technical Flow

### Endpoint:
```
POST http://localhost:8000/interfaces/<interface_name>
```

### Example (Static IP):
```json
{
  "interface": "Ethernet0",
  "ipv4": "192.168.1.100",
  "mask": "255.255.255.0",
  "gateway": "192.168.1.1"
}
```

### Example (DHCP):
```json
{
  "interface": "Ethernet0",
  "dhcp": true
}
```

### Response:
```json
{
  "status": "ok",
  "interface": "Ethernet0"
}
```

---

## 📤 Distribution Notes

You only need to distribute the following:

- `Netman.exe` (compiled with PyInstaller `--onefile`)
- `logo.png` (used inside the GUI)
- `logo.ico` (optional, for Windows shortcut)

> ✅ Python is **not required** on client machines. The `.exe` runs standalone from any folder or USB stick.

---

## 🚫 Limitations

- ❗ Backend only works on **Windows** with **Administrator** privileges  
- ❗ Only **IPv4** supported (no DNS or IPv6 yet)  
- 🔌 Backend must be running before launching the GUI

---

## ✅ Recommended Next Steps (optional)

- 🔁 Log `netsh` commands to:  
  `C:\logs\network_backend.log`
- 🌐 Add support for DNS configuration:  
  `netsh interface ip set dns name="X" static 8.8.8.8`
- 🛠 Package with an installer (Inno Setup or NSIS) for:
  - Start Menu + Desktop shortcut
  - Backend service auto-installation
  - Uninstall support
- 🔒 Add token or ACL security if backend is ever exposed externally

---

**Created by CALLET Alexis**  
_This app is licensed under the MIT License._
