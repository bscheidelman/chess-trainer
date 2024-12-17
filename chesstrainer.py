import chess
import chess.engine
from chess.engine import Cp, Mate, MateGiven
import tkinter as tk
from tkinter import messagebox, PhotoImage, Label, Button, Frame
import requests
import json
import random

LICHESS_API_URL = "https://explorer.lichess.ovh/lichess"

ENGINE_PATH = r"C:\Users\bsche\source\repos\chess trainer\stockfish\stockfish-windows-x86-64-sse41-popcnt.exe" #CHANGE TO YOUR ENGINE PATH




class ChessTrainer:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Trainer")
        self.master.configure(bg="#2c2c2c")  

        self.left_frame = Frame(master, bg="#2c2c2c")
        self.left_frame.grid(row=0, column=0, padx=10, pady=10)

        self.right_frame = Frame(master, bg="#3b3b3b")
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.board = chess.Board()
        self.canvas_size = 400
        self.square_size = self.canvas_size // 8
        self.canvas = tk.Canvas(self.left_frame, width=self.canvas_size, height=self.canvas_size, bg="white")
        self.canvas.pack()

        self.piece_images = self.load_piece_images()
        self.eval_images = self.load_eval_images()

        self.info_label = Label(self.right_frame, text="Set up the board and press 'Start Training'",
                                bg="#3b3b3b", fg="white", font=("Helvetica", 12))
        self.info_label.pack(pady=10)

        self.eval_label = Label(self.right_frame, text="Current Evaluation: N/A",
                                bg="#3b3b3b", fg="white", font=("Helvetica", 12))
        self.eval_label.pack(pady=10)

        self.best_move_label = Label(self.right_frame, text="Previous best move: N/A",
                                bg="#3b3b3b", fg="white", font=("Helvetica", 12))
        self.best_move_label.pack(pady=10)

        self.eval_image_size = self.canvas_size // 3
        self.eval_image_label = Label(self.right_frame, bg="#3b3b3b")
        self.eval_image_label.pack(pady=10)
        self.eval_image_label.image = self.resize_image(self.eval_images.get("Good move."), self.eval_image_size)
        self.eval_image_label.config(image=self.eval_image_label.image)

        self.start_button = Button(self.right_frame, text="Start Training", command=self.start_training, bg="#6dabe4",
                                   fg="white", font=("Helvetica", 10), relief="flat")
        self.start_button.pack(pady=10)

        self.try_again_button = Button(self.right_frame, text="Try Again", command=self.undo_move, bg="#e46666",
                                       fg="white", font=("Helvetica", 10), relief="flat")
        self.try_again_button.pack(pady=10)

        self.training = False
        self.previous_eval = 0
        self.selected_piece = None
        self.user_color = chess.WHITE
        self.draw_board()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def load_piece_images(self):
        pieces = {}
        names = ["p", "r", "n", "b", "q", "k"]
        for color, prefix in [(chess.WHITE, "l"), (chess.BLACK, "d")]:
            for piece in names:
                filename = f"images/Chess_{piece}{prefix}t60.png"
                pieces[piece + ("w" if color else "b")] = PhotoImage(file=filename)
        return pieces

    def load_eval_images(self):
        evals = {
            "Best move!": PhotoImage(file="images/great_move.png"),
            "Good move.": PhotoImage(file="images/good_move.png"),
            "Okay": PhotoImage(file="images/fine_move.png"),
            "Inaccurate move.": PhotoImage(file="images/innacurate_move.png"),
            "Mistake.": PhotoImage(file="images/mistake_move.png"),
            "Blunder!": PhotoImage(file="images/blunder_move.png")
        }
        return evals

    def resize_image(self, image, size):
        return image.subsample(image.width() // size, image.height() // size)

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"]
        for i in range(8):
            for j in range(8):
                color = colors[(i + j) % 2]
                self.canvas.create_rectangle(
                    j * self.square_size, i * self.square_size,
                    (j + 1) * self.square_size, (i + 1) * self.square_size, fill=color
                )
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                x, y = chess.square_file(square), chess.square_rank(square)
                piece_image = self.piece_images[piece.symbol().lower() + ("w" if piece.color == chess.WHITE else "b")]
                self.canvas.create_image(
                    x * self.square_size + self.square_size // 2,
                    (7 - y) * self.square_size + self.square_size // 2, image=piece_image, tags=("piece", square)
                )

    def fetch_stockfish_eval(self, fen, depth=20):
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
            board = chess.Board(fen)
            info = engine.analyse(board, chess.engine.Limit(depth=depth))
            score = info["score"].relative
            
            if score.is_mate(): 
                return 999
            if self.board.turn == chess.BLACK:
                return -score.score() / 100
            else:
                return score.score() / 100
            
    def get_best_move(self, fen, depth=20, move_format="text"):
        with chess.engine.SimpleEngine.popen_uci(ENGINE_PATH) as engine:
            board = chess.Board(fen)
            
            result = engine.play(board, chess.engine.Limit(depth=depth))
            
            move = result.move
            
            if move_format == "uci":
                return move.uci()  
            elif move_format == "text":
                return board.san(move)  
            else:
                raise ValueError("Invalid move_format. Use 'uci' or 'text'.")
            
    def fetch_lichess_move(self, fen):
        params = {"fen": fen}
        response = requests.get(LICHESS_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            moves = data.get("moves", [])
            if moves:
                choice = random.choices(moves, weights=[move["white"] + move["black"] for move in moves], k=1)[0]
                return choice["uci"]
        return None

    def evaluate_move_quality(self, current_eval):
        if current_eval is None or self.previous_eval is None:
            return "Evaluation unavailable"
        centipawn_loss = abs(self.previous_eval - current_eval) * 100
        if self.is_best:
            return "Best move!"
        elif centipawn_loss < 50:
            return "Good move."
        elif centipawn_loss < 100:
            return "Okay"
        elif centipawn_loss < 200:
            return "Inaccurate move."
        elif centipawn_loss < 300:
            return "Mistake."
        else:
            return "Blunder!"

    def undo_move(self):
        if self.board.move_stack:
            self.board.pop()
            self.board.pop()
            self.previous_eval = 0
            self.info_label.config(text="Move undone. Make your next move.")
            self.eval_label.config(text="Current Evaluation: N/A")
            self.draw_board()

    def on_click(self, event):
        row, col = event.y // self.square_size, event.x // self.square_size
        square = chess.square(col, 7 - row)
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.selected_piece = square

    def on_drag(self, event):
        if self.selected_piece is not None:
            self.draw_board()
            piece = self.board.piece_at(self.selected_piece)
            image = self.piece_images[piece.symbol().lower() + ("w" if piece.color == chess.WHITE else "b")]
            self.canvas.create_image(event.x, event.y, image=image)

    def on_release(self, event):
        if self.selected_piece is not None:
            start_square = self.selected_piece
            end_row, end_col = event.y // self.square_size, event.x // self.square_size
            end_square = chess.square(end_col, 7 - end_row)
            move = chess.Move(start_square, end_square)

            self.is_best = False
            if (move.uci() == self.get_best_move(self.board.fen(), move_format="uci")):
                self.is_best = True

            if move in self.board.legal_moves:
                previous_best = self.get_best_move(self.board.fen(), move_format="text")
                self.best_move_label.config(text=f"Previous Best: {previous_best}")
                
                self.board.push(move)
                self.draw_board()

                current_eval = self.fetch_stockfish_eval(self.board.fen())
                move_quality = self.evaluate_move_quality(current_eval)

                if self.training: 
                    self.info_label.config(text=move_quality)
                    self.eval_label.config(text=f"Current Evaluation: {current_eval:.2f}")
                    self.eval_image_label.config(image=self.eval_images.get(move_quality, ""))
                    resized_image = self.resize_image(self.eval_images.get(move_quality), self.eval_image_size)
                    self.eval_image_label.config(image=resized_image)
                    self.eval_image_label.image = resized_image

                    

                if self.training:
                    lichess_move = self.fetch_lichess_move(self.board.fen())
                    if lichess_move:
                        self.board.push_uci(lichess_move)
                        self.info_label.config(text=f"Computer played: {lichess_move}")
                        self.previous_eval = self.fetch_stockfish_eval(self.board.fen())
                        self.eval_label.config(text=f"Current Evaluation: {self.previous_eval:.2f}")
                    else:
                        self.info_label.config(text="No move data available from Lichess.")
            else:
                self.info_label.config(text="Illegal move. Try again.")
            self.selected_piece = None
            self.draw_board()

    def start_training(self):
        if not self.board.is_valid():
            messagebox.showerror("Invalid Position", "The board position is invalid.")
            return
        self.training = True
        self.previous_eval = self.fetch_stockfish_eval(self.board.fen())
        self.info_label.config(text="Training started! Make your move.")
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessTrainer(root)
    root.mainloop()
