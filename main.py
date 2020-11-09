import telegram
from telegram.ext import MessageHandler, Filters, ConversationHandler, CommandHandler, Updater
import logging
import threading
from datetime import timedelta
import os
import random
import re

TOKEN = "TOKEN"
GREET = "Hello! I\'m Deep Space Insanity Avoidance Bot (DSIABot) and some more unknown shit!\n" + \
        "You can ask for riddles, jokes or just chat around!"
HELP = "\nList of supported commands:\n" + \
       "/help - display all supported commands\n" + \
       "/disconnect - disconnect from the bot\n" + \
       "/alarm <msg> <days> <hours> <minutes> - set an alarm with the message msg: days, hours, and minutes from now\n" + \
       "/courses - get all courses in the database\n" + \
       "/list <course> - list all resources in a course, by course name\n" + \
       "/get - get a document from the database (interactive)\n"


active_users = []


def guess():
    lst = ["It\'s ok", "Everything will be fine", "Hi, i\'m Dbot", "yes", "no", "Fine, and how are you?",
           "I can\'t answer that", "I feel the same", "What a nice day! don\'t you agree?",
           "Well, it is the way it is...", "At the end of the day, aren\'t we all?", "I know", "How are you?",
           "Wanna hear a joke?\n"]
    return random.choice(lst)


def isvalidpath(path):
    try:
        os.path.isdir(path)
        os.path.isfile(path)
        return True
    except:
        return False


def start(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=GREET + HELP)
    if update.effective_user not in active_users:
        active_users.append(update.effective_user)


def handle(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="This command is not supported, type /help for the full list")


def help(update: telegram.Update, context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=HELP)


def disconnect(update: telegram.Update, context: telegram.ext.CallbackContext):
    txt = "Sorry to see you leave " + update.effective_user.full_name
    # remove data...
    if update.effective_user in active_users:
        active_users.remove(update.effective_user)
    context.bot.send_message(chat_id=update.effective_chat.id, text=txt)


def set_alarm(update: telegram.Update, context: telegram.ext.CallbackContext):
    try:
        txt = context.args[0]
        days = float(context.args[1])
        hours = float(context.args[2])
        minutes = float(context.args[3])
        job_queue.run_once(when=timedelta(days=days, hours=hours, minutes=minutes), callback=callback_alarm, context=(
            update.effective_chat.id, "ALARM: " + txt))

    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid parameters, see help for more info")
        print(e)


def callback_alarm(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=context.job.context[0], text=context.job.context[1])


def joke(update: telegram.Update, context: telegram.ext.CallbackContext):
        fd = open(os.getcwd()+"\\resources\\jokes", "r")
        lst = fd.readlines()
        context.bot.send_message(update.effective_chat.id, text=random.choice(lst))
        fd.close()


def riddle(update: telegram.Update, context: telegram.ext.CallbackContext):
    fd = open(os.getcwd() + "\\resources\\riddles", "r")
    lst = fd.readlines()
    rnd = random.randint(0, int(len(lst) / 2 - 1))
    context.bot.send_message(update.effective_chat.id, text=lst[2 * rnd])
    global ans
    ans = lst[2 * rnd + 1]
    ans = ans.split("\n")[0]
    # context.bot.send_message(update.effective_chat.id, text="You have 5 minutes...")
    # job_queue.run_once(when=60 * 5, callback=callback_alarm, context=(update.effective_chat.id,
    #                                                                   "ALARM: " + ans))
    fd.close()
    return "try"


def try_answers(update: telegram.Update, context: telegram.ext.CallbackContext):
    if re.search(ans.lower(), update.message.text.lower()):
        context.bot.send_message(update.effective_chat.id,
                                 text=random.choice(["Correct!", "Excellent!", "Your\'e on fire!"]))
        return "done"
    else:
        if re.search("^.*stop.*|^.*exit.*|^.*quit.*", update.message.text.lower()):
            context.bot.send_message(update.effective_chat.id, text="Oh snap! maybe next time...")
            return "done"
        else:
            context.bot.send_message(update.effective_chat.id,
                                     text=random.choice(["Not quite...", "Try again", "No...", "Hmm...", "Nope..."]))
        return "try"


def interpret(update: telegram.Update, context: telegram.ext.CallbackContext):
    # In the future we'll try to process the language and try to execute commands... (NLP)
    context.bot.send_message(update.effective_chat.id, text=guess())


