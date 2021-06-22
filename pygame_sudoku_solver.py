import time, sys, pygame
import numpy as np
import numba as nb

BLACK = (0,0,0)
WHITE = (255,255,255)
WIDTH, HEIGHT = 800, 800

sudoku_board = np.array([
    [8,0,0,0,0,0,0,0,0],
    [0,0,3,6,0,0,0,0,0],
    [0,7,0,0,9,0,2,0,0],
    [0,5,0,0,0,7,0,0,0],
    [0,0,0,0,4,5,7,0,0],
    [0,0,0,1,0,0,0,3,0],
    [0,0,1,0,0,0,0,6,8],
    [0,0,8,5,0,0,0,1,0],
    [0,9,0,0,0,0,4,0,0]
])

"""
Alternative input format:
sudoku_board = '010500300002800000003000190020009010640000050500001020000070006000062007090000000'
"""

def backtracking(board):
    
    def draw_board(display, font, board):
        display.fill(WHITE)
        gap_x = WIDTH/9
        gap_y = HEIGHT/9

        for i in range(10):
            pygame.draw.line(display, BLACK, (gap_x*i, 0), (gap_x*i, HEIGHT), width = 5 if (i % 3 == 0) else 1)
            pygame.draw.line(display, BLACK, (0,gap_y*i), (WIDTH, gap_y*i), width = 5 if (i % 3 == 0) else 1)
            

        for row in range(len(board)):
            for col in range(len(board[0])):
                val = str(board[row,col]) if board[row,col] != 0 else ''
                text = font.render(val, True, BLACK)
                textRect = text.get_rect()
                textRect.center = (col*gap_x + gap_x/2, row*gap_y + gap_y/2)
                display.blit(text, textRect)
        pygame.display.update()

    def is_solved(board):
        len_b = 9
        solved_line = {1,2,3,4,5,6,7,8,9}
        if any([set(board[i,:]) != solved_line for i in range(len_b)]):
            return False
        elif any([set(board[:,i]) != solved_line for i in range(len_b)]):
            return False
        elif any(set([board[3*(i//3) + j//3, 3*(i%3) + j%3] for j in range(len_b)]) != solved_line for i in range(len_b)):
            return False
        return True
    
    @nb.njit()
    def is_valid(num, i, j, board):
        if num in board[i,:] or num in board[:, j]:
            return False
        square_num = 3*(i//3) + (j//3)
        for index in range(9):
            if (board[3*(square_num//3) + index//3, 3*(square_num%3) + index%3] == num):
                return False
        return True

    def transform_into_array(board):
        """
        Runs if the sudoku board is given in string notation.
        Example : '010500300002800000003000190020009010640000050500001020000070006000062007090000000'
        """
        new_board = [[0 for j in range(9)] for i in range(9)]
        for index in range(81):
            new_board[index//9][index%9] = int(board[index])
        return np.array(new_board)
    
    def increment_pos(i,j, by_amount = 1):
        index = i*9 + j
        index += by_amount
        i,j = index//9, index%9
        return i,j
    
    if type(board) == str:
        board = transform_into_array(board)

    pygame.init()
    display = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku solver")
    font = pygame.font.Font('freesansbold.ttf', 32)
    draw_board(display, font, board)


    reference_board = board.copy()
    i = 0
    j = 0
    solved = False
    step = 0
    quit = False
    
    while not quit:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                t0 = time.time()
                while not solved:
                    
                    if reference_board[i,j] == 0:
                        
                        while not board[i,j] == 9 and not is_valid(board[i,j]+1, i, j, board):
                            board[i,j] += 1

                        board[i,j] += 1

                        if board[i,j] == 10: #Backtracks!
                            board[i,j] = 0
                            i,j = increment_pos(i, j, -1)
                            while not reference_board[i,j] == 0: #Backtracks until it finds the next value to modify
                                i,j = increment_pos(i,j,-1)
                        else:
                            # It found a possible value for the point i,j. 
                            # It goes to the next point to begin incrementing 
                            # that one.
                            i,j = increment_pos(i,j)
                    
                    else:
                        i,j = increment_pos(i,j)
                    

                    if (i > 8):
                        draw_board(display, font, board)
                        print(f'It took {time.time() - t0}s to solve this sudoku! The result is\n{board}')
                        solved = True

                    elif (i < 0):
                        """
                        We've gone off the board. The sudoku is impossible
                        to solve. This happens if, for example, the input 
                        board contains two "4"s on the same line.
                        """
                        print("IMPOSSIBLE SUDOKU!")
                        solved = True

                    step += 1
                    if step%1000 == 0:
                        draw_board(display, font, board)

if __name__ == "__main__":
    backtracking(sudoku_board)
