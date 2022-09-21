"""
responsible for storing all the information about the current state of a chess 
also responsible for determining the valid moves at the current state
will also keep a move log
"""

class GameState():
    def __init__(self):
        #board is 8x8, 2d list, each element of the list has 2 char
        #first char represents color, second character represents the type
        #"--" represents empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],]
        self.move_functions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False

    def make_move(self, move): #takes a move as parameter and executes it in the board
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        if move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        
    def undo_move(self):
        if len(self.move_log)!=0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_capt
            self.white_to_move = not self.white_to_move
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            if move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
    
    def get_valid_move(self): #considering checkmate/checks
        #algo
        #1 see if any pieces are in check
        #2 see if any pieces are pinned
        #3 see if there is double check
        moves = []
        self.in_check, self.pins, self.checks = self.check_pin_check()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks)==1:
                moves = self.get_possible_moves()
                #kalo mau ngeblock check harus ada piece yang digerakin supaya ngehalangin checking piece sm king
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                check_piece = self.board[check_row][check_col]
                valid_square = [] #kotak yg bisa ditaro pieces
                #kalo knight, knight harus di capture ato king harus di move
                #else bisa di block
                if check_piece[1] == "N":
                    valid_square = [(check_row, check_col)]
                else:
                    for i in range(1,8):
                        kotak_valid = (king_row + check[2]*i, king_col + check[3]*i)
                        valid_square.append(kotak_valid)
                        if kotak_valid[0] == check_row and kotak_valid[1] == check_col:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] != "K":
                        if (moves[i].end_row, moves[i].end_col) not in valid_square:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)

        else:
            moves = self.get_possible_moves()
        if len(moves)==0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        return moves

    def check_pin_check(self): #ngecek apakah si king (color based on turn) kena check/ada piece kena pin
        pins = [] #lokasi piece yang kena pin (allied) dan arah dari mana pinned nya
        checks = [] #lokasi dari mana king kena check
        in_check = False
        if self.white_to_move:
            ally_color = "w"
            enemy_color = "b"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            ally_color = "b"
            enemy_color = "w"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        #cek dari arah king outwards klo ada pin, log kalo ada
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            dir = directions[i]
            possible_pin = ()
            for j in range(1,8):
                end_row = start_row + dir[0]*j # 0 + -1 = -1
                end_col = start_col + dir[1]*j # 4 + 0 = 4
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == (): #bisa jadi ini piece yang pinned
                            possible_pin = (end_row, end_col, dir[0], dir[1])
                        else: #berarti yang pertama kaga pinned soalnya ada dua piece di satu garis
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        #possibilities:
                        #1 arah horizontal/vertikal, enemy nya rook
                        #2 arah diagonal, enemy nya bishop
                        #3 arah diagonal 1 kotak, enemy nya pawn
                        #4 arah manapun, enemy nya queen
                        #5 arah manapun 1 kotak, enemy nya king
                        if (0 <= i <= 3 and type=="R") or \
                                (4<=i<=7 and type=="B") or \
                                (j==1 and type=="p" and ((enemy_color=="b" and 4<=i<=5) or (enemy_color=="w" and 6<=i<=7))) or \
                                (type=="Q") or (type=="K" and j==1):         
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, dir[0], dir[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
        knight_dir = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        for dir in knight_dir:
            end_row = start_row + dir[0]
            end_col = start_col + dir[1]                        
            if 0<=end_row<=7 and 0<=end_col<=7:
                endPiece = self.board[end_row][end_col]
                if endPiece[1] == "N" and endPiece[0] == enemy_color:
                    in_check = True
                    checks.append((end_row, end_col, dir[0], dir[1]))
        return in_check, pins, checks

    def get_possible_moves(self): #not considering checks
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn=='w' and self.white_to_move) or (turn=='b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves
                    
    #buat dapetin semua moves possible buat tiap piece di row, trus masukin ke list
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move: #focus on the white pawns
            if self.board[r-1][c] == "--": #one square move
                if not piece_pinned or pin_direction == (-1,0):
                    moves.append(Move((r,c), (r-1,c), self.board))
                    if r == 6 and self.board[r-2][c]=="--": #two square move
                        moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b": #jika ada enemy piece to capture
                    if not piece_pinned or pin_direction == (-1,-1):
                        moves.append(Move((r,c), (r-1,c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    if not piece_pinned or pin_direction == (-1,1):
                        moves.append(Move((r,c), (r-1,c+1), self.board))
        else:
            if self.board[r+1][c] == "--":
                if not piece_pinned or pin_direction == (1,0):
                    moves.append(Move((r,c), (r+1,c), self.board))
                    if r == 1 and self.board[r+2][c]=="--":
                        moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    if not piece_pinned or pin_direction == (1,-1):
                        moves.append(Move((r,c), (r+1,c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    if not piece_pinned or pin_direction == (1,1):
                        moves.append(Move((r,c), (r+1,c+1), self.board))

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q": #kalo queen jangan di remove
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1,0), (0,1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if end_row>=0 and end_row<=7 and end_col>=0 and end_col<=7:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        if self.board[end_row][end_col] == "--":
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                        elif self.board[end_row][end_col][0] == enemy_color:
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((1,1), (-1,1), (1,-1), (-1,-1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        if self.board[end_row][end_col] == "--":
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                        elif self.board[end_row][end_col][0] == enemy_color:
                            moves.append(Move((r,c), (end_row,end_col), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0]==r and self.pins[i][1]==c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    if self.board[end_row][end_col] == "--":
                        moves.append(Move((r,c), (end_row,end_col), self.board))
                    elif self.board[end_row][end_col][0] == enemy_color:
                        moves.append(Move((r,c), (end_row,end_col), self.board))
    
    def get_queen_moves(self, r, c, moves):
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        directions = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
        ally_color = "w" if self.white_to_move else "b"
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if self.board[end_row][end_col][0] != ally_color:
                    if ally_color == "w":
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_pin_check()
                    if not in_check:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    if ally_color == "w":
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

class Move():
    rank_to_row = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    row_to_rank = {v:k for k, v in rank_to_row.items()}
    file_to_col = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    col_to_file = {v:k for k, v in file_to_col.items()}

    def __init__(self, start, end, board):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_capt = board[self.end_row][self.end_col]
        self.move_ID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_notation(self, gs):
        checc = ""
        takes = ""
        if self.piece_capt != "--":
            takes = "x"
        if gs.in_check:
            if gs.checkmate:
                checc = "#"
            else:
                checc = "+"
        if self.piece_moved[1] == "p":
            return (takes + self.get_rank_file(self.end_row, self.end_col) + checc)
        else:
            return (self.piece_moved[1] + takes + self.get_rank_file(self.end_row, self.end_col) + checc)

    def get_rank_file(self, r, c):
        return self.col_to_file[c] + self.row_to_rank[r]