def courses(update: telegram.Update, context: telegram.ext.CallbackContext):
    try:
        tmp = ""
        for f in os.listdir(os.getcwd() + "\\courses"):
            tmp += f + "\n"
        context.bot.send_message(update.effective_chat.id, text=tmp)
    except Exception as e:
        context.bot.send_message(update.effective_chat.id, text="Sorry, Internal Error Occurred")
        print(e)


def list_course(update: telegram.Update, context: telegram.ext.CallbackContext):
    try:
        course = update.message.text[6:]
        if course not in os.listdir(os.getcwd() + "\\courses"):
            context.bot.send_message(update.effective_chat.id, text="Course " + course + "doesn\'t exist")
        tmp = ""
        for f in os.listdir(os.getcwd() + "\\courses\\" + course):
            tmp += f + "\n"
        context.bot.send_message(update.effective_chat.id, text="Resources of " + course + ":\n" + tmp)
    except Exception as e:
        context.bot.send_message(update.effective_chat.id, text="Sorry, Internal Error Occurred")
        print(e)


def rec_get(update: telegram.Update, context: telegram.ext.CallbackContext):
    global path
    tmp = path
    # assume path is initialized with os.cwd()+"\\courses"
    try:
        path += "\\" + update.message.text
        if isvalidpath(path) and os.path.isfile(path):
            f = open(path, 'rb')
            if update.message.text.split(".")[-1] in ["png", "jpg", "jpeg", "bmp", "gif"]:
                context.bot.send_photo(update.effective_chat.id, photo=f, timeout=60)
            else:
                context.bot.send_document(update.effective_chat.id, document=f, timeout=60)
            f.close()
            return "done"
        else:
            if isvalidpath(path) and update.message.text in os.listdir(tmp):
                path = path
                txt = "Select one of the following:"
            else:
                path = tmp
                txt = "Invalid input\nTry again"
            custom_keyboard = [[]]
            reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
            for f in os.listdir(path):
                custom_keyboard.append([f])
            context.bot.send_message(update.effective_chat.id, text=txt, reply_markup=reply_markup)
            return "rec_get"
    except Exception as e:
        context.bot.send_message(update.effective_chat.id, text="Sorry, Internal Error Occurred")
        print(e)
        return "done"


def init_get(update: telegram.Update, context: telegram.ext.CallbackContext):
    try:
        global path
        path = os.getcwd() + "\\courses"
        custom_keyboard = [[]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        for f in os.listdir(path):
            custom_keyboard.append([f])
        context.bot.send_message(update.effective_chat.id, text="Select one of the following:", reply_markup=reply_markup)
        return "rec_get"
    except Exception as e:
        context.bot.send_message(update.effective_chat.id, text="Sorry, Internal Error Occurred")
        print(e)
        return "done"


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
job_queue = updater.job_queue

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(CommandHandler('disconnect', disconnect))
dispatcher.add_handler(CommandHandler('alarm', set_alarm))
dispatcher.add_handler(CommandHandler('courses', courses))
dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(CommandHandler('list', list_course))
dispatcher.add_handler(MessageHandler(Filters.regex("[jJ]oke\\?*$|[Tt]ell.*[Jj]oke"), joke))
dispatcher.add_handler(ConversationHandler(entry_points=[MessageHandler(Filters.regex(
    ".*[Rr]iddle[\\?!]*$|[Tt]ell.*[Rr]iddle|[Rr]iddle.*a [Rr]iddle"), riddle)],
                                           fallbacks=[CommandHandler('help', help)],
                                           states={"try": [MessageHandler(Filters.text, try_answers)],
                                                   "done": [MessageHandler(Filters.regex(
                                                       ".*[Rr]iddle[\\?!]*$|[Tt]ell.*[Rr]iddle|[Rr]iddle.*a [Rr]iddle"),
                                                       riddle)],
                                                   }))
dispatcher.add_handler(ConversationHandler(entry_points=[CommandHandler('get', init_get)],
                                           fallbacks=[CommandHandler('help', help)],
                                           states={"rec_get": [MessageHandler(Filters.text, rec_get)],
                                                   "done": [CommandHandler('get', init_get)]}))
dispatcher.add_handler(MessageHandler(Filters.text & (~ Filters.command), interpret))


dispatcher.add_handler(MessageHandler(Filters.command, handle))


def shell():
    # a thread for debugging console
    done = False
    while not done:
        cmd = input(">>> ")
        if cmd != "exit()":
            try:
                exec(cmd)
            except Exception as e:
                print(e)
        else:
            done = True


t = threading.Thread(target=shell)
t.start()
updater.start_polling()
