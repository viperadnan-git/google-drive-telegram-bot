from pyrogram import Client, filters
from bot.config import BotCommands, Messages
from bot.helpers.utils import CustomFilters
from bot.helpers.gdrive_utils import GoogleDrive
from bot import LOGGER

@Client.on_message(filters.private & filters.incoming & filters.command(BotCommands.Clone) & CustomFilters.auth_users)
def _clone(client, message):
  user_id = message.from_user.id
  if len(message.command) > 1:
    link = message.command[1]
    LOGGER.info(f'Copy:{user_id}: {link}')
    sent_message = message.reply_text(Messages.CLONING.format(link), quote=True)
    msg = GoogleDrive(user_id).clone(link)
    sent_message.edit(msg)
  else:
    message.reply_text(Messages.PROVIDE_GDRIVE_URL.format(BotCommands.Clone[0]))