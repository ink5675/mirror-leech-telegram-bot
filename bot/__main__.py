import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from sys import executable

from telegram import ParseMode
from telegram.ext import CommandHandler
from telegraph import Telegraph
from wserver import start_server_async
from bot import bot, app, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, alive, web, nox, OWNER_ID, AUTHORIZED_CHATS, telegraph_token
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, delete, speedtest, count, leech_settings, search


def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'<b>⏲️বট আপটাইম:</b> <code>{currentTime}</code>\n' \
            f'<b>📀টোটাল ডেস্ক স্পেস:</b> <code>{total}</code>\n' \
            f'<b>🌡️ ব্যবহৃত স্পেস:</b> <code>{used}</code>' \
            f'<b>🔥ফ্রী স্পেস:</b> <code>{free}</code>\n\n' \
            f'<b>📤আপলোড:</b> <code>{sent}</code>\n' \
            f'<b>📥ডাওনলোড:</b> <code>{recv}</code>\n\n' \
            f'<b>🖥️সিপিইউ:</b> <code>{cpuUsage}%</code>' \
            f'<b>💾র‍্যাম:</b> <code>{memory}%</code>' \
            f'<b>📀ডিস্ক:</b> <code>{disk}%</code>'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Owner", "https://t.me/ihnasim")
    buttons.buildbutton("Group", "https://t.me/IH_X_NASIM")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup('You are not authorized user.So you can not use this bot.To use this bot contact bot Owner or join Group.THANK You', context.bot, update, reply_markup)

