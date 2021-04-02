from collections import namedtuple, Counter, defaultdict
import random
import math
import time
infi = math.inf
import json
import requester as req
import ast
# import sys
# sys.setrecursionlimit(5000)
import sys
sys.setrecursionlimit(5000)

class Board(defaultdict):
    not_taken = '-'
   
    def __init__(self, size, to_move=None, **kwds): self.__dict__.update(size=size, to_move=to_move, **kwds)
    # def new(self, changes: dict, **kwds) -> 'Board':
    #     board = self.get_board()
    #     # board.update(self)
    #     # board.update(changes)
    #     return board
    
    # def get_board(self):
    #     board = Board(board_size)
    #     raw = req.get_board_map(gameId = gameId)
    #     if (raw is None):
    #         pass
    #     else:
    #         raw_board = ast.literal_eval(raw["output"])
    #         print(type(raw_board))
    #         board_d = {tuple(map(int,k.split(','))):str(v)
    #                     for k,v in raw_board.items()}
    #         board.update(board_d)
    #     return board


    # def __missing__(self, loc):
    #     x, y = loc
    #     if 0 <= x < self.size and 0 <= y < self.size: return self.not_taken
            
    # def __hash__(self): return hash(tuple(sorted(self.items()))) + hash(self.to_move)
    
    # def __repr__(self):
    #     def row(y): return ' '.join(self[x, y] for x in range(self.size))
    #     return '\n'.join(map(row, range(self.size))) +  '\n'
    def new(self, changes: dict, **kwds) -> 'Board':
        board = Board(self.size, **kwds)
        board.update(self)
        board.update(changes)
        return board

    def __missing__(self, loc):
        x, y = loc
        # print(loc)
        if 0 <= x < self.size and 0 <= y < self.size: return self.not_taken
            
    def __hash__(self): return hash(tuple(sorted(self.items()))) + hash(self.to_move)
    
    def __repr__(self):
        def row(y): return ' '.join(self[x, y] for x in range(self.size))
        return '\n'.join(map(row, range(self.size))) +  '\n'


class TTT():
    def __init__(self, size, k):
        self.k = k # k in a row
        self.squares = {(x, y) for x in range(size) for y in range(size)}
        self.initial = Board(size=size, to_move=p1, utility=0)

    def slots_left(self, board): return self.squares - set(board) #checks how many moves are allowed to make yet

    def marker(self, board, square): #putting the X or O mark 
        player = board.to_move
        board = board.new({square: player}, to_move=(p2 if player == p1 else p1))
        win = TTT.k_in_row(board, player, square, self.k)
        board.utility = (0 if not win else +1 if player == p1 else -1)
        return board

    def utility(self, board, player): return board.utility if player == p1 else -board.utility #1 for win, -1 for loss, 0 for else

    def is_terminal(self, board): return board.utility != 0 or len(self.squares) == len(board) #checks if game is finished or no empty squares left

    def display(self, board): print(board)     

    def play(game, strategies: dict, verbose=False):
        #strategies is a {player_name: function} dict
        #function(state, game) is used to get the player's move
        #keep verbose false if you don't want to see the board outputs
        state = game.initial
        while not game.is_terminal(state):
            player = state.to_move
            move = strategies[player](game, state)
            state = game.marker(state, move)
            if verbose: 
                print('Player', player, 'move:', move)
                print(state)
        if (game.is_terminal(state) and state.utility == 0):
        # if (len(game.squares) == len(state) and state.utility == 0):
          print("It's DRAW")
        else: print("Player", player, "WON")
        #draw is not detectable
        return state

    def k_in_row(board, player, square, k): #checks if player has k pieces in a line through k x k square
      def in_row(x, y, dx=0, dy=0): return 0 if board[x, y] != player else 1 + in_row(x + dx, y + dy, dx, dy)
      return any(in_row(*square, dx, dy) + in_row(*square, -dx, -dy) - 1 >= k for (dx, dy) in ((0, 1), (1, 0), (1, 1), (1, -1)))
  
class Player():
    def AI(depth): return lambda game, state: Player.a_b_minimax(game, state, depth)[1] #player with algorithm
    def player(): return lambda game, state: Player.opponent(game, state)

    def opponent(game, state):
        player = state.to_move
        inpt = req.get_moves(gameId)
        try:
            p = inpt["moves"][-1]['symbol']
        except Exception as e:
            Player.opponent(game, state)
        else:
            p = inpt["moves"][-1]['symbol']
            if player == p:
                m = inpt["moves"][-1]['move']
                m = tuple(map(int,m.split(',')))
                if game.is_terminal(state):
                  return game.utility(state, player), None
                *_, move = game.marker(state, m)
                return move
            else: 
                # time.sleep(2)
                return Player.opponent(game, state)

    def a_b_minimax(game, state, d, h=lambda s, p: 0):
        player = state.to_move
        def max_value(state, alpha, beta, depth):
            if game.is_terminal(state):
                return game.utility(state, player), None
            if depth>d:
                return h(state, player), None
            v, move = -infi, None
            for a in game.slots_left(state):
                v2, _ = min_value(game.marker(state, a), alpha, beta, depth+1)
                if v2 > v:
                    v, move = v2, a
                    alpha = max(alpha, v)
                if v >= beta:
                    return v, move
            return v, move

        def min_value(state, alpha, beta, depth):
            if game.is_terminal(state):
                return game.utility(state, player), None
            if depth>d:
                return h(state, player), None
            v, move = +infi, None
            for a in game.slots_left(state):
                v2, _ = max_value(game.marker(state, a), alpha, beta, depth + 1)
                if v2 < v:
                    v, move = v2, a
                    beta = min(beta, v)
                if v <= alpha:
                    return v, move
            return v, move
        _, mxmn =  max_value(state, -infi, +infi, 0)
        req.make_a_move(gameId, mxmn)
        # time.sleep(10)
        return max_value(state, -infi, +infi, 0)

def first(): #if we are the ones creating the game, this will be run
    global p1,p2
    p1,p2 = 'O','X'
    TTT.play(TTT(size=board_size, k=target), {'O':Player.AI(3), 'X':Player.player()}, verbose=True).utility
    

def second(): #if we are the ones playing against someone who created the game, this will be run
    global p1,p2
    p1,p2 = 'X', 'O'
    TTT.play(TTT(size=board_size, k=target), {'O':Player.player(),'X':Player.AI(3)}, verbose=True).utility


if __name__ == '__main__':
    strt = time.time()
    global board_size, target 
    board_size, target = int(req.board_size), int(req.target)
    # gameId = req.create_game(1284)
    # print(gameId)
    # gameId = 3053
    # first()
#________________________________#
    gameId = 3063
    second()

    endd = time.time()
    print(endd - strt)
