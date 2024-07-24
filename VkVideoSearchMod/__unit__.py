import logging
from .. import loader, utils
from telethon import Button
import requests

logger = logging.getLogger(__name__)

@loader.tds
class VkVideoSearchMod(loader.Module):
    """Модуль для поиска видео ВКонтакте по ключевым словам"""

    strings = {"name": "VkVideoSearch"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "VK_API_KEY", "", "API ключ для доступа к VK"
        )

    async def client_ready(self, client, db):
        self.client = client

    async def searchvcmd(self, message):
        """Ищет видео ВКонтакте по ключевым словам. Использование: .searchv {ключевые слова}"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "Пожалуйста, укажите ключевые слова для поиска.")
            return

        await self._search_video(message, args)

    async def _search_video(self, message, query):
        api_key = self.config["VK_API_KEY"]
        if not api_key:
            await utils.answer(message, "API ключ не установлен. Пожалуйста, настройте модуль.")
            return

        params = {
            "q": query,
            "count": 5,  # Количество результатов
            "access_token": api_key,
            "v": "5.131"
        }
        response = requests.get("https://api.vk.com/method/video.search", params=params)
        data = response.json()

        if "response" not in data:
            await utils.answer(message, "Ошибка при поиске видео.")
            return

        videos = data["response"]["items"]
        buttons = []

        for video in videos:
            title = video.get("title", "Без названия")
            video_id = video["id"]
            owner_id = video["owner_id"]
            buttons.append(Button.inline(title, data=f"play:{owner_id}_{video_id}"))

        await utils.answer(message, "Результаты поиска:", buttons=buttons)

    async def watcher(self, message):
        if message.text and message.text.startswith("play:"):
            parts = message.text.split(":")[1].split("_")
            owner_id = parts[0]
            video_id = parts[1]
            video_url = f"https://vk.com/video{owner_id}_{video_id}"
            await message.reply(f"Ссылка на видео: {video_url}")

def register():
    """
    Функция для регистрации модуля в Hikka.
    """
    from .. import loader
    loader.register(VkVideoSearchMod)
