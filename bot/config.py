class Config:
    BOT_TOKEN = ""
    APP_ID = ""
    API_HASH = ""
    DATABASE_URL = ""
    SUDO_USERS = ""  # Separated by space.
    SUPPORT_CHAT_LINK = ""
    DOWNLOAD_DIRECTORY = "./downloads/"
    G_DRIVE_CLIENT_ID = ""
    G_DRIVE_CLIENT_SECRET = ""


class BotCommands:
    Download = ['download', 'dl']
    Authorize = ['auth', 'authorize']
    SetFolder = ['setfolder', 'setfl']
    Revoke = ['revoke']
    Clone = ['copy', 'clone']
    Delete = ['delete', 'del']
    EmptyTrash = ['emptyTrash']
    YtDl = ['ytdl']


class Messages:
    START_MSG = "**Hi there {}.**\n__I'm Google Drive Uploader Bot. You can use me to upload any file/video to Google Drive from a direct link or Telegram Files.__\n__You can know more from /help.__"

    HELP_MSG = [
        ".",
        "**Google Drive Uploader**\n__I can upload files from a direct link or Telegram Files to your Google Drive. All I need is to authenticate me to your Google Drive Account and send a direct download link or Telegram File.__\n\nI have more features... ! Want to know about them? Just walk through this tutorial and read the messages carefully.",
        f"**Authenticating Google Drive**\n__Send the /{BotCommands.Authorize[0]} command and you will receive a URL. Visit the URL and follow the steps, then send the received code here. Use /{BotCommands.Revoke[0]} to revoke your currently logged Google Drive Account.__\n\n**Note: I will not listen to any command or message (except /{BotCommands.Authorize[0]} command) until you authorize me.\nSo, authorization is mandatory!**",
        f"**Direct Links**\n__Send me a direct download link for a file, and I will download it on my server and upload it to your Google Drive Account. You can rename files before uploading to the GDrive Account. Just send me the URL and the new filename separated by ' | '.__\n\n**__Examples:__**\n```https://example.com/AFileWithDirectDownloadLink.mkv | New FileName.mkv```\n\n**Telegram Files**\n__To upload Telegram files to your Google Drive Account, just send me the file, and I will download and upload it to your Google Drive Account. Note: Telegram file downloading is slow, it may take longer for big files.__\n\n**YouTube-DL Support**\n__Download files via youtube-dl.\nUse /{BotCommands.YtDl[0]} (YouTube Link/YouTube-DL Supported site link)__",
        f"**Custom Folder for Upload**\n__Want to upload to a custom folder or to a __ **TeamDrive** __?\nUse /{BotCommands.SetFolder[0]} (Folder URL) to set the custom upload folder.\nAll the files will be uploaded in the custom folder you provide.__",
