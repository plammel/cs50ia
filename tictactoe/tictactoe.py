"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    nX = 0
    nO = 0

    i = 0
    while i < 3:
        j = 0
        while j < 3:
            if board[i][j] is X:
                nX += 1
            elif board[i][j] is O:
                nO += 1
            j += 1
        i += 1

    if nX == nO:
        return X
    return O
    


def actions(board):
    empties = []
    i = 0
    while i < 3:
        j = 0
        while j < 3:
            if board[i][j] is EMPTY:
                empties.append((i, j))
            j += 1
        i += 1
    return empties


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    newBoard = copy.deepcopy(board)
    if action is not None:
        value = player(newBoard)
        newBoard[action[0]][action[1]] = value

    return newBoard

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    if equals(board[0][0], board[1][1], board[2][2]) is True:
        return board[0][0]
    
    elif equals(board[0][2], board[1][1], board[2][0]):
        return board[0][2]
    
    i = 0
    while i < 3:
        j = 0
        while j < 3:
        # horizontal
            if equals(board[i][0], board[i][1], board[i][2]):
                return board[i][0]
            # vertical
            
            elif equals(board[0][j], board[1][j], board[2][j]):
                return board[0][j]
            j += 1
        i += 1

    return None

def equals(a, b, c):
    return a is not EMPTY and a == b and b == c

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    return len(actions(board)) == 0

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    result = winner(board)
    if result is X:
        return 1
    elif result is O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    current_player = player(board)
    best_action = None

    if current_player is X:
        best_score = -math.inf
        for action in actions(board):
            score = min_score(result(board, action))
            if score > best_score:
                best_score = score
                best_action = action

    elif current_player is O:
        best_score = math.inf
        for action in actions(board):
            score = max_score(result(board, action))
            if score < best_score:
                best_score = score
                best_action = action

    return best_action

def max_score(board):
    if terminal(board):
        return utility(board)

    best_score = -math.inf
    for action in actions(board):
        best_score = max(best_score, min_score(result(board, action)))
    return best_score

def min_score(board):
    if terminal(board):
        return utility(board)

    best_score = math.inf
    for action in actions(board):
        best_score = min(best_score, max_score(result(board, action)))
    return best_score