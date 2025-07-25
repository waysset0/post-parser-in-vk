import os

class Config:
    TELEGRAM_TOKEN = os.environ['BOT_TOKEN']
    VK_TOKEN = os.environ['VK_TOKEN']
    CHECK_INTERVAL = 60
    STORAGE_FILE = "/data/subscriptions.json"