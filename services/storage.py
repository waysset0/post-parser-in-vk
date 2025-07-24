import json
import os
from typing import Dict, List

from config import Config

class Storage:
    def __init__(self):
        self.subscriptions = {}
        self.last_posts = {}
        self.load()

    def load(self):
        if os.path.exists(Config.STORAGE_FILE):
            try:
                with open(Config.STORAGE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.subscriptions = data.get('subscriptions', {})
                    self.last_posts = data.get('last_posts', {})
            except Exception:
                self.subscriptions = {}
                self.last_posts = {}

    def save(self):
        try:
            with open(Config.STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'subscriptions': self.subscriptions,
                    'last_posts': self.last_posts
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

storage = Storage()