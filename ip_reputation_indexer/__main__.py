from datetime import datetime
from typing import Optional
from time import sleep

import requests
import yaml

from rich import print
from sqlmodel import Field, SQLModel, create_engine, Session


class Reputation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str
    ip: str
    abuse_score: int
    at: datetime = Field(default=datetime.now())

config = yaml.load(open('config.yml', 'r'), Loader=yaml.FullLoader)

print(f"Starting ip reputation indexer at {datetime.now()}")
print(f"Enabled source: {list(config.get('token', {}).keys())}")
print(f"Ip to check: {config.get('ip_to_check', [])}")

token = config.get('token', {}).get('abuseipdb', None)
dayly_limit = config.get('dayly_limit', 1000)

query_per_ip_per_day = dayly_limit / len(config.get('ip_to_check', []))
wait_time = 86400 / query_per_ip_per_day
print(f"Query per ip per day: {query_per_ip_per_day}")
print(f"Wait time: {wait_time} seconds")

engine = create_engine(config.get("db_url"), echo=False)
SQLModel.metadata.create_all(engine)
session = Session(engine)
alerts = []

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
    print(response.status_code)

def check_abuseipdb(ip: str) -> Optional[Reputation]:
    response = requests.request(method='GET', url='https://api.abuseipdb.com/api/v2/check', headers={
        'Accept': 'application/json',
        'Key': token
    }, params={
        'ipAddress': ip,
        'maxAgeInDays': '90'
    })
    if response.status_code == 200:
        data: dict = response.json().get('data', {})
        reputation = Reputation(source='abuseipdb', ip=data.get('ipAddress'), abuse_score=data.get('abuseConfidenceScore'), at=datetime.now())
        print(f"ip: {reputation.ip}, score: {reputation.abuse_score}")
        session.add(reputation)
        return reputation

while True:
    for ip in config.get('ip_to_check', []):
        reputation = check_abuseipdb(ip)
        if reputation and reputation.abuse_score > 0:
            alerts.append({
                "name": reputation.ip,
                "value": f"Score: {reputation.abuse_score}\nSource: https://www.abuseipdb.com/check/{reputation.ip}",
            })

    if len(alerts) > 0:
        send_discord_alert(alerts)

    session.commit()
    session.close()
    print(f"Sleeping for {wait_time} seconds")
    sleep(wait_time)
