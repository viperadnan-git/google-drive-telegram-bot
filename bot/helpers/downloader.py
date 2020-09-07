import wget
from pySmartDL import SmartDL
from urllib.error import HTTPError
from bot import DOWNLOAD_DIRECTORY, LOGGER


def download_file(url, dl_path):
  try:
    dl = SmartDL(url, dl_path, progress_bar=False)
    LOGGER.info(f'Downloading: {link} in {dl_path}')
    dl.start()
    return True, dl.get_dest()
  except HTTPError as error:
    return False, error
  except Exception as error:
    try:
      filename = wget.download(url, dl_path)
      return True, os.path.join(f"{DOWNLOAD_DIRECTORY}/{filename}")
    except HTTPError:
      return False, error