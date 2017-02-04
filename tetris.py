# Simple tetris program! v0.2
# D. Crandall, Sept 2016
"""
(1) a description of how you formulated the search problem, including precisely defining the state space, the successor
function, the edge weights, and any heuristics you designed
Ans - We have formulated our search problem using genetic algorithm as heuristic for tetris game.
Ref - https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/

Whenever a new piece arrive, we check the min value of row for each column where we can place the piece with all the
rotation possible for that new piece. We calculate 4 parameters to calculate the heuristic.
    1. Aggregate height
    2. Lines cleared by the move
    3. Number of holes, holes are blank spaces such that at least one block is present in rows above it in the same column
    4. Bumpiness, bumpiness is sum of difference between height of each consecutive columns

State space - State space is the board with all possible placement of all the piece with all the rotations
Successor function - Successor function finds all the possible placement for the new piece on the current board with all
the possible rotation of the piece
Heuristic - Calculates the four parameters mentioned above
Edge weight - all the edges have constant weight
Select the state with maximum heuristic value and move.rotate the piece to place it on desired location
The search could be improved by calculating heuristic for all the possible combinations of current piece and next piece, we
have only used current piece as of now.

(2) a brief description of how your search algorithm works
Ans - In the infinite loop until the game ends, we get the current state of the board with new piece and next piece. We
calculate heuristic for each possible placement of the new piece on the board and select the placement with maximum heuristic
value.

(3) a discussion of any problems you faced, any assumptions, simplifications, and/or design decisions you made
Ans - When we calculated all the possible placements, we did not initially consider any collisions before reaching to the
desired row. Hence in many cases state with maximum heuristic was actually not reachable. Hence we had to start from row 0 and
check for collision until desired row to make sure we can reach that state.

Another collision problem appeared when we needed to rotate a piece when it was on edge. So while trying to rotate we were
facing a collision with the wall and rotate function would return without actually rotating the piece. Hence we added a check
to make sure if rotate function is actually roating the piece, if not checked the column of the piece and than move left,right
accordingly.
"""
from AnimatedTetris import *
from SimpleTetris import *
from kbinput import *
import time, sys

class HumanPlayer:
    def get_moves(self, tetris):
        print "Type a sequence of moves using: \n  b for move left \n  m for move right \n  n for rotation\nThen press enter. E.g.: bbbnn\n"
        moves = raw_input()
        return moves

    def control_game(self, tetris):
        while 1:
            c = get_char_keyboard()
            commands =  { "b": tetris.left, "n": tetris.rotate, "m": tetris.right, " ": tetris.down }
            commands[c]()

