#!/usr/bin/env python3
from bs4 import BeautifulSoup as bs
import httpx
from datetime import datetime
import yaml
from sqlitedict import SqliteDict
import hashlib
from helpers.content import *
from helpers.telegram_bot import *

KV=SqliteDict("history_hash.sqlite", autocommit=True)

with open("config.yaml","r") as f:
  config=yaml.safe_load(f)
bot_config=config["telegram_bot"]

client=httpx.Client(
  headers={
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55",
    "cookie": config["byrbt"]["cookies"]
  },
  base_url="https://byr.pt"
)
funboxPage=client.get(url="/log.php?action=funbox")

soup=bs(funboxPage.text.replace("thumb.",""),"html.parser")
content=soup.select("tr:nth-child(3) > td.rowfollow ")[0]

timeNow=datetime.now().strftime("%Y%m%d-%H")

content_string = content.text
content_hash = hashlib.sha256(content_string.encode("utf-8")).hexdigest()

if content_hash not in KV.keys():
  title=soup.select("tr:nth-child(1) > td.rowfollow")[0]
  title=title.text.split(" - ")[0]
  telegraph_url = content_to_telegraph(content, title, timeNow, client, config)["url"]
  print(telegraph_url)
  bot_send(
    bot_config["channel_id"],
    telegraph_url,
    bot_config["bot_token"]
  )
  KV[content_hash]={
    "time": timeNow,
    "url": telegraph_url
  }

else:
  print("funbox not changed since last check")
