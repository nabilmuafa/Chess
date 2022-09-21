"""
driver file, responsible for handling user input and displaying GameState object
"""

import pygame as pp
import ChessEngine

width = height = 512
dimension = 8
square_size = height // dimension
max_fps = 15 #buat animasi
images = {}

"""
Initialize a global dict of images, called exactly once in the main
"""
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wp", "wQ", "wK", "wB", "wN", "wR"]
    for piece in pieces:
        images[piece] = pp.transform.scale(pp.image.load("images/" + piece + ".png"), (square_size, square_size))
    #we can access an image by calling the image dict

"""
code main driver, handles the user input
"""
def main():
    pp.init()
    screen = pp.display.set_mode((width, height))
    clock = pp.time.Clock()
    screen.fill(pp.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_move()
    move_made = False #flag variable for when a valid move is made, supaya ga regenerate vmoves b4 player makes move
    load_images() #sekali aja sblm while loop
    running = True #nandain kalo game udah jalan(??)
    selected_sq = () #keeping track of last click of user (row,col)
    player_click = [] #keep track of the player clicks, list of two tuples
    while(running):
        for e in pp.event.get():
            if e.type == pp.QUIT:
                running = False
            #mouse handler
            elif e.type == pp.MOUSEBUTTONDOWN:
                location = pp.mouse.get_pos() #lokasi mouse (x,y)
                col = location[0]//square_size
                row = location[1]//square_size
                if selected_sq == (row, col):
                    selected_sq = () #deselect kalo misal yg dipilih itu kotak yg sama
                    player_click = []
                else:
                    selected_sq = (row, col)
                    player_click.append(selected_sq)
                if len(player_click) == 2: #kalo ini klik kedua, buat gerakin piece
                    move = ChessEngine.Move(player_click[0], player_click[1], gs.board)
                    if move in valid_moves:
                        gs.make_move(move)
                        move_made = True
                        selected_sq = () #reset user clicks
                        player_click = []
                    else:
                        player_click = [selected_sq]
            #key handler
            elif e.type == pp.KEYDOWN:
                if e.key == pp.K_z:
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_move()
            print(move.get_notation(gs))
            if gs.checkmate:
                winner = "White" if not gs.whiteToMove else "Black"
                print ("The game is finished. The winner is " + winner + ". The game takes " + \
                        str(len(gs.moveLog)) + " moves. Thanks for playing!")
                running = False
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(max_fps)
        pp.display.flip()

#draws the square and board (graphics)
def draw_game_state(screen, gs):
    draw_board(screen) #gambar kotak
    draw_pieces(screen, gs.board) #gambar pieces

#gambar papan
def draw_board(screen):
    colors = [pp.Color("white"), pp.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[(r+c)%2]
            pp.draw.rect(screen, color, pp.Rect(c*square_size, r*square_size, square_size, square_size))

#gambar pieces pake GameState.board
def draw_pieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], pp.Rect(c*square_size, r*square_size, square_size, square_size))

if __name__ == "__main__":
    main()