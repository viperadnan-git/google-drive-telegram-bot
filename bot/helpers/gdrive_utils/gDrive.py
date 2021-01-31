import os
import re
import json
import logging
from bot import LOGGER
from time import sleep
from tenacity import *
import urllib.parse as urlparse
from bot.config import Messages
from mimetypes import guess_type
from urllib.parse import parse_qs
from bot.helpers.utils import humanbytes
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from bot.helpers.sql_helper import gDriveDB, idsDB


logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)
logging.getLogger('oauth2client.transport').setLevel(logging.ERROR)
logging.getLogger('oauth2client.client').setLevel(logging.ERROR)


class GoogleDrive:
  def __init__(self, user_id):
    self.__G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
    self.__G_DRIVE_BASE_DOWNLOAD_URL = "https://drive.google.com/uc?id={}&export=download"
    self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL = "https://drive.google.com/drive/folders/{}"
    self.__service = self.authorize(gDriveDB.search(user_id))
    self.__parent_id = idsDB.search_parent(user_id)

  def getIdFromUrl(self, link: str):
      if "folders" in link or "file" in link:
          regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
          res = re.search(regex,link)
          if res is None:
              raise IndexError("GDrive ID not found.")
          return res.group(5)
      parsed = urlparse.urlparse(link)
      return parse_qs(parsed.query)['id'][0]

  @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
  def getFilesByFolderId(self, folder_id):
      page_token = None
      q = f"'{folder_id}' in parents"
      files = []
      while True:
          response = self.__service.files().list(supportsTeamDrives=True,
                                                 includeTeamDriveItems=True,
                                                 q=q,
                                                 spaces='drive',
                                                 pageSize=200,
                                                 fields='nextPageToken, files(id, name, mimeType,size)',
                                                 pageToken=page_token).execute()
          for file in response.get('files', []):
              files.append(file)
          page_token = response.get('nextPageToken', None)
          if page_token is None:
              break
      return files


  @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
  def copyFile(self, file_id, dest_id):
      body = {'parents': [dest_id]}
      try:
          res = self.__service.files().copy(supportsAllDrives=True,fileId=file_id,body=body).execute()
          return res
      except HttpError as err:
          if err.resp.get('content-type', '').startswith('application/json'):
              reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
              if reason == 'dailyLimitExceeded':
                 raise IndexError('LimitExceeded')
              else:
                 raise err


  def cloneFolder(self, name, local_path, folder_id, parent_id):
      files = self.getFilesByFolderId(folder_id)
      new_id = None
      if len(files) == 0:
        return self.__parent_id
      for file in files:
        if file.get('mimeType') == self.__G_DRIVE_DIR_MIME_TYPE:
            file_path = os.path.join(local_path, file.get('name'))
            current_dir_id = self.create_directory(file.get('name'))
            new_id = self.cloneFolder(file.get('name'), file_path, file.get('id'), current_dir_id)
        else:
            try:
                self.transferred_size += int(file.get('size'))
            except TypeError:
                pass
            try:
                self.copyFile(file.get('id'), parent_id)
                new_id = parent_id
            except Exception as err:
                return err
      return new_id

  @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
  def create_directory(self, directory_name):
          file_metadata = {
              "name": directory_name,
              "mimeType": self.__G_DRIVE_DIR_MIME_TYPE
          }
          file_metadata["parents"] = [self.__parent_id]
          file = self.__service.files().create(supportsTeamDrives=True, body=file_metadata).execute()
          file_id = file.get("id")
          return file_id

  def clone(self, link):
    self.transferred_size = 0
    try:
      file_id = self.getIdFromUrl(link)
    except (IndexError, KeyError):
      return Messages.INVALID_GDRIVE_URL
    try:
      meta = self.__service.files().get(supportsAllDrives=True, fileId=file_id, fields="name,id,mimeType,size").execute()
      if meta.get("mimeType") == self.__G_DRIVE_DIR_MIME_TYPE:
        dir_id = self.create_directory(meta.get('name'))
        result = self.cloneFolder(meta.get('name'), meta.get('name'), meta.get('id'), dir_id)
        return Messages.COPIED_SUCCESSFULLY.format(meta.get('name'), self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL.format(dir_id), humanbytes(self.transferred_size))
      else:
        file = self.copyFile(meta.get('id'), self.__parent_id)
        return Messages.COPIED_SUCCESSFULLY.format(file.get('name'), self.__G_DRIVE_BASE_DOWNLOAD_URL.format(file.get('id')), humanbytes(int(meta.get('size'))))
    except Exception as err:
      if isinstance(err, RetryError):
        LOGGER.info(f"Total Attempts: {err.last_attempt.attempt_number}")
        err = err.last_attempt.exception()
      err = str(err).replace('>', '').replace('<', '')
      LOGGER.error(err)
      return f"**ERROR:** ```{err}```"


  @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
  def upload_file(self, file_path, mimeType=None):
      mime_type = mimeType if mimeType else guess_type(file_path)[0]
      mime_type = mime_type if mime_type else "text/plain"
      media_body = MediaFileUpload(
          file_path,
          mimetype=mime_type,
          chunksize=150*1024*1024,
          resumable=True
      )
      filename = os.path.basename(file_path)
      filesize = humanbytes(os.path.getsize(file_path))
      body = {
          "name": filename,
          "description": "Uploaded using @UploadGdriveBot",
          "mimeType": mime_type,
      }
      body["parents"] = [self.__parent_id]
      LOGGER.info(f'Upload: {file_path}')
      try:
        uploaded_file = self.__service.files().create(body=body, media_body=media_body, fields='id', supportsTeamDrives=True).execute()
        file_id = uploaded_file.get('id')
        return Messages.UPLOADED_SUCCESSFULLY.format(filename, self.__G_DRIVE_BASE_DOWNLOAD_URL.format(file_id), filesize)
      except HttpError as err:
        if err.resp.get('content-type', '').startswith('application/json'):
          reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
          if reason == 'userRateLimitExceeded' or reason == 'dailyLimitExceeded':
            return Messages.RATE_LIMIT_EXCEEDED_MESSAGE
          else:
            return f"**ERROR:** {reason}"
      except Exception as e:
        return f"**ERROR:** ```{e}```"

  @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
  def checkFolderLink(self, link: str):
    try:
      file_id = self.getIdFromUrl(link)
    except (IndexError, KeyError):
      raise IndexError
    try:
      file = self.__service.files().get(supportsAllDrives=True, fileId=file_id, fields="mimeType").execute()
    except HttpError as err:
      if err.resp.get('content-type', '').startswith('application/json'):
        reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
        if 'notFound' in reason:
          return False, Messages.FILE_NOT_FOUND_MESSAGE.format(file_id)
        else:
          return False, f"**ERROR:** ```{str(err).replace('>', '').replace('<', '')}```"
    if str(file.get('mimeType')) == self.__G_DRIVE_DIR_MIME_TYPE:
      return True, file_id
    else:
      return False, Messages.NOT_FOLDER_LINK

  @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
    retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
  def delete_file(self, link: str):
    try:
      file_id = self.getIdFromUrl(link)
    except (IndexError, KeyError):
      return Messages.INVALID_GDRIVE_URL
    try:
      self.__service.files().delete(fileId=file_id, supportsTeamDrives=True).execute()
      return Messages.DELETED_SUCCESSFULLY.format(file_id)
    except HttpError as err:
      if err.resp.get('content-type', '').startswith('application/json'):
        reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
        if 'notFound' in reason:
          return Messages.FILE_NOT_FOUND_MESSAGE.format(file_id)
        elif 'insufficientFilePermissions' in reason:
          return Messages.INSUFFICIENT_PERMISSONS.format(file_id)
        else:
          return f"**ERROR:** ```{str(err).replace('>', '').replace('<', '')}```"
      
  def emptyTrash(self):
    try:
      self.__service.files().emptyTrash().execute()
      return Messages.EMPTY_TRASH
    except HttpError as err:
      return f"**ERROR:** ```{str(err).replace('>', '').replace('<', '')}```"


  def authorize(self, creds):
    return build('drive', 'v3', credentials=creds, cache_discovery=False)