import re
import random
import json
from dotenv import load_dotenv
import os

import telebot
from telebot import types
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    SwitchInlineQueryChosenChat,
    InlineQueryResultsButton,
    ForceReply,
)
from telebot.util import quick_markup


import firebase_admin
from firebase_admin import db

# Quick References:
# https://pytba.readthedocs.io/en/latest/types.html#telebot.types.InlineKeyboardButton
# ref = db.reference('/')
# print(ref.get())
# set example
# ref = db.reference('/user_id')
# ref.set({
# 	"recieve_id":[
# 		{
# 			"question":"question",
# 			"answer":"answer",
# 		}
# 	]
# })
# # update example
# ref = db.reference('/user_id')
# user_qns = ref.get()
# user_qns["recieve_id"][0]["question"] = "new question"
# ref.update(user_qns)
# delete example
# ref.set({})

# def send_KeyboardButton():
# 	markup = types.ReplyKeyboardMarkup()
# 	btn_information = types.KeyboardButton('More Information')
# 	btn_question_deck = types.KeyboardButton('Choose Question Deck')
# 	btn_write_question = types.KeyboardButton('Write Question')
# 	startbtn = types.KeyboardButton('Choose Deck')
# 	markup.row(btn_information, btn_question_deck, btn_write_question)
# 	bot.send_message(chat_id, "PLease Select:", reply_markup=markup)

load_dotenv()
service_account = json.loads(os.getenv("SERVICE_ACCOUNT"))
bot_token = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(bot_token)

# firebase functions
cred_obj = firebase_admin.credentials.Certificate(service_account)
default_app = firebase_admin.initialize_app(
    cred_obj,
    {
        "databaseURL": "https://bumbletele-74895-default-rtdb.asia-southeast1.firebasedatabase.app/"
    },
)

decks = {
    "Relationships": [
        "When did you know you wanted to be in a relationship with me?",
        "What was your first impression of me?",
        "What is your favorite thing about our relationship?",
        "What is your favorite thing about us?",
        "What is your favorite memory of us?",
        "What is your favorite thing that I do for you?",
    ],
    "Casual": [
        "What's your favorite thing to do on a rainy day?",
        "What's your most used Singlish word?",
        "What food can you not live without?",
        "What's a song that describes your life?",
        "What's the funniest nickname someone has for you?",
        "What's your go-to midnight snack?",
        "When did you last stay up all night and why?",
    ],
    "Deep": [
        "What do you think you're reall good at, even if others don't agree?",
        "What's something you've done and will never do again?",
        "If you didn't need to work, what would you be doing?",
        "What are you glad your parents don't know about you?",
        "What's your biggest fear?",
        "What gives you courage?",
        "What's your biggest accomplishment?",
        "What's your biggest pet peeve?",
        "What's your biggest insecurity?",
    ],
    "Couples": [
        "When did you know you wanted to be in a relationship with me?",
        "What was your first impression of me?",
        "What is your favorite thing about our relationship?",
        "What is your favorite thing about us?",
        "What is your favorite memory of us?",
        "What is your favorite thing that I do for you?",
    ],
    "Quiz": [
        "What's my favorite color?",
    ],
}


@bot.message_handler(commands=["start"])
def send_welcome(message):
    payload = None
    if len(message.text.split()) > 1:
        payload = message.text.split()[1]
    print(payload)
    if payload is not None:
        print()
        user_id = payload.split("_")[1]
        query_id = payload.split("_")[0]
        ref = db.reference(f"/{user_id}/{query_id}")
        print(f"user_id: {user_id} query_id: {query_id} ref: {ref.get()}")
        question = ref.get()["question"]
        answer = ref.get()["answer"]
        bot.send_message(
            message.chat.id,
            f"Question: {question}\nPlease reply with your answer to the question to unlock the answer!",
            reply_markup=ForceReply(input_field_placeholder="Your Answer:"),
        )
        bot.set_state(
            message.from_user.id,
            f"unlock_answer|{query_id}|{user_id}|{message.from_user.username}",
        )
    else:
        bot.send_message(
            message.chat.id, "Please Select:", reply_markup=gen_main_menu()
        )


def gen_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Question Deck", callback_data="cb_question_deck"),
        InlineKeyboardButton("Custom Question", callback_data="cb_custom_question"),
        InlineKeyboardButton("Contact/Tutorial", callback_data=("cb_contact")),
    )
    return markup


def gen_question_deck_menu():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for deck in decks.keys():
        random.shuffle(decks[deck])
        markup.add(InlineKeyboardButton(deck, callback_data="cb_deck_" + deck))
    markup.add(InlineKeyboardButton("Back", callback_data="cb_main_menu"))
    return markup


