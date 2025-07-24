from .bot_instance import bot
import asyncio
from aiogram.enums import ParseMode
from vk_api.exceptions import VkApiError
from services.vk_utils import vk

from config import Config
from services.storage import storage

async def format_post_message(entity_id: str, post: dict, entity_name: str) -> str:
    if entity_id.startswith('-'):
        post_url = f"https://vk.com/club{entity_id[1:]}?w=wall{entity_id}_{post['id']}"
    else:
        post_url = f"https://vk.com/id{entity_id[2:]}?w=wall{entity_id}_{post['id']}"
    
    message = [
        f"📢 Новый пост в <b>{entity_name}</b>",
        f"🔗 <a href='{post_url}'>Открыть пост</a>"
    ]
    
    if post.get('text'):
        text = post['text'][:500] + ("..." if len(post['text']) > 500 else "")
        message.append(f"\n{text}")
    
    if post.get('attachments'):
        message.append("\n\n📎 В посте есть вложения")
    
    return "\n".join(message)

async def notify_subscribers(entity_id: str, message_text: str):
    for user_id, subs in storage.subscriptions.items():
        if entity_id in subs:
            try:
                await bot.send_message(
                    int(user_id),
                    message_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            except Exception:
                pass

async def check_new_posts():
    while True:  
        entities_to_check = set()
        for user_subs in storage.subscriptions.values():
            entities_to_check.update(user_subs)
        
        for entity_id in entities_to_check:
            try:
                await asyncio.sleep(0.5)
                
                if entity_id.startswith('id'):
                    owner_id = entity_id[2:]
                    api_owner_id = owner_id
                else:
                    owner_id = entity_id[1:] if entity_id.startswith('-') else entity_id
                    api_owner_id = f"-{owner_id}"
                
                try:
                    if entity_id.startswith('id'):
                        entity_info = vk.users.get(user_ids=owner_id)[0]
                        entity_name = f"{entity_info['first_name']} {entity_info['last_name']}"
                    else:
                        entity_info = vk.groups.getById(group_id=owner_id)
                        entity_name = entity_info['groups'][0]['name']
                except Exception as e:
                    print(f"Ошибка получения информации: {e}")
                    continue
                
                try:
                    response = vk.wall.get(
                        owner_id=api_owner_id,
                        count=1,
                        filter="owner"
                    )
                    
                    if not response.get('items'):
                        continue
                        
                    last_post = response['items'][0]
                    last_post_id = last_post['id']
                    
                    if entity_id not in storage.last_posts:
                        storage.last_posts[entity_id] = last_post_id
                        storage.save()
                        continue
                        
                    if last_post_id != storage.last_posts[entity_id]:
                        storage.last_posts[entity_id] = last_post_id
                        storage.save()
                        message_text = await format_post_message(entity_id, last_post, entity_name)
                        await notify_subscribers(entity_id, message_text)
                
                except VkApiError as e:
                    print(f"Ошибка API: {e}")
                except Exception as e:
                    print(f"Ошибка: {e}")
                    
            except Exception as e:
                print(f"Критическая ошибка: {e}")
                await asyncio.sleep(10)
                
        await asyncio.sleep(Config.CHECK_INTERVAL)