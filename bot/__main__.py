import signal
import os

from os import path as ospath, remove as osremove, execl as osexecl
from subprocess import run as srun
from asyncio import run as asyrun
from psutil import disk_usage, cpu_percent, swap_memory, cpu_count, virtual_memory, net_io_counters, Process as psprocess
from time import time
from pyrogram import idle
from sys import executable
from telegram import ParseMode, InlineKeyboardMarkup
from telegram.ext import CommandHandler

from wserver import start_server_async
from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, alive, web, OWNER_ID, AUTHORIZED_CHATS, LOGGER, Interval, nox, rss_session, a2c
from .helper.ext_utils.fs_utils import start_cleanup, clean_all, exit_clean_up
from .helper.telegram_helper.bot_commands import BotCommands
from .helper.telegram_helper.message_utils import sendMessage, sendMarkup, editMessage, sendLogFile
from .helper.ext_utils.telegraph_helper import telegraph
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from .helper.telegram_helper.button_build import ButtonMaker
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, delete, speedtest, count, leech_settings, search, rss


def stats(update, context):
    currentTime = get_readable_time(time() - botStartTime)
    total, used, free, disk= disk_usage('/')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    cpuUsage = cpu_percent(interval=0.5)
    p_core = cpu_count(logical=False)
    t_core = cpu_count(logical=True)
    swap = swap_memory()
    swap_p = swap.percent
    swap_t = get_readable_file_size(swap.total)
    swap_u = get_readable_file_size(swap.used)
    memory = virtual_memory()
    mem_p = memory.percent
    mem_t = get_readable_file_size(memory.total)
    mem_a = get_readable_file_size(memory.available)
    mem_u = get_readable_file_size(memory.used)
    stats = f'<b>⏲️আপটাইম⏲️:</b> {currentTime}\n\n'\
            f'<b>📀টোটাল ডিস্কস্পেস📀:</b> {total}\n'\
            f'<b>🗃️ব্যাবহৃত🗃️:</b> {used} | <b>🗑️খালি জায়গা🗑️:</b> {free}\n\n'\
            f'<b>📤আপলোড📤</b> {sent}\n'\

    

            f'<b>📩ডাউনলোড📩:</b> {recv}\n\n'\
            f'<b>🖥️সিপিইউ 🖥️:</b> {cpuUsage}%\n'\
            f'<b>💾র‍্যাম💾:<b> {mem_p}%\n'\
            f'<b>DISK:</b> {disk}%\n\n'\
            f'<b>Physical Cores:</b> {p_core}\n'\
            f'<b>Total Cores:</b> {t_core}\n\n'\
            f'<b>SWAP:</b> {swap_t} | <b>Used:</b> {swap_p}%\n'\
            f'<b>Memory Total:</b> {mem_t}\n'\
            f'<b>Memory Free:</b> {mem_a}\n'\
            f'<b>Memory Used:</b> {mem_u}\n'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = ButtonMaker()
    buttons.buildbutton("Channel", "https://t.me/ihnasim")
    buttons.buildbutton("Report Group", "https://t.me/ihnasim90")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup('Not Authorized user, deploy your own mirror-leech bot', context.bot, update, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update)
    if Interval:
        Interval[0].cancel()
    alive.kill()
    procs = psprocess(web.pid)
    for proc in procs.children(recursive=True):
        proc.kill()
    procs.kill()
    clean_all()
    srun(["python3", "update.py"])
    nox.kill()
    a2cproc = psprocess(a2c.pid)
    for proc in a2cproc.children(recursive=True):
        proc.kill()
    a2cproc.kill()
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    osexecl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.Help1Command}</b>: To get this message
<br><br>
<b>/{BotCommands.Mirror1Command}</b> [download_url][magnet_link]: Start mirroring to Google Drive. Send <b>/{BotCommands.MirrorCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipMirror1Command}</b> [download_url][magnet_link]: Start mirroring and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.UnzipMirror1Command}</b> [download_url][magnet_link]: Start mirroring and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.QbMirror1Command}</b> [magnet_link][torrent_file][torrent_file_url]: Start Mirroring using qBittorrent, Use <b>/{BotCommands.QbMirrorCommand} s</b> to select files before downloading
<br><br>
<b>/{BotCommands.QbZipMirror1Command}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipMirror1Command}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.Leech1Command}</b> [download_url][magnet_link]: Start leeching to Telegram, Use <b>/{BotCommands.LeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.ZipLeech1Command}</b> [download_url][magnet_link]: Start leeching to Telegram and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.UnzipLeech1Command}</b> [download_url][magnet_link][torent_file]: Start leeching to Telegram and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.QbLeech1Command}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent, Use <b>/{BotCommands.QbLeechCommand} s</b> to select files before leeching
<br><br>
<b>/{BotCommands.QbZipLeech1Command}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipLeech1Command}</b> [magnet_link][torrent_file][torrent_file_url]: Start leeching to Telegram using qBittorrent and upload the file/folder extracted from any archive extension
<br><br>
<b>/{BotCommands.Clone1Command}</b> [drive_url][gdtot_url]: Copy file/folder to Google Drive
<br><br>
<b>/{BotCommands.Count1Command}</b> [drive_url][gdtot_url]: Count file/folder of Google Drive
<br><br>
<b>/{BotCommands.Delete1Command}</b> [drive_url]: Delete file/folder from Google Drive (Only Owner & Sudo)
<br><br>
<b>/{BotCommands.Watch1Command}</b> [yt-dlp supported link]: Mirror yt-dlp supported link. Send <b>/{BotCommands.WatchCommand}</b> for more help
<br><br>
<b>/{BotCommands.ZipWatch1Command}</b> [yt-dlp supported link]: Mirror yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechWatch1Command}</b> [yt-dlp supported link]: Leech yt-dlp supported link
<br><br>
<b>/{BotCommands.LeechZip1WatchCommand}</b> [yt-dlp supported link]: Leech yt-dlp supported link as zip
<br><br>
<b>/{BotCommands.LeechSet1Command}</b>: Leech settings
<br><br>
<b>/{BotCommands.SetThumb1Command}</b>: Reply photo to set it as Thumbnail
<br><br>
<b>/{BotCommands.RssList1Command}</b>: List all subscribed rss feed info
<br><br>
<b>/{BotCommands.RssGet1Command}</b>: [Title] [Number](last N links): Force fetch last N links
<br><br>
<b>/{BotCommands.RssSub1Command}</b>: [Title] [Rss Link] f: [filter]: Subscribe new rss feed
<br><br>
<b>/{BotCommands.RssUnSub1Command}</b>: [Title]: Unubscribe rss feed by title
<br><br>
<b>/{BotCommands.RssUnSubAll1Command}</b>: Remove all rss feed subscriptions
<br><br>
<b>/{BotCommands.Cancel1Mirror}</b>: Reply to the message by which the download was initiated and that download will be cancelled
<br><br>
<b>/{BotCommands.CancelAll1Command}</b>: Cancel all downloading tasks
<br><br>
<b>/{BotCommands.List1Command}</b> [query]: Search in Google Drive(s)
<br><br>
<b>/{BotCommands.Search1Command}</b> [query]: Search for torrents with API
<br>sites: <code>rarbg, 1337x, yts, etzv, tgx, torlock, piratebay, nyaasi, ettv</code><br><br>
<b>/{BotCommands.Status1Command}</b>: Shows a status of all the downloads
<br><br>
<b>/{BotCommands.Stats1Command}</b>: Show Stats of the machine the bot is hosted on
'''

help = telegraph.create_page(
        title='IH NASIM BoT',
        content=help_string_telegraph,
    )["path"]

help_string = f'''
/{BotCommands.Ping1Command}: Check how long it takes to Ping the Bot

