import uttt_data

class Board:
    def __init__(self, data):
        self.markers = [ [ data.GetMarker(board, position) for position in range(9) ] for board in range(9) ]
        self.next_player = data.GetNextPlayer()
        self.next_board = data.GetNextBoard()
        self.winner = data.GetWinner()
        self.board_owners = [ data.GetBoardOwner(board) for board in range(9) ]
        self.this_player = data.GetPlayer()
        if self.this_player == uttt_data.PLAYER_X:
            self.other_player = uttt_data.PLAYER_O
        else:
            self.other_player = uttt_data.PLAYER_X
        return

    def CheckBoardWin(self, b):
        for i in range(0, 9, 3):
            if b[i] == b[i+1] and b[i] == b[i+2] and b[i] != uttt_data.PLAYER_N:
                return b[i]
        for i in range(0, 3, 1):
            if b[i] == b[i+3] and b[i] == b[i+6] and b[i] != uttt_data.PLAYER_N:
                return b[i]
        if b[0] == b[4] and b[0] == b[8] and b[0] != uttt_data.PLAYER_N:
            return b[0]
        if b[2] == b[4] and b[0] == b[6] and b[0] != uttt_data.PLAYER_N:
            return b[0]
        return uttt_data.PLAYER_N
        
    def MakeMove(self, move):
        board, position = move
        undo_info = (board, position, self.markers[board][position],
                     self.next_player, self.next_board, self.board_owners[board], self.winner)
        
        self.markers[board][position] = self.next_player
        if self.next_player == uttt_data.PLAYER_X:
            self.next_player = uttt_data.PLAYER_O
        else:
            self.next_player = uttt_data.PLAYER_X
        self.next_board = position
        self.board_owners[board] = self.CheckBoardWin(self.markers[board])
        if self.board_owners[self.next_board] != uttt_data.PLAYER_N:
            self.next_board = uttt_data.BOARD_ANY
        self.winner = self.CheckBoardWin(self.board_owners)

        return undo_info

    def PositionScore(self, position, scores):
        if position in [ 0, 2, 6, 8 ]:
            score = scores[0]
        elif position in [ 1, 3, 5, 7 ]:
            score = scores[2]
        elif position in [ 4 ]:
            score = scores[1]
        else:
            score = 0
        return score
        
        
    def Evaluate(self):
        BOARD_CORNER_SCORE = 60
        BOARD_CENTER_SCORE = 100
        BOARD_EDGE_SCORE = 30
        BOARD_SCORES = [ BOARD_CORNER_SCORE, BOARD_CENTER_SCORE, BOARD_EDGE_SCORE ]
        POSITION_CORNER_SCORE = 6
        POSITION_CENTER_SCORE = 10
        POSITION_EDGE_SCORE = 3
        POSITION_SCORES = [ POSITION_CORNER_SCORE, POSITION_CENTER_SCORE, POSITION_EDGE_SCORE ]
        score = 0
        for board in range(9):
            if self.board_owners[board] == self.this_player:
                score += self.PositionScore(board, BOARD_SCORES)
            elif self.board_owners[board] == self.other_player:
                score -= self.PositionScore(board, BOARD_SCORES)
            else:
                for position in range(9):
                    if self.markers[board][position] == self.this_player:
                        score += self.PositionScore(position, POSITION_SCORES)
                    elif self.markers[board][position] == self.other_player:
                        score -= self.PositionScore(position, POSITION_SCORES)
        return score
                    
                    

    def UndoMove(self, undo_info):
        (b, p, m, np, nb, bo, w) = undo_info
        self.markers[b][p] = m
        self.next_player = np
        self.next_board = nb
        self.board_owners[b] = bo
        self.winner = w
        return

    def LegalMoves(self):
        moves = []
        if self.next_board == uttt_data.BOARD_ANY:
            board_list = range(9)
        else:
            board_list = [ self.next_board ]
        for board in board_list:
            if self.board_owners[board] != uttt_data.PLAYER_N:
                continue
            for position in range(9):
                if self.markers[board][position] != uttt_data.PLAYER_N:
                    continue
                moves.append( (board, position) )
        return moves
                
            

class UTTTAI:

    def __init__(self, data):
        self.data = data
        return

    def ChooseMove(self, depth):
        board = Board(self.data)
        (move, value) = self.Max(board, depth)
        return move

    def Max(self, board, depth):
        if depth <= 0:
            return (None, board.Evaluate())
        max_value = -1000000
        max_move = None
        moves = board.LegalMoves()
        for m in moves:
            undo_info = board.MakeMove(m)
            (junk, value) = self.Min(board, depth-1)
            board.UndoMove(undo_info)
            if value > max_value:
                max_value = value
                max_move = m
        return (max_move, max_value)

    def Min(self, board, depth):
        if depth <= 0:
            return (None, board.Evaluate())
        min_value = 1000000
        min_move = None
        moves = board.LegalMoves()
        for m in moves:
            undo_info = board.MakeMove(m)
            (junk, value) = self.Max(board, depth-1)
            board.UndoMove(undo_info)
            if value < min_value:
                min_value = value
                min_move = m
        return (min_move, min_value)
            
            
