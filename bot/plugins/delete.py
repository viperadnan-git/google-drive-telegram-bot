from pyrogram import Client, filters
from bot.config import BotCommands, Messages
from bot.helpers.gdrive_utils import GoogleDrive
from bot.helpers.utils import CustomFilters
from bot import LOGGER

@Client.on_message(filters.private & filters.incoming & filters.command(BotCommands.Delete) & CustomFilters.auth_users)
def _delete(client, message):
  user_id = message.from_user.id
  if len(message.command) > 1 or message.reply_to_message:
    sent_message = message.reply_text('🕵️**Checking Link...**', quote=True)
    if len(message.command) > 1:
      link = message.command[1]
    elif message.reply_to_message.entities[1].url:
      link = message.reply_to_message.entities[1].url
    else:
      message.reply_text(Messages.PROVIDE_GDRIVE_URL.format(BotCommands.Delete[0]), quote=True)
      return
    LOGGER.info(f'Delete:{user_id}: {link}')
    result = GoogleDrive(user_id).delete_file(link)
    sent_message.edit(result)
  else:
    message.reply_text(Messages.PROVIDE_GDRIVE_URL.format(BotCommands.Delete[0]), quote=True)


@Client.on_message(filters.private & filters.incoming & filters.command(BotCommands.EmptyTrash) & CustomFilters.auth_users)
def _emptyTrash(client, message):
  user_id = message.from_user.id
  LOGGER.info(f'EmptyTrash: {user_id}')
  msg = GoogleDrive(user_id).emptyTrash()
  message.reply_text(msg, quote=True)