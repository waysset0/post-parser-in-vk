from aiogram import Router, types
from aiogram.filters import Command
from vk_api.exceptions import VkApiError

from config import Config
from services.storage import storage
from services.vk_utils import vk

router = Router()

@router.message(Command("list"))
async def list_subscriptions(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in storage.subscriptions or not storage.subscriptions[user_id]:
        await message.answer("📭 У вас нет активных подписок")
        return
    
    response = ["📋 Ваши подписки:"]
    for entity_id in storage.subscriptions[user_id]:
        try:
            if entity_id.startswith("id"):
                user_info = vk.users.get(user_ids=entity_id[2:])[0]
                entity_name = f"{user_info['first_name']} {user_info['last_name']} (id{user_info['id']})"
            else:
                group_info = vk.groups.getById(group_id=entity_id[1:])
                entity_name = f"{group_info['groups'][0]['name']} (club{group_info['groups'][0]['id']})"
            response.append(f"• {entity_name}")
        except VkApiError:
            response.append(f"• {entity_id} (недоступен)")
    
    await message.answer("\n".join(response))