import os
from time import sleep
from pyrogram import Client, filters
from bot.helpers.sql_helper import gDriveDB, idsDB
from bot.helpers.utils import CustomFilters, humanbytes
from bot.helpers.downloader import download_file
from bot.helpers.gdrive_utils import GoogleDrive 
from bot import DOWNLOAD_DIRECTORY, LOGGER
from bot.config import Messages, BotCommands

@Client.on_message(filters.private & filters.incoming & (filters.command(BotCommands.Download) | filters.document | filters.audio | filters.video | filters.photo | filters.regex('^(ht|f)tp*')) & CustomFilters.auth_users)
def _download(client, message):
  user_id = message.from_user.id
  LOGGER.info(f'Download request from {user_id}')
  sent_message = message.reply_text('**Checking link...**', quote=True)
  if not message.media:
    if message.command:
      link = message.command[1]
    else:
      link = message.text
    if '|' in link:
      link, filename = link.split('|')
      link = link.strip()
      filename.strip()
      dl_path = os.path.join(f'{DOWNLOAD_DIRECTORY}/{filename}')
    else:
      link = link.strip()
      filename = os.path.basename(link)
      dl_path = os.path.join(f'{DOWNLOAD_DIRECTORY}/')
    sent_message.edit(Messages.DOWNLOADING.format(filename))
    result, file_path = download_file(link, dl_path)
    if result == False:
      sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))
      return
  elif message.media:
    sent_message.edit(Messages.DOWNLOAD_TG_FILE)
    try:
      file_path = client.download_media(message)
    except FloodWait as e:
      sleep(e.x)
    except Exception as e:
      sent_message.edit(f'**ERROR:** ```{e}```')
      return
  sent_message.edit(Messages.DOWNLOADED_SUCCESSFULLY.format(os.path.basename(file_path), humanbytes(os.path.getsize(file_path))))
  msg = GoogleDrive(user_id).upload_file(file_path)
  sent_message.edit(msg)
  os.remove(file_path)