def restart(update, context):
    restart_message = sendMessage("Restarting...", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.kill()
    process = psutil.Process(web.pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()
    nox.kill()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


help_string_telegraph = f'''<br>
<b>/{BotCommands.HelpxCommand}</b>: বট ব্যাবহারের কমান্ডগুলো জানতে - 
<br><br>
<b>/{BotCommands.MirrorxCommand}</b> [download_url][magnet_link]: মিরর করতে - .<b>/{BotCommands.MirrorxCommand}</b> মিরর সংক্লান্ত সকল তথ্য পেতে - 
<br><br>
<b>/{BotCommands.ZipMirrorxCommand}</b> [download_url][magnet_link]: জিপ ফাইল আকারে মিরর করতে - 
<br><br>
<b>/{BotCommands.UnzipMirrorxCommand}</b> [download_url][magnet_link]: মিরর ফাইল আনজিপ করতে -
<br><br>
<b>/{BotCommands.QbMirrorxCommand}</b> [magnet_link][torrent_file][torrent_file_url]: QB হিসেবে মিরর করতে - , Use <b>/{BotCommands.QbMirrorxCommand} s</b> ডাউনলোডের পূর্বে ফাইল সিলেক্ট করুন - 
<br><br>
<b>/{BotCommands.QbZipMirrorxCommand}</b> [magnet_link][torrent_file][torrent_file_url]: Start mirroring using qBittorrent and upload the file/folder compressed with zip extension
<br><br>
<b>/{BotCommands.QbUnzipMirrorxCommand}</b> [magnet_link][torrent_file][torrent_file_url]: QBitTorrent হিসেবে মিরর করতে এবং archive extensionand থেকে ফাইল/ফোল্ডার এক্সট্র্যাক করতে -
<br><br>
<b>/{BotCommands.LeechxCommand}</b> [download_url][magnet_link]: লিঙ্ক থেকে ফাইল টেলিগ্রামে আপলোড করতে - , Use <b>/{BotCommands.LeechxCommand} s</b> টেলিগ্রামে আপলোড করার পূর্বে ফাইলটি সিলেক্ট করুন - 
<br><br>
<b>/{BotCommands.ZipLeechxCommand}</b> [download_url][magnet_link]: জিপ ফাইল/ফোল্ডার আনজিপ করে টেলিগ্রামে আপলোড করতে - <br><br>
<b>/{BotCommands.UnzipLeechxCommand}</b> [download_url][magnet_link][torent_file]: যেকোনো ফাইল/ফোল্ডার archive extension থেকে এক্সট্র্যাক করে টেলিগ্রামে আপলোড করতে - 
<br><br>
<b>/{BotCommands.QbLeechxCommand}</b> [magnet_link][torrent_file][torrent_file_url]: qBittorrent ব্যবহার করে ফাইল টেলিগ্রামে আপলোড করতে - , Use <b>/{BotCommands.QbLeechCommand1} s</b> কমান্ডের পূর্বে ফাইল সিলেক্ট করুন - 
<br><br>
<b>/{BotCommands.QbZipLeechxCommand}</b> [magnet_link][torrent_file][torrent_file_url]: QBitTorrent হিসেবে টেলিগ্রামে ফাইল/ফোল্ডার আপলোড  এবং extension থেকে ফাইল/ফোল্ডার কমপ্রেস করতে - 
<br><br>
<b>/{BotCommands.QbUnzipLeechxCommand}</b> [magnet_link][torrent_file][torrent_file_url]: যেকোনো archive extensio থেকে QBitTorrent হিসেবে টেলিগ্রামে ফাইল/ফোল্ডার আপলোড করতে - 
<br><br>
<b>/{BotCommands.ClonexCommand}</b> [drive_url][gdtot_url]: যেকোনো জিডিটিওটি কিংবা গুগল ড্রাইভ লিঙ্ক থেকে ফাইল/ফোল্ডার কপি করতে -
<br><br>
<b>/{BotCommands.CountxCommand}</b> [drive_url][gdtot_url]: যেকোনো গুগল ড্রাইভের ফাইল/ফোল্ডার গণনা করতে - 
<br><br>
<b>/{BotCommands.DeletexCommand}</b> [drive_url]: গুগল ড্রাইভ থেকে ফাইল ডিলেট করতে ( শুধুমাত্র এডমিন এবং সাব-এডমিন কমান্ড ব্যবহার করতে পারবে - )
<br><br>
<b>/{BotCommands.WatchxCommand}</b> [yt-dlp supported link]:ফেসবুক,ইউটিউব ইত্যাদি ভিডিও ডাউনলোড করে গুগল ড্রাইভ আপলোড করতে - . Send <b>/{BotCommands.WatchCommand1}</b> আরো সাহায্য পেতে - 
<br><br>
<b>/{BotCommands.ZipWatchxCommand}</b> [yt-dlp supported link]: ফেসবুক,ইউটিউব ইত্যাদি ভিডিও ডাউনলোড করে জিপ হিসেবে গুগল ড্রাইভ আপলোড করতে - 
<br><br>
<b>/{BotCommands.LeechWatchxCommand}</b> [yt-dlp supported link]: ফেসবুক,ইউটিউব ইত্যাদি ভিডিও ডাউনলোড করে টেলিগ্রামে আপলোড করতে - 
<br><br>
<b>/{BotCommands.LeechZipWatchxCommand}</b> [yt-dlp supported link]: ফেসবুক,ইউটিউব ইত্যাদি ভিডিও ডাউনলোড করে জিপ হিসেবে টেলিগ্রামে আপলোড করতে - 
<br><br>
<b>/{BotCommands.LeechSetxCommand}</b>: Leech সেটিং জানতে -
<br><br>
<b>/{BotCommands.SetThumbxCommand}</b>: রিপ্লাই করে থামনাইল সেট করতে - 
<br><br>
<b>/{BotCommands.RssListxCommand}</b>: আর.এস.এস এর সকল Subscriber দের তথ্য জানতে - 
<br><br>
<b>/{BotCommands.RssGetxCommand}</b>: [Title] [Number](last N links): Force fetch এর শেষের N  লিঙ্ক - 
<br><br>
<b>/{BotCommands.RssSubxCommand}</b>: [Title] [Rss Link] f: [filter]: আর.এস.এস এর নতুন Subscribe এর ফীড
<br><br>
<b>/{BotCommands.RssUnSubxCommand}</b>: [Title]:  টাইটেল ব্যবহার করে আর.এস.এস Unubscribe করতে - 
<br><br>
<b>/{BotCommands.RssUnSubAllxCommand}</b>: আর.এস.এস এর সকল ফীড subscriptions রিমভ করতে - 
<br><br>
<b>/{BotCommands.CancelMirrorx}</b>: মিরর ক্যানসেল করতে - 
<br><br>
<b>/{BotCommands.CancelAllxCommand}</b>: সকল মিরর ক্যানসেল করতে - 
<br><br>
<b>/{BotCommands.ListxCommand}</b> [query]: গুগল ড্রাইভ সার্চ করতে - 
<br><br>
<b>/{BotCommands.SearchxCommand}</b> [query]: টরেন্ট ব্যবহার করে এপিআই সার্চ করতে - 
<br>sites: <code>rarbg, 1337x, yts, etzv, tgx, torlock, piratebay, nyaasi, ettv</code><br><br>
<b>/{BotCommands.StatusxCommand}</b>: সকল কাজের তথ্য পেতে - 
<br><br>
<b>/{BotCommands.StatsxCommand}</b>: বটের সকল তথ্য পেতে - 
'''
help = telegraph.create_page(

        title='Mirror-Leech-Bot Help',

        content=help_string_telegraph,

    )["path"]


help_string = f'''
These Commands Are Only For Admin.if you are a unauthorize user don't try this commands.

/{BotCommands.PingxCommand}: Check how long it takes to Ping the Bot

/{BotCommands.AuthorizexCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizexCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersxCommand}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudoxCommand}: Add sudo user (Only Owner)

/{BotCommands.RmSudoxCommand}: Remove sudo users (Only Owner)

/{BotCommands.RestartxCommand}: Restart the bot

/{BotCommands.LogxCommand}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.SpeedxCommand}: Check Internet Speed of the Host

/{BotCommands.ShellxCommand}: Run commands in Shell (Only Owner)

/{BotCommands.ExecHelpxCommand}: Get help for Executor module (Only Owner)
'''

def bot_help(update, context):
    button = button_build.ButtonMaker()
    button.buildbutton("ALL COMMANDS", f"https://telegra.ph/{help}")
    reply_markup = InlineKeyboardMarkup(button.build_menu(1))
    sendMarkup(help_string, context.bot, update, reply_markup)

'''
botcmds = [
        (f'{BotCommands.HelpxCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorxCommand}', 'Start Mirroring'),
        (f'{BotCommands.ZipMirrorxCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorxCommand}','Extract files'),
        (f'{BotCommands.QbMirrorxCommand}','Start Mirroring using qBittorrent'),
        (f'{BotCommands.QbZipMirrorxCommand}','Start mirroring and upload as .zip using qb'),
        (f'{BotCommands.QbUnzipMirrorxCommand}','Extract files using qBitorrent'),
        (f'{BotCommands.ClonexCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountxCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeletexCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchxCommand}','Mirror Youtube-dl support link'),
        (f'{BotCommands.ZipWatchxCommand}','Mirror Youtube playlist link as .zip'),
        (f'{BotCommands.CancelMirrorx}','Cancel a task'),
        (f'{BotCommands.CancelAllxCommand}','Cancel all tasks'),
        (f'{BotCommands.ListxCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusxCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsxCommand}','Bot Usage Stats'),
        (f'{BotCommands.PingxCommand}','Ping the Bot'),
        (f'{BotCommands.RestartxCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.LogxCommand}','Get the Bot Log [owner/sudo only]')
    ]
'''

def main():
    fs_utils.start_cleanup()
    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))
    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
    elif OWNER_ID:
        try:
            text = "<b>Bot Restarted!</b>"
            bot.sendMessage(chat_id=OWNER_ID, text=text, parse_mode=ParseMode.HTML)
            if AUTHORIZED_CHATS:
                for i in AUTHORIZED_CHATS:
                    bot.sendMessage(chat_id=i, text=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            LOGGER.warning(e)
    # bot.set_my_commands(botcmds)
    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()
