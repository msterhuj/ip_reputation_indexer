from datetime import datetime
from typing import Optional
from time import sleep

import requests
import yaml

def send_discord_alert(fields: list):
    response = requests.request(method='POST', url=config.get('discord_webhook_url'), json={
    "content": None,
    "embeds": [
        {
        "title": "The reputation of the ip is abnormal",
        "description": "Check ip list below",
        "color": 14287105,
        "fields": fields,
        "timestamp": datetime.now().isoformat()
        }
    ],
    "attachments": []
    })

def check_abuseipdb(ip: str):
    response = requests.request(method='GET', url='https://api.abuseipdb.com/api/v2/check', headers={
        'Accept': 'application/json',
        'Key': token
    }, params={
        'ipAddress': ip,
        'maxAgeInDays': '90'
    })
    if response.status_code == 200:
        data: dict = response.json().get('data', {})
        print(f"{datetime.now()} \t| ip: {data.get('ipAddress')} \t| score: {data.get('abuseConfidenceScore')}")
    return {
        "ip": data.get('ipAddress'),
        "abuse_score": data.get('abuseConfidenceScore')
    }

config = yaml.load(open('config.yml', 'r'), Loader=yaml.FullLoader)

print(f"Starting ip reputation indexer at {datetime.now()}")
print("Testing discord webhook")
send_discord_alert([{"name": "Starting", "value": "Ip reputation checker started"}])
print(f"Enabled source: {list(config.get('token', {}).keys())}")
print(f"Ip to check: {config.get('ip_to_check', [])}")

token = config.get('token', {}).get('abuseipdb', None)
dayly_limit = config.get('dayly_limit', 1000)

query_per_ip_per_day = dayly_limit / len(config.get('ip_to_check', []))
wait_time = 86400 / query_per_ip_per_day
print(f"Query per ip per day: {query_per_ip_per_day}")
print(f"Wait time: {wait_time} seconds")

while True:
    alerts = []
    for ip in config.get('ip_to_check', []):
        reputation = check_abuseipdb(ip)
        if reputation and reputation.get('abuse_score', 99999) > 0:
            alerts.append({
                "name": f"IP: {reputation.get('ip')}",
                "value": f"Score: {reputation.get("abuse_score")}\nSource: https://www.abuseipdb.com/check/{reputation.get('ip')}",
            })

    if len(alerts) > 0:
        send_discord_alert(alerts)

    print(f"Sleeping for {wait_time} seconds")
    sleep(wait_time)
