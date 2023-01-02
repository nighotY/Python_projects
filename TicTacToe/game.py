import time
import math
from players import HumanPlayer, ComputerPlayer
class TicTacToe():
    def __init__(self):
        self.board= [' ' for _ in range (9)]  # 3x3 board using single list
        self.current_winner = None

    def print_board(self):                  #print board  
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            print('| '+' |'.join(row)+' |')

    @staticmethod
    def print_board_num():
        #create num_board [0, 1, 2, 3, 4,5,6,7,8]
        number_board = [[str(i) for i in range(j*3, (j+1)*3)] for j in range(3)]
        for row in number_board:
            print('| '+' |'.join(row)+' |')

    def available_moves(self):
        return[i for i, spot in enumerate(self.board) if spot == ' ']
        # moves=[]
        # for i, spot in enumerate(self.board):
        #     if spot == ' '
        #     moves.append(i)
        # return moves
    def empty_squares(self):    #check if any empty square on board
        return ' ' in self.board
    
    def num_empty_squares(self):  # how many empty squares on board
        return self.board.count(' ')

    def make_move(self, square, letter):  
        #if valid move, then make the move (assign square to letter) return true. Else return false
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False
    
    def winner(self, square,letter):
        #winner if 3 in row or diagonally
        #check row
        row_ind = math.floor(square / 3)
        row = self.board[row_ind*3 :(row_ind+1)*3]
        if all([spot == letter for spot in row]):
            return True
        
        #check_column
        col_ind = square % 3
        column = [self.board[col_ind+i*3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        
        #check diagonals (0, 4, 8 or 2, 4, 6 spot)
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0,4,8]] #left to right diagonal
            if all([spot == letter for spot in diagonal1]):
                return True

            diagonal2 = [self.board[i] for i in [2, 4, 6]] #right to left diagonal
            if all([spot == letter for spot in diagonal2]):
                return True

        return False


def playgame(game, x_player, o_player, print_game =True): #if we want computer to play against itself we can set to false, 
    if print_game:
        game.print_board_num()

    letter = "X" #starting letter
    #continue playing while we have available empty squares

    while game.empty_squares():
        #get the move from appropriate player
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)

        #function to make move
        if game.make_move(square,letter):
            if print_game:
                print(letter + f'makes a move to square {square}')
                game.print_board()
                print('')
            if game.current_winner:
                if print_game:
                    print(letter + " Wins!")
                return letter
        #after we made move, we need to alternate letters

            letter = 'O' if letter == 'X' else 'X'
        time.sleep(.8)
    
    if print_game:
        print('It\'s a tie')

if __name__ == '__main__':
    x_player = ComputerPlayer('X')
    o_player = HumanPlayer('O')
    t=TicTacToe()
    playgame(t, x_player, o_player ,print_game=True)