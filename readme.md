# Netman – Network Interface Manager (v3.0)

> **Created by CALLET Alexis**  
> _This app is licensed under the MIT License._

OVERVIEW
--------
Netman is a Windows application that allows users to configure local network interfaces
using a graphical interface. It supports both static IPv4 assignment and dynamic (DHCP) configuration.

The application is composed of:
1. A standalone graphical interface (`Netman.exe`) compiled with PyInstaller.
2. A backend REST service (`network_backend_service_windows.py`) that applies IP configurations using `netsh`.

FILES INCLUDED
--------------
• Netman.exe ...................... Standalone desktop application (.exe)
• logo.ico ........................ Application icon (used by .exe and desktop shortcuts)
• logo.png ........................ Displayed in the UI header
• network_card_app.py ............ Source code of the interface (Tkinter)
• network_backend_service_windows.py ... Backend service to be installed as a Windows service
• readme.txt ...................... This documentation

PREREQUISITES
-------------
Windows 10/11 (64-bit)  
Administrator rights (for backend service)  
Python 3.11+ (only required for backend installation)

REQUIRED PYTHON MODULES (backend only)
--------------------------------------
Open PowerShell as administrator and run:

```
py -3.11 -m pip install flask psutil pywin32 requests
```

INSTALLING THE BACKEND (Windows Service)
----------------------------------------

📦 If you want to use the backend as a compiled `.exe` (e.g. `network_backend_service_windows.exe`) instead of running it via Python, follow these steps:

1. Open **Command Prompt as Administrator**.
2. Run the following commands from the folder containing the `.exe`:

```
network_backend_service_windows.exe install
network_backend_service_windows.exe start
```

- The service will be installed with automatic startup at boot.
- To stop the service: `network_backend_service_windows.exe stop`
- To uninstall: `network_backend_service_windows.exe remove`

---

1. Open PowerShell as Administrator.
2. Navigate to the project folder.
3. Run the following commands to install and start the backend:

```
py -3.11 network_backend_service_windows.py --startup auto install
py -3.11 network_backend_service_windows.py start
```

- `--startup auto`: Automatically launches the service at boot.
- To stop the service: `py network_backend_service_windows.py stop`
- To uninstall: `py network_backend_service_windows.py remove`

Once installed, the backend listens only on `127.0.0.1:8000` and requires no internet access.

USING THE APPLICATION (Netman.exe)
----------------------------------
1. Launch `Netman.exe` (no Python required).
2. Select an active network interface from the dropdown.
3. Edit the IP address, mask (CIDR or netmask), and optional gateway.
   - You may enter CIDR notation (e.g., `24`) or full netmask (`255.255.255.0`)
4. Click:
   - **Apply** to set static IP configuration
   - **Enable DHCP** to revert the interface to dynamic mode

TECHNICAL DETAILS
-----------------
• REST endpoint used:
  `POST http://localhost:8000/interfaces/<interface_name>`

• Payload example (static):
{
  "interface": "Ethernet0",
  "ipv4": "XXX.XXX.X.XXX",
  "mask": "XXX.XXX.XXX.X",
  "gateway": "XXX.XXX.X.X"
}

• Payload example (DHCP):
{
  "interface": "Ethernet0",
  "dhcp": true
}

• Backend responds with:
{ "status": "ok", "interface": "Ethernet0" }

DISTRIBUTION
------------
Only these files need to be distributed:
- `Netman.exe`
- `logo.png`
- `logo.ico` (optional, used for creating Windows shortcuts)

Python and dependencies are embedded in `Netman.exe`. It can be launched from any folder or USB drive.

LIMITATIONS
-----------
- Backend only works on Windows with admin rights
- Only IPv4 is supported (no IPv6 or DNS config yet)
- Make sure the backend service is running, or the GUI will display a connection error

RECOMMENDED NEXT STEPS (Optional)
---------------------------------
• Log all `netsh` commands to `C:\logs\network_backend.log`  
• Add DNS configuration support (`netsh interface ip set dns ...`)  
• Provide a full installer (e.g., Inno Setup or NSIS) with Start Menu/desktop shortcut  
• Add token-based authentication to secure the backend if exposed

---

Created by CALLET Alexis, this app is licensed under the MIT License.
