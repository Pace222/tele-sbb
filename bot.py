#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.


Usage:

```python
python bot.py
```

Press Ctrl-C on the command line to stop the bot.

"""

import logging
import state.state as store

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler
from keys import TELEGRAM_KEY
from solver import *
from telegram import sendP

import state.state as store

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

store.init_db()
conv = {
    "January": "01",
    "February": "02",
    "March": "03",
    "April": "04",
    "May": "05",
    "June": "06",
    "July": "07",
    "August": "08",
    "September": "09",
    "October": "10",
    "November": "11",
    "December": "12"
}
# Stages
CHOOSE_MONTH, CHOOSE_DAY, CHOOSE_INPUT_METH, GIVE_LOC, WAIT_STRING, WAIT_FOR_OTHERS, WAIT_LOC, DEST, TIME = range(9)
location_strings = {}

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

# async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def select_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    keyboard = [ [
        InlineKeyboardButton("Jan", callback_data='select_day'+"Jan"),
        InlineKeyboardButton("Feb", callback_data='select_day'+"Feb"),
        InlineKeyboardButton("Mar", callback_data='select_day'+"Mar"),
        InlineKeyboardButton("Apr", callback_data='select_day'+"Apr"),
        InlineKeyboardButton("May", callback_data='select_day'+"May"),
        InlineKeyboardButton("Jun", callback_data='select_day'+"Jun")],
        [
        InlineKeyboardButton("Jul", callback_data='select_day'+"Jul"),
        InlineKeyboardButton("Aug", callback_data='select_day'+"Aug"),
        InlineKeyboardButton("Sep", callback_data='select_day'+"Sep"),
        InlineKeyboardButton("Oct", callback_data='select_day'+"Oct"),
        InlineKeyboardButton("Nov", callback_data='select_day'+"Nov"),
        InlineKeyboardButton("Dec", callback_data='select_day'+"Dec"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Please select a date:', reply_markup=reply_markup)
    return CHOOSE_DAY

async def select_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    print("eeeee")
    keyboard = [ 
        [
        InlineKeyboardButton("1", callback_data='give_location'+"1"),
        InlineKeyboardButton("2", callback_data='give_location'+"2"),
        InlineKeyboardButton("3", callback_data='give_location'+"3"),
        InlineKeyboardButton("4", callback_data='give_location'+"4"),
        InlineKeyboardButton("5", callback_data='give_location'+"5"),
        ],
        [
        InlineKeyboardButton("6", callback_data='give_location'+"6"),
        InlineKeyboardButton("7", callback_data='give_location'+"7"),
        InlineKeyboardButton("8", callback_data='give_location'+"8"),
        InlineKeyboardButton("9", callback_data='give_location'+"9"),
        InlineKeyboardButton("10", callback_data='give_location'+"10"),
        ],
        [
        InlineKeyboardButton("11", callback_data='give_location'+"11"),
        InlineKeyboardButton("12", callback_data='give_location'+"12"),
        InlineKeyboardButton("13", callback_data='give_location'+"13"),
        InlineKeyboardButton("14", callback_data='give_location'+"14"),
        InlineKeyboardButton("15", callback_data='give_location'+"15"),
        ],
        [
        InlineKeyboardButton("16", callback_data='give_location'+"16"),
        InlineKeyboardButton("17", callback_data='give_location'+"17"),
        InlineKeyboardButton("18", callback_data='give_location'+"18"),
        InlineKeyboardButton("19", callback_data='give_location'+"19"),
        InlineKeyboardButton("20", callback_data='give_location'+"20"),
        ],
        [
        InlineKeyboardButton("21", callback_data='give_location'+"21"),
        InlineKeyboardButton("22", callback_data='give_location'+"22"),
        InlineKeyboardButton("23", callback_data='give_location'+"23"),
        InlineKeyboardButton("24", callback_data='give_location'+"24"),
        InlineKeyboardButton("25", callback_data='give_location'+"25"),
        ],
        [
        InlineKeyboardButton("26", callback_data='give_location'+"26"),
        InlineKeyboardButton("27", callback_data='give_location'+"27"),
        InlineKeyboardButton("28", callback_data='give_location'+"28"),
        InlineKeyboardButton("29", callback_data='give_location'+"29"),
        InlineKeyboardButton("30", callback_data='give_location'+"30"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    planid = str(query.message.chat_id)
    store.set_journey_deadline_month(planid, query.data.split('select_day')[1])
    store.print_all_db()
    await query.edit_message_text(text='Please select a date:', reply_markup=reply_markup)
    return CHOOSE_INPUT_METH

async def plan_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Plans a trip."""
    keyboard = [
        [InlineKeyboardButton("Select Date", callback_data='select_month', pay=True)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print("eyyyy")
    planid = str(update.message.chat_id)
    print(planid)
    store.add_journey_id(planid)
    store.print_all_db()
    await update.message.reply_text('Welcome! Click the button below to select a date:', reply_markup=reply_markup)
    return CHOOSE_MONTH

async def choose_starting_point(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Plans a trip."""
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("Input Gare", callback_data='int_take_string', pay=True),
         InlineKeyboardButton("Send GeoLoc", callback_data='int_take_geo_pos', pay=True)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print("eyyyy")
    planid = str(query.message.chat_id)
    store.set_journey_deadline_day(planid, query.data.split('give_location')[1])
    store.print_all_db()
    await query.edit_message_text('Where are you going from ?', reply_markup=reply_markup)
    return GIVE_LOC

async def int_take_string(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    await update.callback_query.edit_message_text("Where are you:")
    return WAIT_STRING

async def take_string(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    location_strings[update.message.from_user.id] = update.message.text
    store.join_journey(update.message.from_user.id, str(update.message.chat_id), update.message.text, car=False, car_capacity=1)
    store.print_all_db()
    await update.message.reply_text("Send me dest:")
    return DEST

async def int_take_geo_pos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.edit_message_text("SEEEEEEND ME your LOCAATion:, lets focus on commincatinggggg")
    return WAIT_LOC

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # user = update.message.from_user
    # user_location = update.message.location
    # location_strings[user.id] = user_location
    # print(user_location)
    # print(location_strings)
    store.join_journey(update.message.from_user.id, str(update.message.chat_id), str(update.message.location), car=False, car_capacity=1)
    store.print_all_db()
    await update.message.reply_text("Send me dest:")
    return DEST

async def dest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_dest = update.message.text
    store.set_journey_destination(str(update.message.chat_id), update.message.text)
    store.print_all_db()
    await update.message.reply_text("At what time : (hh:mm) ")
    return TIME

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_time = update.message.text
    store.set_journey_deadline_time(str(update.message.chat_id), user_time)
    store.print_all_db()
    return ConversationHandler.END

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.edit_message_text(text="next time")
    return ConversationHandler.END

WAIT_OTHERS, GIVE_LOC_SPEC, WAIT_STRING_SPEC, WAIT_LOC_SPEC, SPEC_END, COMPUTE = range(6)

async def join_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Plans a trip."""
    query = update.message
    keyboard = [
        [InlineKeyboardButton("Input Gare", callback_data='int_take_string_spec', pay=True),
         InlineKeyboardButton("Send GeoLoc", callback_data='int_take_geo_pos_spec', pay=True)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    planid = str(query.chat_id)
    await query.reply_text('Where are you going from ?', reply_markup=reply_markup)
    return GIVE_LOC_SPEC

async def int_take_string_spec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    await update.callback_query.edit_message_text("Where are you:")
    return WAIT_STRING_SPEC

async def take_string_spec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    location_strings[update.message.from_user.id] = update.message.text
    store.join_journey(update.message.from_user.id, str(update.message.chat_id), update.message.text, car=False, car_capacity=1)
    store.print_all_db()
    cnt = store.count_journey_users(str(update.message.chat_id))
    if (cnt >= 3):
        a = solve_planning(str(update.message.chat_id))
        if a is not None:
            plan, train_card = prepare_planning_v1(a)
        await update.message.reply_text(str(plan))
        await update.message.reply_photo(train_card)
    return ConversationHandler.END

async def location_spec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # user = update.message.from_user
    # user_location = update.message.location
    # location_strings[user.id] = user_location
    # print(user_location)
    # print(location_strings)
    store.join_journey(update.message.from_user.id, str(update.message.chat_id), str(update.message.location), car=False, car_capacity=1)
    store.print_all_db()
    cnt = store.count_journey_users(str(update.message.chat_id))
    if (cnt >= 3):
        a = solve_planning(str(update.message.chat_id))
        if a is not None:
            plan, train_card = prepare_planning_v1(a)
        await update.message.reply_text(str(plan))
        await update.message.reply_photo(train_card)
    return ConversationHandler.END

async def int_take_geo_pos_spec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.edit_message_text("SEEEEEEND ME your LOCAATion:, lets focus on commincatinggggg")
    return WAIT_LOC_SPEC

# async def spec_end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     await update.callback_query.edit_message_text("SEEEEEEND ME your LOCAATion:, lets focus on commincatinggggg")
#     return WAIT_LOC_SPEC

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_KEY).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("plan_trip", plan_trip)],
        states={
            CHOOSE_MONTH: [
                CallbackQueryHandler(select_month, pattern="^" + str("select_month")+"*"),
            ],
            CHOOSE_DAY: [
                #CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(select_day, pattern=r'^select_day([A-Za-z]{3})$'),
            ],
            CHOOSE_INPUT_METH: [
                CallbackQueryHandler(choose_starting_point, pattern=r'^give_location(30|[1-9]|[12]\d)$')
            ],
            GIVE_LOC: [
                CallbackQueryHandler(int_take_string, pattern="^"+str("int_take_string")+"$"),
                CallbackQueryHandler(int_take_geo_pos, pattern="^"+str("int_take_geo_pos")+"$")
            ],
            WAIT_STRING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, take_string)
            ],
            WAIT_LOC: [ 
                MessageHandler(filters.LOCATION, location),
            ],
            DEST: [
                MessageHandler(filters.TEXT, dest),
            ],
            TIME: [
                MessageHandler(filters.TEXT, time),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    conv_handler_join = ConversationHandler(
        entry_points=[CommandHandler("join_trip", join_trip)],
        states={
            WAIT_OTHERS: [
                CallbackQueryHandler(select_month, pattern="^" + str("select_month") + "$"),
            ],
            GIVE_LOC_SPEC:[
                CallbackQueryHandler(int_take_string_spec, pattern="^"+str("int_take_string_spec")+"$"),
                CallbackQueryHandler(int_take_geo_pos_spec, pattern="^"+str("int_take_geo_pos_spec")+"$")
            ],
            WAIT_STRING_SPEC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, take_string_spec)
            ],
            WAIT_LOC_SPEC: [ 
                MessageHandler(filters.LOCATION, location_spec),
            ],
            COMPUTE: [

            ]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_join)

    store.init_db()

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
