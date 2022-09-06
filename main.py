from pyrogram import Client, filters
import json
from decouple import config
from src.const import *
from src.methods import *
from src.sql import *
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,

)


print("1")
app = Client(
    config("session_name"),
    api_id = int(config("api_id")),
    api_hash = config("api_hash"),
    bot_token = config("bot_token"),
)

print("2")
with app:
    print("Started ...!")
    app.send_message(int(config("admin_id")), "Started ...!")



@app.on_message(filters.command("start", ["/"]))
async def me(client, message):
    await message.reply(
        """سلام،\nخوش اومدی!\n برای شروع بازی روی دکمه ی زیر کلیک کن و چت یا پیوی دوستت رو انتخاب کن.
        
روش بازی :

برای شروع، چهار مهره مطابق شکل در وسط صفحه به صورت ضربدری، قرار می گیرند. مهره تیره بازی را آغاز می کند. هر یک از دو بازیکن به نوبت یک حرکت انجام می‌دهند. مهره را جایی قرار دهید که یک یا چند مهره حریف را محاصره کند. انجام حرکت به معنی گذاشتن یک مهره (از طرف رنگ خود) در صفحه و محصور کردن یک یا چند مهره حریف در یک یا چند راستا است. در نتیجه مهره‌های محاصره شده را برگردانده و به رنگ مهره خود درآورید. این به معنی محاصره و تصاحب است. البته مهره هایی که در جریان بازی در بین مهره های شما قرار میگیرن به رنگ مهره های شما تبدیل نمیشن و فقط مهره هایی که در راستا های 8گانه مهره هایی که شما گذاشتین قرار میگیرن به رنگ مهره های شما در میان. هدف داشتن بیشترین مهره رنگ خود روی صفحه در پایان بازی است.

پایان بازی:

وقتی تمام صفحه پر شود و یا هیچ کدام از دو طرف حرکتی نداشته باشند، بازی به پایان می‌رسد و بازیکنی که تعداد مهره‌های بیشتری روی صفحه بازی داشته باشد برنده می‌باشد.

قوانین:

مهره را جایی قرار دهید که یک یا چند مهره حریف را محاصره کند. یعنی مهره قرار داده شده تعدادی از مهره های حریف را بین مهره جدید و مهره هم رنگ شما در صفحه محاصره کند سپس مهره های محاصره شده را چرخانده و به رنگ مهره خود درآورید.این به معنی محاصره و تصاحب است.
قرار دادن مهره در صفحه به صورت نوبتی انجام می گیرد.
مهره جدید را فقط در محلی می توان قرار داد که مهره ای از حریف محاصره شود. به عبارتی مهره ای به صورت آزاد در صفحه نمی تواند وجود داشته باشد و همه مهره ها حتما در مجاورت مهره های دیگر هستند.
خط محاصره می تواند افقی یا عمودی یا مورب یا هر سه باشد
فقط مهره هایی را می توان تصاحب کرد که بین مهره جدید و مهره قبلی موجود در صفحه محاصره شده باشند
در صورتی یکی از بازیکنان در نوبت خود، مکانی برای محاصره حریف نداشته باشد و نتواند حتی یک مهره او را محاصره کند، در این صورت حرکت به حریف واگذار می شود. تا زمانی که امکان محاصره برایش ایجاد شود.
در پایان بازیکنی که تعداد مهره های بیشتری روی صفحه بازی داشته باشد، برنده است.""",
        reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "انتخاب دوست ...",
                            switch_inline_query="start"
                        ),
                    ]
                ]
            )
    )


@app.on_callback_query(filters.regex("strat-*"))  
async def answer(client, callback_query):
    enemy_id = int(callback_query.data.split("-")[1])
    enemy_name = callback_query.data.split("-")[2]
    my_id = callback_query.from_user.id
    if enemy_id == my_id:
        await callback_query.answer("شما نمی توانید با خودتان بازی کنید.",show_alert=True)
    else:
        keyboard = create_board(my_id, enemy_id, callback_query.from_user.first_name, enemy_name)
        obj = json.loads(str(keyboard))
        manage.insert_into_db(callback_query.inline_message_id, callback_query.chat_instance, callback_query.from_user.first_name, enemy_name, obj)
        await callback_query.edit_message_text("🔍 هر کی خونه های بیشتری رو تصاحب کنه برندست.",reply_markup=keyboard)
    manage.delete_obj_all()

@app.on_callback_query(filters.regex("[0-9]*-[0-9]*"))  
async def answer(client, callback_query):
    data_sql = manage.get_obj_from_db(callback_query.inline_message_id, callback_query.chat_instance)
    board = data_sql[4]['inline_keyboard']
    row_selected, col_selected = list(map(int,callback_query.data.split("-")))
    callback_query_data_text = board[row_selected][col_selected]['text']
    turn = board[8][0]['text']
    next_turn = blue if turn == red else red
    
    if callback_query_data_text == white:
        await callback_query.answer("شما نميتوانيد در اين خانه مهره بگذاريد.",show_alert=True)
    elif callback_query_data_text in [red, blue]:
        await callback_query.answer("اين خانه قبلاً پر شده است.",show_alert=True)
    elif callback_query_data_text == yellow:
        red_id = int(board[9][0]['callback_data'])
        blue_id = int(board[9][1]['callback_data'])
        if (turn == red and callback_query.from_user.id != red_id) or (turn == blue and callback_query.from_user.id != blue_id) :
            await callback_query.answer("نوبت شما نیست.",show_alert=False)
            return 
            
        # update keyboard before calculating possible blocks
        board[row_selected][col_selected]['text'] = turn

        all_reverse_board = calculate_reverse(board, row_selected, col_selected, turn)

        # calculate possible blocks
        possible_squares = possible_blocks(all_reverse_board, next_turn) 

        keyboard_update = update_board(
                board,
                possible_squares,
                row_selected, 
                col_selected, 
                next_turn,
                data_sql[2],
                data_sql[3]
                )
        if len(possible_squares) == 0:
            keyboard_update = who_wins(
                    board,
                    possible_squares,
                    row_selected, 
                    col_selected, 
                    next_turn,
                    data_sql[2],
                    data_sql[3]
                    )    
            manage.delete_obj(callback_query.inline_message_id, callback_query.chat_instance)

        obj = json.loads(str(keyboard_update))
        manage.update_keyboard(callback_query.inline_message_id, callback_query.chat_instance, obj) 
        await callback_query.edit_message_reply_markup(keyboard_update)


@app.on_inline_query()
async def answer(client, inline_query):
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="🕹 بازی اوتلو دونفره 🕹",
                input_message_content=InputTextMessageContent("رو دکمه ی 'من پایم! 🖐' کلیک کن تا همین الان بازی اوتلو رو شروع کنیم!"),
                description="🎮 برای مبارزه طلبی اینجا بزن 🎮",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton( "من پایم! 🖐",callback_data=f"strat-{inline_query.from_user.id}-{inline_query.from_user.first_name}")]]) 
            ),
        ],
        cache_time=0
    )

app.run()
