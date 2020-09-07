from pyrogram import Client, filters
from bot.config import BotCommands, Messages
from bot.helpers.gdrive_utils import GoogleDrive
from bot.helpers.utils import CustomFilters


@Client.on_message(filters.private & filters.incoming & filters.command(BotCommands.Delete) & CustomFilters.auth_users)
def _delete(client, message):
  user_id = message.from_user.id
  if len(message.command) > 1:
    sent_message = message.reply_text('**Checking Link...**', quote=True)
    link = message.command[1]
    result = GoogleDrive(user_id).delete_file(link)
    sent_message.edit(result)
  else:
    message.reply_text(Messages.PROVIDE_GDRIVE_URL.format(BotCommands.Delete[0]), quote=True)