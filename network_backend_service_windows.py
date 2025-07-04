#!/usr/bin/env python3
from __future__ import annotations

import ipaddress
import json
import platform
import subprocess
import sys
import win32event
import win32service
import win32serviceutil
from typing import Dict
from flask import Flask, jsonify, request
from threading import Thread

app = Flask("network-backend")

def _run(cmd: list[str]):
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())

def _windows_set_ipv4(iface: str, ip: str, mask: str, gw: str | None):
    cmd = ["netsh", "interface", "ip", "set", "address", iface, "static", ip, mask]
    if gw:
        cmd.append(gw)
        cmd.append("1")
    else:
        cmd.append("none")
    _run(cmd)

def _windows_set_dhcp(iface: str):
    _run(["netsh", "interface", "ip", "set", "address", iface, "dhcp"])

def _validate_static_payload(data: Dict) -> tuple[str, str, str | None]:
    ip = data.get("ipv4", "").strip()
    mask = data.get("mask", "").strip()
    gw = data.get("gateway", "").strip()

    try:
        ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError as exc:
        raise ValueError(f"Adresse IP invalide : {exc}")

    if gw:
        try:
            ipaddress.IPv4Address(gw)
        except ipaddress.AddressValueError as exc:
            raise ValueError(f"Passerelle invalide : {exc}")

    if mask.isdigit():
        if not (0 <= int(mask) <= 32):
            raise ValueError("CIDR invalide (0-32)")
    else:
        try:
            ipaddress.IPv4Address(mask)
        except ipaddress.AddressValueError:
            raise ValueError("Masque invalide")
    return ip, mask, gw or None

@app.route("/interfaces/<iface>", methods=["POST"])
def configure_interface(iface: str):
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Payload JSON manquant ou invalide"}), 400

    if data.get("dhcp") is True:
        try:
            _windows_set_dhcp(iface)
        except RuntimeError as err:
            return jsonify({"error": str(err)}), 500
        return jsonify({"status": "ok", "interface": iface, "mode": "dhcp"}), 200

    try:
        ip, mask, gw = _validate_static_payload(data)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    try:
        _windows_set_ipv4(iface, ip, mask, gw)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"status": "ok", "interface": iface, "mode": "static"}), 200

class NetworkBackendService(win32serviceutil.ServiceFramework):
    _svc_name_ = "NetworkBackendService"
    _svc_display_name_ = "Network Backend Service (IPv4 + DHCP)"
    _svc_description_ = "Service local REST appliquant les configurations IPv4 et DHCP."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.flask_thread: Thread | None = None

    def SvcDoRun(self):
        self.flask_thread = Thread(target=app.run, kwargs={"host": "127.0.0.1", "port": 8000})
        self.flask_thread.daemon = True
        self.flask_thread.start()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("Ce script ne s'exécute que sous Windows.")
        sys.exit(1)
    win32serviceutil.HandleCommandLine(NetworkBackendService)
