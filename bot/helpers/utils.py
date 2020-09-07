import re
from pyrogram import filters
from bot.helpers.sql_helper import gDriveDB


class CustomFilters:
    auth_users = filters.create(lambda _, __, message: bool(gDriveDB.search(message.from_user.id)))


def humanbytes(size: int) -> str:
    if not size:
        return ""
    power = 2 ** 10
    number = 0
    dict_power_n = {
        0: " ",
        1: "K",
        2: "M",
        3: "G",
        4: "T",
        5: "P"
    }
    while size > power:
        size /= power
        number += 1
    return str(round(size, 2)) + " " + dict_power_n[number] + 'B'