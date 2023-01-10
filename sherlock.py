import subprocess
import time
import requests
import xmltodict
from telegram_init import *


def parse_scan_dict(scan_dict_raw):
    parsed_scan = []
    hosts = scan_dict_raw["nmaprun"]["host"]

    for host in hosts:
        host_ip_address = host["address"]["@addr"]
        hostnames = host["hostnames"]

        if hostnames:
            hostname = hostnames["hostname"]["@name"]
        else:
            hostname = "Could not identify"

        parsed_scan.append((host_ip_address, hostname))

    return parsed_scan


def run_os_discovery_scan():
    scan_output = subprocess.check_output(['sh', '-c', 'nmap -sn -oX - 10.100.102.0/24'])
    scan_dict = xmltodict.parse(scan_output)

    scan_parsed = parse_scan_dict(scan_dict)
    return scan_parsed


if __name__ == "__main__":
    print("Sherlock Program Initiated, started collecting data from LAN")
    telegram_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    scan_interval = 60

    lan_state = run_os_discovery_scan()
    print(lan_state)
    time.sleep(scan_interval)

    while True:
        updated_lan_state = run_os_discovery_scan()

        for device in updated_lan_state:
            if device not in lan_state:
                print("New Device Found ! ", device)

                telegram_message = f"New Device Found!, IP address: {device[0]}, hostname: {device[1]}"
                uri_params = {'chat_id': telegram_chat_id, 'text': telegram_message}
                r = requests.get(telegram_url, params=uri_params)

        lan_state = updated_lan_state
        time.sleep(scan_interval)
