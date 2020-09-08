from pyrogram import Client, filters
from bot.config import BotCommands, Messages
from bot.helpers.utils import CustomFilters
from bot.helpers.gdrive_utils import GoogleDrive
from bot.helpers.sql_helper import idsDB
from bot import LOGGER

@Client.on_message(filters.private & filters.incoming & filters.command(BotCommands.SetFolder) & CustomFilters.auth_users)
def _set_parent(client, message):
  user_id = message.from_user.id
  if len(message.command) > 1:
    link = message.command[1]
    if not 'clear' in link:
      sent_message = message.reply_text('🕵️**Checking Link...**', quote=True)
      gdrive = GoogleDrive(user_id)
      try:
        result, file_id = gdrive.checkFolderLink(link)
        if result:
          idsDB._set(user_id, file_id)
          LOGGER.info(f'SetParent:{user_id}: {file_id}')
          sent_message.edit(Messages.PARENT_SET_SUCCESS.format(file_id, BotCommands.SetFolder[0]))
        else:
          sent_message.edit(file_id)
      except IndexError:
        sent_message.edit(Messages.INVALID_GDRIVE_URL)
    else:
      idsDB._clear(user_id)
      message.reply_text(Messages.PARENT_CLEAR_SUCCESS, quote=True)
  else:
    message.reply_text(Messages.CURRENT_PARENT.format(idsDB.search_parent(user_id), BotCommands.SetFolder[0]), quote=True)