import re
import vk_api
from vk_api.exceptions import VkApiError

from config import Config

vk_session = vk_api.VkApi(token=Config.VK_TOKEN, api_version="5.199")
vk = vk_session.get_api()

def extract_vk_id_from_url(url: str) -> str:
    url = url.split('?')[0]
    patterns = [
        r'vk\.com/(id\d+)',
        r'vk\.com/(club\d+)',
        r'vk\.com/(public\d+)',
        r'vk\.com/([^/]+)$',
        r'vk\.com/([^/]+)/?$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1).lower()
    return None