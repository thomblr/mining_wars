import main


def draw_board(board):
    for row in board:
        for col in row:
            print(col, end=' ')
        print('')


draw_board(main.game_board['board'])