/{BotCommands.Authorize1Command}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorize1Command}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsers1Command}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudo1Command}: Add sudo user (Only Owner)

/{BotCommands.RmSudo1Command}: Remove sudo users (Only Owner)

/{BotCommands.Restart1Command}: Restart and update the bot

/{BotCommands.Log1Command}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.Speed1Command}: Check Internet Speed of the Host

/{BotCommands.Shell1Command}: Run commands in Shell (Only Owner)

/{BotCommands.ExecHelp1Command}: Get help for Executor module (Only Owner)
'''

def bot_help(update, context):
    button = ButtonMaker()
    button.buildbutton("অন্যান্য কমান্ড", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

botcmds = [

        (f'{BotCommands.Mirror1Command}', 'Mirror'),
        (f'{BotCommands.ZipMirror1Command}','Mirror and upload as zip'),
        (f'{BotCommands.UnzipMirror1Command}','Mirror and extract files'),
        (f'{BotCommands.QbMirror1Command}','Mirror torrent using qBittorrent'),
        (f'{BotCommands.QbZipMirror1Command}','Mirror torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipMirror1Command}','Mirror torrent and extract files using qb'),
        (f'{BotCommands.Watch1Command}','Mirror yt-dlp supported link'),
        (f'{BotCommands.ZipWatch1Command}','Mirror yt-dlp supported link as zip'),
        (f'{BotCommands.Clone1Command}','Copy file/folder to Drive'),
        (f'{BotCommands.Leech1Command}','Leech'),
        (f'{BotCommands.ZipLeech1Command}','Leech and upload as zip'),
        (f'{BotCommands.UnzipLeech1Command}','Leech and extract files'),
        (f'{BotCommands.QbLeech1Command}','Leech torrent using qBittorrent'),
        (f'{BotCommands.QbZipLeech1Command}','Leech torrent and upload as zip using qb'),
        (f'{BotCommands.QbUnzipLeech1Command}','Leech torrent and extract using qb'),
        (f'{BotCommands.LeechWatch1Command}','Leech yt-dlp supported link'),
        (f'{BotCommands.LeechZipWatch1Command}','Leech yt-dlp supported link as zip'),
        (f'{BotCommands.Count1Command}','Count file/folder of Drive'),
        (f'{BotCommands.Delete1Command}','Delete file/folder from Drive'),
        (f'{BotCommands.Cancel1Mirror}','Cancel a task'),
        (f'{BotCommands.CancelAll1Command}','Cancel all downloading tasks'),
        (f'{BotCommands.List1Command}','Search in Drive'),
        (f'{BotCommands.LeechSet1Command}','Leech settings'),
        (f'{BotCommands.SetThumb1Command}','Set thumbnail'),
        (f'{BotCommands.Status1Command}','Get mirror status message'),
        (f'{BotCommands.Stats1Command}','Bot usage stats'),
        (f'{BotCommands.Ping1Command}','Ping the bot'),
        (f'{BotCommands.Restart1Command}','Restart the bot'),
        (f'{BotCommands.Log1Command}','Get the bot Log'),
        (f'{BotCommands.Help1Command}','Get detailed help')
    ]

def main():
    # bot.set_my_commands(botcmds)
    start_cleanup()
    if IS_VPS:
        asyrun(start_server_async(PORT))
    # Check if the bot is restarting
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        osremove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.Log1Command, log1, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, exit_clean_up)
    if rss_session is not None:
        rss_session.start()

app.start()
main()
idle()
