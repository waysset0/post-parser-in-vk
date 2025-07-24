from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from vk_api.exceptions import VkApiError

from config import Config
from services.storage import storage
from services.vk_utils import extract_vk_id_from_url, vk

router = Router()

@router.message(Command("add"))
async def add_subscription(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите ссылку, ID или короткое имя после команды /add")
        return
    
    input_str = args[1].strip()
    user_id = message.from_user.id
    
    if input_str.startswith(('http://', 'https://', 'vk.com/')):
        if not input_str.startswith(('http://', 'https://')):
            input_str = 'https://' + input_str
        vk_entity = extract_vk_id_from_url(input_str)
        if not vk_entity:
            await message.answer("❌ Не удалось распознать ссылку ВКонтакте")
            return
    else:
        vk_entity = input_str.lower()
    
    try:
        if vk_entity.startswith("id"):
            owner_id = vk_entity[2:]
            entity_info = vk.users.get(user_ids=owner_id, fields="screen_name")[0]
            entity_name = f"{entity_info['first_name']} {entity_info['last_name']}"
            entity_id = f"id{entity_info['id']}"
        elif vk_entity.startswith(("club", "public")):
            group_id = vk_entity[4:]
            entity_info = vk.groups.getById(group_id=group_id)
            entity_name = entity_info['groups'][0]['name']
            entity_id = f"-{entity_info['groups'][0]['id']}"
        else:
            try:
                entity_info = vk.groups.getById(group_id=vk_entity)
                entity_name = entity_info['groups'][0]['name']
                entity_id = f"-{entity_info['groups'][0]['id']}"
            except VkApiError:
                entity_info = vk.users.get(user_ids=vk_entity, fields="screen_name")[0]
                entity_name = f"{entity_info['first_name']} {entity_info['last_name']}"
                entity_id = f"id{entity_info['id']}"
        
        if str(user_id) not in storage.subscriptions:
            storage.subscriptions[str(user_id)] = []
        
        if entity_id in storage.subscriptions[str(user_id)]:
            await message.answer(f"ℹ️ Вы уже подписаны на {entity_name}")
            return
        
        storage.subscriptions[str(user_id)].append(entity_id)
        storage.save()
        
        try:
            posts = vk.wall.get(owner_id=entity_id, count=1)["items"]
            if posts:
                storage.last_posts[entity_id] = posts[0]["id"]
                storage.save()
        except VkApiError:
            pass
        
        await message.answer(f"✅ Вы подписались на новые посты: <b>{entity_name}</b>", parse_mode=ParseMode.HTML)
        
    except VkApiError:
        await message.answer("❌ Не удалось найти указанное сообщество или профиль")