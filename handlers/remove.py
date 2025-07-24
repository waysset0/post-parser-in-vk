from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from vk_api.exceptions import VkApiError

from config import Config
from services.storage import storage
from services.vk_utils import extract_vk_id_from_url, vk

router = Router()

@router.message(Command("remove"))
async def remove_subscription(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажите ссылку, ID или короткое имя после команды /remove")
        return
    
    input_str = args[1].strip()
    user_id = str(message.from_user.id)
    
    if user_id not in storage.subscriptions or not storage.subscriptions[user_id]:
        await message.answer("📭 У вас нет активных подписок")
        return
    
    try:
        if input_str.startswith(('http://', 'https://', 'vk.com/')):
            if not input_str.startswith(('http://', 'https://')):
                input_str = 'https://' + input_str
            vk_entity = extract_vk_id_from_url(input_str)
            if not vk_entity:
                await message.answer("❌ Не удалось распознать ссылку ВКонтакте")
                return
        else:
            vk_entity = input_str.lower()

        if vk_entity.startswith(('id', 'club', 'public')):
            if vk_entity.startswith('id'):
                user_info = vk.users.get(user_ids=vk_entity[2:], fields="screen_name")[0]
                entity_id = f"id{user_info['id']}"
                entity_name = f"{user_info['first_name']} {user_info['last_name']}"
            else:
                group_id = vk_entity.replace('club', '').replace('public', '')
                group_info = vk.groups.getById(group_id=group_id)
                entity_id = f"-{group_info['groups'][0]['id']}"
                entity_name = group_info['groups'][0]['name']
        else:
            try:
                group_info = vk.groups.getById(group_id=vk_entity)
                entity_id = f"-{group_info['groups'][0]['id']}"
                entity_name = group_info['groups'][0]['name']
            except VkApiError:
                user_info = vk.users.get(user_ids=vk_entity, fields="screen_name")[0]
                entity_id = f"id{user_info['id']}"
                entity_name = f"{user_info['first_name']} {user_info['last_name']}"

        if entity_id not in storage.subscriptions[user_id]:
            await message.answer("❌ У вас нет такой подписки")
            return

        storage.subscriptions[user_id].remove(entity_id)
        storage.save()
        await message.answer(f"✅ Подписка на <b>{entity_name}</b> удалена", parse_mode=ParseMode.HTML)

    except VkApiError:
        await message.answer("❌ Не удалось найти указанное сообщество или профиль")
    except Exception:
        await message.answer("❌ Произошла ошибка при обработке вашего запроса")