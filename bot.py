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

import state.state as store

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

store.init_db()

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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def select_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    print("eeeee")
    keyboard = [ [
        InlineKeyboardButton("Jan", callback_data='select_day'),
        InlineKeyboardButton("Feb", callback_data='select_day'),
        InlineKeyboardButton("Mar", callback_data='select_day'),
        InlineKeyboardButton("Apr", callback_data='select_day'),
        InlineKeyboardButton("May", callback_data='select_day'),
        InlineKeyboardButton("Jun", callback_data='select_day')],
        [
        InlineKeyboardButton("Jul", callback_data='select_day'),
        InlineKeyboardButton("Aug", callback_data='select_day'),
        InlineKeyboardButton("Sep", callback_data='select_day'),
        InlineKeyboardButton("Oct", callback_data='select_day'),
        InlineKeyboardButton("Nov", callback_data='select_day'),
        InlineKeyboardButton("Dec", callback_data='select_day'),
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
        InlineKeyboardButton("1", callback_data='give_location'),
        InlineKeyboardButton("2", callback_data='give_location'),
        InlineKeyboardButton("3", callback_data='give_location'),
        InlineKeyboardButton("4", callback_data='give_location'),
        InlineKeyboardButton("5", callback_data='give_location'),
        ],
        [
        InlineKeyboardButton("6", callback_data='give_location'),
        InlineKeyboardButton("7", callback_data='give_location'),
        InlineKeyboardButton("8", callback_data='give_location'),
        InlineKeyboardButton("9", callback_data='give_location'),
        InlineKeyboardButton("10", callback_data='give_location'),
        ],
        [
        InlineKeyboardButton("11", callback_data='give_location'),
        InlineKeyboardButton("12", callback_data='give_location'),
        InlineKeyboardButton("13", callback_data='give_location'),
        InlineKeyboardButton("14", callback_data='give_location'),
        InlineKeyboardButton("15", callback_data='give_location'),
        ],
        [
        InlineKeyboardButton("16", callback_data='give_location'),
        InlineKeyboardButton("17", callback_data='give_location'),
        InlineKeyboardButton("18", callback_data='give_location'),
        InlineKeyboardButton("19", callback_data='give_location'),
        InlineKeyboardButton("20", callback_data='give_location'),
        ],
        [
        InlineKeyboardButton("21", callback_data='give_location'),
        InlineKeyboardButton("22", callback_data='give_location'),
        InlineKeyboardButton("23", callback_data='give_location'),
        InlineKeyboardButton("24", callback_data='give_location'),
        InlineKeyboardButton("25", callback_data='give_location'),
        ],
        [
        InlineKeyboardButton("26", callback_data='give_location'),
        InlineKeyboardButton("27", callback_data='give_location'),
        InlineKeyboardButton("28", callback_data='give_location'),
        InlineKeyboardButton("29", callback_data='give_location'),
        InlineKeyboardButton("30", callback_data='give_location'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text='Please select a date:', reply_markup=reply_markup)
    return CHOOSE_INPUT_METH

async def plan_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Plans a trip."""
    keyboard = [
        [InlineKeyboardButton("Select Date", callback_data='select_month', pay=True)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    print("eyyyy")
    planid = update.message.media_group_id
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
    await query.edit_message_text('Where are you going from ?', reply_markup=reply_markup)
    return GIVE_LOC

async def int_take_string(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Echo the user message."""
    await update.callback_query.edit_message_text("Where are you:")
    return WAIT_STRING

async def take_string(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    location_strings[update.message.from_user.id] = update.message.text
    
    print(location_strings)
    await update.message.reply_text("Send me dest:")
    return DEST

async def int_take_geo_pos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.edit_message_text("SEEEEEEND ME your LOCAATion:, lets focus on commincatinggggg")
    return WAIT_LOC

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_location = update.message.location
    location_strings[user.id] = user_location
    print(user_location)
    print(location_strings)
    await update.message.reply_text("Send me dest:")
    return DEST

async def dest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_dest = update.message.text
    await update.message.reply_text("At what time : (hh:mm) ")
    return TIME

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_time = update.message.text
    return ConversationHandler.END

# async def manage_loc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Plans a trip."""
#     query = update.callback_query
#     keyboard = [
#         [InlineKeyboardButton("Input Gare", callback_data='manage_loc', pay=True),
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     print("eyyyy")
#     await query.edit_message_text('Where are you going from ?', reply_markup=reply_markup)
#     return WAIT_STRING

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.edit_message_text(text="next time")
    return ConversationHandler.END


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
                CallbackQueryHandler(select_month, pattern="^" + str("select_month") + "$"),
                #CallbackQueryHandler(two, pattern="^" + str(TWO) + "$"),
                #CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                #CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            CHOOSE_DAY: [
                #CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(select_day, pattern="^" + str("select_day") + "$"),
            ],
            CHOOSE_INPUT_METH: [
                CallbackQueryHandler(choose_starting_point, pattern="^"+str("give_location")+"$")
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
            WAIT_FOR_OTHERS: [
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    store.init_db()

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()