#!/usr/bin/env python3
import ipaddress
import socket
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List

import psutil
import requests
from PIL import Image, ImageTk 
import sys
import os

SERVICE_BASE_URL = "http://localhost:8000"
HTTP_TIMEOUT = 5  

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_active_interfaces() -> List[str]:
    return [n for n, s in psutil.net_if_stats().items() if s.isup]

def get_ipv4_info(iface: str) -> Dict[str, str]:
    for addr in psutil.net_if_addrs().get(iface, []):
        if addr.family == socket.AF_INET:
            return {
                "ip": addr.address or "",
                "mask": addr.netmask or "",
                "gateway": "",
                "dhcp": addr.broadcast is None
            }
    return {"ip": "", "mask": "", "gateway": "", "dhcp": False}

def cidr_to_netmask(cidr: str) -> str:
    bits = int(cidr)
    return str(ipaddress.IPv4Network(f"0.0.0.0/{bits}").netmask)

class InterfaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Netman")
        self.geometry("440x460")
        self.resizable(False, False)
        self.iconbitmap(resource_path("logo.ico"))

        
        try:
            image = Image.open("logo.png").resize((100, 100))
            self.logo_image = ImageTk.PhotoImage(image)
            ttk.Label(self, image=self.logo_image).pack(pady=(10, 10))
        except Exception:
            pass

        ttk.Label(self, text="Interface réseau active :").pack(pady=(0, 5))

        self.iface_var = tk.StringVar()
        self.dropdown = ttk.Combobox(self, textvariable=self.iface_var, state="readonly", width=30)
        self.dropdown.pack()

        self.iface_var.trace_add("write", self.update_fields)

        fields = ttk.Frame(self)
        fields.pack(pady=10)

        ttk.Label(fields, text="Adresse IPv4 :").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.ip_entry = ttk.Entry(fields, width=24)
        self.ip_entry.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(fields, text="Masque (CIDR ou netmask) :").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.mask_entry = ttk.Entry(fields, width=24)
        self.mask_entry.grid(row=1, column=1, padx=6, pady=4)

        ttk.Label(fields, text="Passerelle (optionnelle) :").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        self.gw_entry = ttk.Entry(fields, width=24)
        self.gw_entry.grid(row=2, column=1, padx=6, pady=4)

        btns = ttk.Frame(self)
        btns.pack(pady=10)
        ttk.Button(btns, text="Appliquer", command=self.apply_config).pack(side="left", padx=6)
        ttk.Button(btns, text="Activer DHCP", command=self.set_dhcp).pack(side="left", padx=6)

        footer = ttk.Label(self, text="Created by CALLET Alexis, this app is licensed under the MIT License.", font=("Segoe UI", 8))
        footer.pack(side="bottom", pady=(12, 4))

        self.refresh_interfaces()

    def refresh_interfaces(self):
        interfaces = get_active_interfaces()
        self.dropdown["values"] = interfaces
        if interfaces:
            self.iface_var.set(interfaces[0])

    def update_fields(self, *args):
        iface = self.iface_var.get()
        if not iface:
            return
        cur = get_ipv4_info(iface)
        self.ip_entry.delete(0, tk.END)
        self.ip_entry.insert(0, cur["ip"])
        self.mask_entry.delete(0, tk.END)
        self.mask_entry.insert(0, cur["mask"])
        self.gw_entry.delete(0, tk.END)
        self.gw_entry.insert(0, cur["gateway"])
        self.dhcp_active = cur["dhcp"]

    def _valid_ip(self, v: str) -> bool:
        try:
            ipaddress.IPv4Address(v)
            return True
        except ipaddress.AddressValueError:
            return False

    def _valid_mask(self, v: str) -> bool:
        if v == "":
            return False
        if v.isdigit():
            return 0 <= int(v) <= 32
        return self._valid_ip(v)

    def apply_config(self):
        iface = self.iface_var.get()
        ip = self.ip_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gw = self.gw_entry.get().strip()

        if not self._valid_ip(ip):
            messagebox.showerror("Erreur", "Adresse IPv4 invalide")
            return
        if not self._valid_mask(mask):
            messagebox.showerror("Erreur", "Masque invalide (CIDR ou netmask)")
            return
        if gw and not self._valid_ip(gw):
            messagebox.showerror("Erreur", "Passerelle invalide")
            return
        if mask.isdigit():
            mask = cidr_to_netmask(mask)

        payload = {"interface": iface, "ipv4": ip, "mask": mask, "gateway": gw}
        self._send(payload)

    def set_dhcp(self):
        iface = self.iface_var.get()
        if hasattr(self, "dhcp_active") and self.dhcp_active:
            messagebox.showinfo("Information", "Le DHCP est déjà actif sur cette interface.")
            return
        self._send({"interface": iface, "dhcp": True})

    def _send(self, payload: Dict):
        try:
            r = requests.post(f"{SERVICE_BASE_URL}/interfaces/{payload['interface']}", json=payload, timeout=HTTP_TIMEOUT)
            if r.status_code == 200:
                messagebox.showinfo("Succès", "Configuration envoyée ✔️")
            else:
                messagebox.showerror("Erreur", f"HTTP {r.status_code} : {r.text[:200]}")
        except requests.exceptions.RequestException:
            messagebox.showerror("Erreur", "Connexion au service backend impossible.")

if __name__ == "__main__":
    InterfaceApp().mainloop()