#####
# This is the part you'll want to modify!
# Replace our super simple algorithm with something better
#
class ComputerPlayer:
    # This function should generate a series of commands to move the piece into the "optimal"
    # position. The commands are a string of letters, where b and m represent left and right, respectively,
    # and n rotates. tetris is an object that lets you inspect the board, e.g.:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #
    def get_moves(self, tetris):
        # super simple current algorithm: just randomly move left, right, and rotate a few times
        board = tetris.get_board()
        score = tetris.get_score()
        current_piece = tetris.get_piece()
        current_piece_shape = current_piece[0]
        # next_piece = tetris.get_next_piece()
        #column_heights = [min([r for r in range(len(board) - 1, 0, -1) if board[r][c] == "x"] + [20, ]) for c in
        #                  range(0, len(board[0]))]

        rotation_count = self.get_rotation_count(current_piece_shape)

        optimal_heuristic = -2147483648
        optimal_piece = current_piece
        for i in range(0, rotation_count):
            for col in range(0, len(board[0])):
                if tetris.check_collision((board, score), current_piece_shape, 0, col):
                    continue
                for row in range(0, len(board)):
                    if tetris.check_collision((board, score), current_piece_shape, row, col):
                        new_heuristic = self.heuristic(
                            tetris.place_piece((board, score), current_piece_shape, row - 1, col))
                        if new_heuristic > optimal_heuristic:
                            optimal_heuristic = new_heuristic
                            optimal_piece = (current_piece_shape, row, col)
                        break
            current_piece_shape = tetris.rotate_piece(current_piece_shape, 90)
        # tetris.move(optimal_piece[2]-current_piece[2], optimal_piece[0])
        moves = ""
        temp_shape = current_piece[0]
        temp_col = current_piece[2]
        while temp_shape != optimal_piece[0]:
            prev_piece = temp_shape
            temp_shape = tetris.rotate_piece(prev_piece, 90)
            moves += "n"
            while temp_shape == prev_piece:
                if temp_col > 5:
                    moves += "b"
                    temp_col -= 1
                    temp_shape = tetris.rotate_piece(prev_piece, 90)
                    moves += "n"
                else:
                    temp_col += 1
                    moves += "m"
                    temp_shape = tetris.rotate_piece(prev_piece, 90)
                    moves += "n"
        while temp_col != optimal_piece[2]:
            if temp_col > optimal_piece[2]:
                moves += "b"
                temp_col -= 1
            else:
                moves += "m"
                temp_col += 1
        return moves

    # This is the version that's used by the animted version. This is really similar to get_moves,
    # except that it runs as a separate thread and you should access various methods and data in
    # the "tetris" object to control the movement. In particular:
    #   - tetris.col, tetris.row have the current column and row of the upper-left corner of the 
    #     falling piece
    #   - tetris.get_piece() is the current piece, tetris.get_next_piece() is the next piece after that
    #   - tetris.left(), tetris.right(), tetris.down(), and tetris.rotate() can be called to actually
    #     issue game commands
    #   - tetris.get_board() returns the current state of the board, as a list of strings.
    #
    def control_game(self, tetris):
        while 1:
            time.sleep(0.1)
            board = tetris.get_board()
            score = tetris.get_score()
            current_piece = tetris.get_piece()
            current_piece_shape = current_piece[0]
            #next_piece = tetris.get_next_piece()
            #column_heights = [min([r for r in range(len(board) - 1, 0, -1) if board[r][c] == "x"] + [20, ]) for c in
            #                  range(0, len(board[0]))]

            rotation_count = self.get_rotation_count(current_piece_shape)

            optimal_heuristic = -2147483648
            optimal_piece = current_piece
            for i in range(0, rotation_count):
                for col in range(0, len(board[0])):
                    if tetris.check_collision((board, score), current_piece_shape, 0 , col):
                        continue
                    for row in range(0, len(board)):
                        if tetris.check_collision((board, score), current_piece_shape, row , col):
                            new_heuristic = self.heuristic(tetris.place_piece((board,score), current_piece_shape, row - 1, col))
                            if new_heuristic > optimal_heuristic:
                                optimal_heuristic = new_heuristic
                                optimal_piece = (current_piece_shape, row, col)
                            break
                current_piece_shape = tetris.rotate_piece(current_piece_shape, 90)
            # tetris.move(optimal_piece[2]-current_piece[2], optimal_piece[0])
            while tetris.get_piece()[0] != optimal_piece[0]:
                prev_piece = tetris.get_piece()[0]
                tetris.rotate()
                while tetris.get_piece()[0] == prev_piece:
                    if tetris.get_piece()[2] > 5:
                        tetris.left()
                        tetris.rotate()
                    else:
                        tetris.right()
                        tetris.rotate()
            while tetris.get_piece()[2] != optimal_piece[2]:
                if(tetris.get_piece()[2] > optimal_piece[2]):
                    tetris.left()
                else:
                    tetris.right()
            tetris.down()

    def heuristic(self, (board, score)):
        a_ah = -0.510066 #aggregate height multiplier
        b_cl = 0.760666 # clear lines multiplier
        c_h = -0.35663 # Holes multiplier
        d_b = -0.184483 # Bumpiness multiplier

        column_heights = [max([20-r for r in range(len(board) - 1, 0, -1) if board[r][c] == "x"] + [0, ]) for c in
                            range(0, len(board[0]))]
        aggregate_height = sum(column_heights)

        # print "Board:"
        # for row in range(0, len(board)):
        #     print board[row]

        clear_lines = 0
        for row in range(len(board) - 1, 19 - max(column_heights), -1):
            if board[row].count(' ') == 0:
                clear_lines += 1

        holes = 0
        for col in range(0,len(board[0])):
            for row in range(20-column_heights[col], 20):
                if board[row][col] != 'x':
                    holes +=1

        bumpiness = 0
        for col in range(0, len(board[0]) - 1):
            bumpiness = bumpiness + abs(column_heights[col] - column_heights[col+1])
        # print "Height: " + str(aggregate_height)
        # print "clear lines: " + str(clear_lines)
        # print "holes: " + str(holes)
        # print "Bumpiness: " + str(bumpiness)
        #
        # print "h: " +str(a_ah*aggregate_height + b_cl*clear_lines + c_h*holes + d_b*bumpiness)
        return a_ah*aggregate_height + b_cl*clear_lines + c_h*holes + d_b*bumpiness

    def get_rotation_count(self, piece):
        rotation_count_2 = [["xxxx"], ["x","x","x","x"], ["xx ", " xx"], [" x","xx","x "]]
        rotation_count_4 = [["xxx", "  x"],[" x"," x","xx"],["x  ","xxx"], ["xx","x ","x "], ["xxx", " x "],
                            [" x","xx"," x"], [" x ","xxx"], ["x ","xx","x "]]
        if piece in rotation_count_2 :
            return 2
        elif piece in rotation_count_4:
            return 4
        return 1


    # def control_game(self, tetris):
    #     # another super simple algorithm: just move piece to the least-full column
    #     while 1:
    #         time.sleep(0.1)
    #
    #         board = tetris.get_board()
    #         column_heights = [ min([ r for r in range(len(board)-1, 0, -1) if board[r][c] == "x"  ] + [100,] ) for c in range(0, len(board[0]) ) ]
    #         index = column_heights.index(max(column_heights))
    #
    #         if(index < tetris.col):
    #             tetris.left()
    #         elif(index > tetris.col):
    #             tetris.right()
    #         else:
    #             tetris.down()


###################
#### main program

(player_opt, interface_opt) = sys.argv[1:3]

try:
    if player_opt == "human":
        player = HumanPlayer()
    elif player_opt == "computer":
        player = ComputerPlayer()
    else:
        print "unknown player!"

    if interface_opt == "simple":
        tetris = SimpleTetris()
    elif interface_opt == "animated":
        tetris = AnimatedTetris()
    else:
        print "unknown interface!"

    tetris.start_game(player)

except EndOfGame as s:
    print "\n\n\n", s
