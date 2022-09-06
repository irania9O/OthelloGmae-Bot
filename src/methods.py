from src.const import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def in_range(*args):
    for arg in args:
        if arg < 0 or arg > 7:
            return False
    return True

def possible_blocks(board, turn):
    possible_squares = []
    enemy = blue if turn == red else red
    for row in range(8):
        for col in range(8):
            # if we have pice on specific squares
            if board[row][col]['text'] == turn:
                for row_incr, col_incr in [
                (-1, +1), # up-right
                (-1, -1), # up-lefr
                (+1, -1), # down-right
                (+1, +1), # down-left
                (-1, 0), # up
                (0, +1), # left
                (+1, 0), # down
                (0, -1)  # right
                ]:
                    possible_row = row + row_incr
                    possible_col = col + col_incr

                    if in_range(possible_row, possible_col):
                        if board[possible_row][possible_col]['text'] == enemy:
                            row_step = possible_row - row 
                            col_step = possible_col - col

                            for i in range(1,8):
                                c_row = row + i*row_step
                                c_col = col + i*col_step
                                if in_range(c_row, c_col):
                                    if board[c_row][c_col]['text'] == turn:
                                        break
                                    elif board[c_row][c_col]['text'] in [yellow, white]: #empty
                                        if board[c_row-row_step][c_col-col_step]['text'] == enemy:
                                            possible_squares.append((c_row, c_col))
                                            break
                                        else:
                                            break
    return possible_squares

def create_board(my_id, enemy_id, my_name, enemy_name):
    board = [[InlineKeyboardButton(white, callback_data=f"{x}-{i}") for i in range(8)]  for x in range(8)]

    board[3][3] = InlineKeyboardButton(red, callback_data=f"{board[3][3].callback_data}")
    board[4][4] = InlineKeyboardButton(red, callback_data=f"{board[4][4].callback_data}")
    board[3][4] = InlineKeyboardButton(blue, callback_data=f"{board[3][4].callback_data}")
    board[4][3] = InlineKeyboardButton(blue, callback_data=f"{board[4][3].callback_data}")

    board[2][4] = InlineKeyboardButton(yellow, callback_data=f"{board[2][4].callback_data}")
    board[4][2] = InlineKeyboardButton(yellow, callback_data=f"{board[4][2].callback_data}")
    board[3][5] = InlineKeyboardButton(yellow, callback_data=f"{board[3][5].callback_data}")
    board[5][3] = InlineKeyboardButton(yellow, callback_data=f"{board[5][3].callback_data}")

    board.append([InlineKeyboardButton(red, callback_data=f"turn"),InlineKeyboardButton("نوبت:",callback_data=f"turn")])                                                                         

    board.append([InlineKeyboardButton(f"{red} {my_name} 2",callback_data=f"{my_id}"),InlineKeyboardButton(f"{blue} {enemy_name} 2",callback_data=f"{enemy_id}")])            

    return InlineKeyboardMarkup(board)

# tmp_board = callback_query.message.reply_markup.inline_keyboard
def update_board(tmp_board, possible_squares, row_selected, col_selected, next_turn, enemy_name, my_name):
    board_new = [[InlineKeyboardButton(white, callback_data=f"{x}-{i}") for i in range(8)]  for x in range(8)]
    blue_count = 0
    red_count = 0
    for row in range(8):
        for col in range(8):
            piece = tmp_board[row][col]


            if (row, col) in possible_squares:
                board_new[row][col] = InlineKeyboardButton(yellow, callback_data=piece['callback_data'])
            else:
                new_text = white if piece['text'] in [yellow, white] else piece['text']
                board_new[row][col] = InlineKeyboardButton(new_text, callback_data=piece['callback_data'])
                    
            if piece['text'] == red:
                red_count += 1
            elif piece['text'] == blue:
                blue_count += 1

    board_new[row_selected][col_selected] = InlineKeyboardButton(tmp_board[8][0]['text'], callback_data=f"{row_selected}-{col_selected}")
                            
    board_new.append([InlineKeyboardButton(next_turn, callback_data=f"turn"),InlineKeyboardButton("نوبت:",callback_data=f"turn")])                                                                         
    board_new.append([InlineKeyboardButton(f"{red} {my_name} {red_count}",callback_data=tmp_board[9][0]['callback_data']),InlineKeyboardButton(f"{blue} {enemy_name} {blue_count}",callback_data=tmp_board[9][1]['callback_data'])])
    
    return InlineKeyboardMarkup(board_new)


def calculate_reverse(board, row_selected, col_selected, turn):
    enemy = blue if turn == red else red
    for row_incr, col_incr in [
            (-1, +1), # up-right
            (-1, -1), # up-lefr
            (+1, -1), # down-right
            (+1, +1), # down-left
            (-1, 0), # up
            (0, +1), # left
            (+1, 0), # down
            (0, -1)  # right
            ]:
        possible_row = row_selected + row_incr
        possible_col = col_selected + col_incr


        if in_range(possible_row, possible_col):
            if board[possible_row][possible_col]['text'] == enemy:
                row_step = possible_row - row_selected 
                col_step = possible_col - col_selected
                between = []
                for i in range(1,8):
                    c_row = row_selected + i*row_step
                    c_col = col_selected + i*col_step
                    if in_range(c_row, c_col):
                        if board[c_row][c_col]['text'] == enemy:
                            try:
                                if not in_range(c_row+row_step, c_col+col_step):
                                    between.clear()
                                    break
                                if board[c_row+row_step][c_col+col_step]['text'] == enemy:
                                    between.append((c_row, c_col))
                                elif board[c_row+row_step][c_col+col_step]['text'] == turn:
                                    between.append((c_row, c_col))
                                    break
                                elif board[c_row][c_col]['text'] in [yellow, white]:
                                    between.clear()
                                    break
                                else:
                                    between.clear()
                                    break                                 
                            except:
                                    between.clear()
                                    break
 
                for row, col in between:
                    board[row][col]['text'] = turn
    return board

def who_wins(tmp_board, possible_squares, row_selected, col_selected, next_turn, enemy_name, my_name):
    board_new = [[InlineKeyboardButton(white, callback_data=f"{x}-{i}") for i in range(8)]  for x in range(8)]
    blue_count = 0
    red_count = 0
    for row in range(8):
        for col in range(8):
            piece = tmp_board[row][col]

            if (row, col) in possible_squares:
                board_new[row][col] = InlineKeyboardButton(yellow, callback_data=piece['callback_data'])
            else:
                new_text = white if piece['text'] in [yellow, white] else piece['text']
                board_new[row][col] = InlineKeyboardButton(new_text, callback_data=piece['callback_data'])
                    
            if piece['text'] == red:
                red_count += 1
            elif piece['text'] == blue:
                blue_count += 1

    board_new[row_selected][col_selected] = InlineKeyboardButton(tmp_board[8][0]['text'], callback_data=f"{row_selected}-{col_selected}")

    if blue_count > red_count:
        msg = f"{blue} {enemy_name} برند شد."
    elif red_count > blue_count:
        msg = f"{red} {my_name} برند شد."
    else:
        msg = "بازی مساوی شد."

    board_new.append([InlineKeyboardButton(msg, callback_data=f"turn")])                                                                         
    board_new.append([InlineKeyboardButton(f"{red} {my_name} {red_count}",callback_data=f"turn"),InlineKeyboardButton(f"{blue} {enemy_name} {blue_count}",callback_data=f"turn")])
    
    return InlineKeyboardMarkup(board_new)
