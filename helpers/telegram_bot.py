import httpx

def bot_send(channel_id: str, message: str, bot_token: str):
  client=httpx.Client()
  message_content={
    "chat_id": channel_id,
    "text": message
  }
  url=f"https://api.telegram.org/bot{bot_token}/sendMessage"
  resp=client.post(url, data=message_content)
  return resp 