def gen_questions(idx, deck):
    # markup = InlineKeyboardMarkup()
    # markup.row_width = 3
    # markup.add(InlineKeyboardButton("Left", callback_data=f"cb_questions_{idx-1}_{deck}"))
    # markup.add(InlineKeyboardButton("Right", callback_data=f"cb_questions_{idx+1}_{deck}"))
    # markup.add(InlineKeyboardButton("Select", callback_data=f"cb_question_{idx}_{deck}"))
    # markup.add(InlineKeyboardButton("Back", callback_data="cb_question_deck"))

    markup = quick_markup(
        {
            "<": {"callback_data": f"cb_questions_{idx-1}_{deck}"},
            "Select": {"callback_data": f"cb_question_{idx}_{deck}"},
            ">": {"callback_data": f"cb_questions_{idx+1}_{deck}"},
            "Back": {"callback_data": "cb_question_deck"},
        },
        row_width=3,
    )
    return markup


def gen_back_button(state):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(
            "Back",
            callback_data=f"cb_{state}",
        )
    )
    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "cb_main_menu":
        bot.edit_message_text(
            "Please select:",
            reply_markup=gen_main_menu(),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
    elif call.data == "cb_contact":
        bot.edit_message_text(
            "Please contact me at: @junkeai",
            reply_markup=gen_back_button("main_menu"),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
    elif call.data == "cb_question_deck":
        bot.edit_message_text(
            "Please select a question deck:",
            reply_markup=gen_question_deck_menu(),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
    elif call.data == "cb_custom_question":
        bot.edit_message_text(
            "Please type and send your custom question",
            reply_markup=gen_back_button("main_menu"),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
        # state pattern shall be "status,question,answer"
        bot.set_state(call.from_user.id, "custom_question||")
    elif call.data.startswith("cb_deck"):
        deck = call.data.split("_")[2]
        question = decks[deck][0]
        bot.edit_message_text(
            f"Please select a question from the {deck} deck:\n\nQuestion: {question}",
            reply_markup=gen_questions(0, deck),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
    elif call.data.startswith("cb_questions"):
        idx = int(call.data.split("_")[2])
        deck = call.data.split("_")[3]
        if idx > len(decks[deck]) - 1:
            idx = 0
        elif idx < 0:
            idx = len(decks[deck]) - 1
        question = decks[deck][idx]
        bot.edit_message_text(
            f"Please select a question\n\nQuestion: {question}",
            reply_markup=gen_questions(idx, deck),
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
        bot.set_state(call.from_user.id, f"deck_answer|{question}|")
    elif call.data.startswith("cb_question"):
        idx = int(call.data.split("_")[2])
        deck = call.data.split("_")[3]
        question = decks[deck][idx]
        bot.send_message(
            call.message.chat.id,
            f"Question: {question}\n\nPlease Answer!",
            reply_markup=ForceReply(input_field_placeholder="Your Answer:"),
        )
        bot.set_state(call.from_user.id, f"deck_answer|{question}|")
    elif call.data.startswith("cb_reveal_answer"):
        cb_data = call.data.split("_")
        sender_id = cb_data[4]
        query_id = cb_data[3]
        ref = db.reference(f"/{sender_id}/{query_id}")
        data = ref.get()
        requirement = data["requirement"]
        print(data)
        if len(data["replies"]) >= requirement:
            reply = f"\nQuestion: {data['question']}\n\n@{sender_id}'s answer: {data['answer']}"
            for reply_id in data["replies"]:
                reply += f"\n\n@{reply_id}'s answer: {data['replies'][reply_id]}"
            reply += "\n\nTalk to @bumble_tele_bot to ask more questions!"
            bot.edit_message_text(reply, inline_message_id=call.inline_message_id)
        else:
            count = len(data["replies"])
            bot.edit_message_text(
                f"Question: {data['question']}\n\n@{sender_id}'s answer: Locked 🔐\n{requirement-count} more answer(s) needed to unlock!\n\nTalk to @bumble_tele_bot to ask more questions!",
                inline_message_id=call.inline_message_id,
                reply_markup=gen_reveal_answer(query_id, sender_id),
            )
        pass


def send_private_chat(question_answer_requirement):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(
            "Select chat to send question",
            switch_inline_query=question_answer_requirement,
        )
    )
    return markup


@bot.message_handler(func=lambda message: True, content_types=["text"])
def handle_message(message):
    state = bot.get_state(message.from_user.id)
    status = state.split("|")[0]
    if status == "custom_answer":
        question = state.split("|")[1]
        answer = message.text
        bot.send_message(
            message.chat.id,
            f"Please state the number of required answers to unlock your answer!",
        )
        # bot.send_message(message.chat.id, "IMPORTANT!!\n\nAfter chat selection, DO NOT send message directly. Wait for a popup to load and click the popup!")
        # bot.send_message(message.chat.id, f"Question: {question}\n\nAnswer: {answer}\n\nPlease select a chat to send the question to!\n\n",
        # reply_markup=send_private_chat(f"{question}_{answer}"))
        bot.set_state(message.from_user.id, f"lock_requirement|{question}|{answer}")
    elif status == "custom_question":
        bot.send_message(
            message.chat.id,
            f"Question: {message.text}\n\nPlease reply with your answer to the question!",
            reply_markup=ForceReply(input_field_placeholder="Your Answer:"),
        )
        bot.set_state(message.from_user.id, f"custom_answer|{message.text}|")
    elif status == "deck_answer":
        question = state.split("|")[1]
        answer = message.text
        bot.send_message(
            message.chat.id,
            f"Please state the number of answers required to unlock the answer!",
        )
        bot.set_state(message.from_user.id, f"lock_requirement|{question}|{answer}")
    elif status == "lock_requirement":
        question = state.split("|")[1]
        answer = state.split("|")[2]
        lock_requirement = message.text
        bot.send_message(
            message.chat.id,
            "IMPORTANT!!\n\nAfter chat selection, DO NOT send message directly. Wait for a popup to load and click the popup!",
        )
        bot.send_message(
            message.chat.id,
            f"Question: {question}\nAnswer: {answer}",
            reply_markup=send_private_chat(f"{question}_{answer}_{lock_requirement}"),
        )
        bot.set_state(message.from_user.id, f"|{question}|{answer}")
    elif status == "unlock_answer":
        query_id = state.split("|")[1]
        user_id = state.split("|")[2]
        sender_id = state.split("|")[3]
        given_answer = message.text
        ref = db.reference(f"/{user_id}/{query_id}/replies")
        ref.update({sender_id: given_answer})
        bot.send_message(
            message.chat.id,
            f"Answer submitted! Go back to the chat and click 'Reveal Answer' to check @{user_id}'s answer!",
        )
        bot.set_state(message.from_user.id, f"main_menu||")
    pass


# not sure if id is unique even if the params is the same. Currently used to identify the reciever
def gen_reveal_answer(query_id, sender_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(
            "Reveal Answer", callback_data=f"cb_reveal_answer_{query_id}_{sender_id}"
        )
    )
    markup.add(
        InlineKeyboardButton(
            "Answer Question",
            switch_inline_query_current_chat=f"answer_question_{query_id}_{sender_id}",
        )
    )
    return markup


# https://pytba.readthedocs.io/en/latest/types.html#telebot.types.InlineQuery
@bot.inline_handler(lambda query: query.query.startswith("answer_question_"))
def answer_inline_query(inline_query):
    try:
        query_id = inline_query.query.split("_")[2]
        sender_id = inline_query.query.split("_")[3]
        bot.answer_inline_query(
            inline_query.id,
            [],
            switch_pm_text="CLICK ME to answer the qn!",
            switch_pm_parameter=f"{query_id}_{sender_id}",
        )

    except Exception as e:
        print(e)


# @bot.inline_handler(lambda query: len(query.query) == 0 )
# https://pytba.readthedocs.io/en/latest/types.html#telebot.types.User
@bot.inline_handler(lambda query: True)
def default_query(inline_query):
    try:
        question = inline_query.query.split("_")[0]
        answer = inline_query.query.split("_")[1]
        requirement = inline_query.query.split("_")[2]
        print("generating inline query")
        print(
            f"question: {question} answer: {answer} inline_query_id: {inline_query.id} from: {inline_query.from_user.username}"
        )
        if question == "":
            question = "random_question()"
        r = types.InlineQueryResultArticle(
            inline_query.id,
            f"CLICK ME to send!",
            types.InputTextMessageContent(
                f"\nQuestion: {question}\n\n@{inline_query.from_user.username}'s answer: Locked 🔐\n{requirement} more answer(s) needed to unlock!\n\nTalk to @bumble_tele_bot to ask more questions!"
            ),
            description="",
            thumbnail_url="https://www.getillustrations.com/packs/circle-flat-illustrations/scenes/_1x/communication,%20security%20_%20lock,%20message,%20chat,%20privacy,%20protection,%20locked,%20conversation_md.png",
            thumbnail_width=70,
            thumbnail_height=70,
            reply_markup=gen_reveal_answer(
                inline_query.id, inline_query.from_user.username
            ),
        )
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)


# https://pytba.readthedocs.io/en/latest/types.html#telebot.types.ChosenInlineResult
@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    ref = db.reference(f"/{chosen_inline_result.from_user.username}")
    # result id is set to be the inline_query_id
    temp = {
        chosen_inline_result.result_id: {
            "question": chosen_inline_result.query.split("_")[0],
            "answer": chosen_inline_result.query.split("_")[1],
            "requirement": int(chosen_inline_result.query.split("_")[2]),
        }
    }
    print(temp)
    ref.set(temp)


bot.infinity_polling()
