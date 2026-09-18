#!/usr/bin/env python3
"""
CML Lab Config Backup Tool
----------------------------
Connects to devices in my CML lab (reachable from MGMT-DT) and pulls each one's running-config, saving
it as a timestamped file under configs/.
"""

import os
import sys
import getpass
from datetime import datetime
from pathlib import Path

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

INVENTORY_FILE = "inventory.yaml"
BACKUP_DIR = Path("configs")


def load_inventory(path):
    if not os.path.exists(path):
        sys.exit(
            f"Inventory file not found: {path}\n"
            f"Copy inventory.example.yaml to {path} and fill in your devices."
        )
    with open(path) as f:
        return yaml.safe_load(f)


def get_credentials(inventory):
    username = inventory.get("username") or input("Username: ")
    password = inventory.get("password") or getpass.getpass("Password: ")
    return username, password


def backup_device(device, username, password):
    conn_params = {
        "device_type": device.get("device_type", "cisco_ios"),
        "host": device["host"],
        "username": username,
        "password": password,
    }
    if device.get("secret"):
        conn_params["secret"] = device["secret"]

    print(f"Connecting to {device['name']} ({device['host']})...")
    try:
        conn = ConnectHandler(**conn_params)
        if device.get("secret"):
            conn.enable()
        output = conn.send_command("show running-config")
        conn.disconnect()
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"  FAILED: {e}")
        return False

    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = BACKUP_DIR / f"{device['name']}.cfg"
    filename.write_text(output)
    print(f"  Saved -> {filename}")
    return True


def main():
    inventory = load_inventory(INVENTORY_FILE)
    devices = inventory.get("devices", [])
    if not devices:
        sys.exit("No devices listed in inventory.yaml")

    username, password = get_credentials(inventory)

    results = [backup_device(d, username, password) for d in devices]

    ok = sum(results)
    print(f"\nDone: {ok}/{len(devices)} devices backed up successfully.")


if __name__ == "__main__":
    main()
