import random
import time
import tkinter as tk
from tkinter import messagebox

try:
    import winsound
    USE_WIN = True
except:
    USE_WIN = False


def s_move():
    if USE_WIN: winsound.Beep(500, 40)
    else: root.bell()

def s_merge():
    if USE_WIN:
        winsound.Beep(650, 70)
        winsound.Beep(800, 60)
    else:
        root.bell()

def s_lose():
    if USE_WIN:
        winsound.Beep(300, 180)
        winsound.Beep(220, 230)
    else:
        root.bell()


SIZE = 4

def new_board():
    b = [[0]*SIZE for _ in range(SIZE)]
    add(b); add(b)
    return b

def add(b):
    kosong = [(r,c) for r in range(SIZE) for c in range(SIZE) if b[r][c] == 0]
    if not kosong: return
    r,c = random.choice(kosong)
    b[r][c] = 4 if random.random() < 0.1 else 2

def compress(row):
    v = [x for x in row if x != 0]
    v += [0]*(SIZE-len(v))
    return v

def merge(row):
    score = 0
    for i in range(SIZE-1):
        if row[i] != 0 and row[i] == row[i+1]:
            row[i] *= 2
            score += row[i]
            row[i+1] = 0
    return row, score

def move_left(b):
    moved = False
    gain = 0
    for i in range(SIZE):
        r = compress(b[i])
        r, s = merge(r)
        r = compress(r)
        if r != b[i]:
            moved = True
        b[i] = r
        gain += s
    return moved, gain

def move_right(b):
    for i in range(SIZE):
        b[i].reverse()
    m, s = move_left(b)
    for i in range(SIZE):
        b[i].reverse()
    return m, s

def move_up(b):
    t = list(zip(*b))
    t = [list(row) for row in t]
    m, s = move_left(t)
    nb = list(zip(*t))
    for i in range(SIZE):
        b[i] = list(nb[i])
    return m, s

def move_down(b):
    t = list(zip(*b))
    t = [list(row) for row in t]
    m, s = move_right(t)
    nb = list(zip(*t))
    for i in range(SIZE):
        b[i] = list(nb[i])
    return m, s

def can_play(b):
    for r in range(SIZE):
        for c in range(SIZE):
            if b[r][c] == 0:
                return True
    for r in range(SIZE):
        for c in range(SIZE-1):
            if b[r][c] == b[r][c+1]:
                return True
    for c in range(SIZE):
        for r in range(SIZE-1):
            if b[r][c] == b[r+1][c]:
                return True
    return False


TILE = {
    0: ("#cdc1b4","#776e65"),
    2: ("#eee4da","#776e65"),
    4: ("#ede0c8","#776e65"),
    8: ("#f2b179","#f9f6f2"),
    16: ("#f59563","#f9f6f2"),
    32: ("#f67c5f","#f9f6f2"),
    64: ("#f65e3b","#f9f6f2"),
    128: ("#edcf72","#f9f6f2"),
    256: ("#edcc61","#f9f6f2"),
    512: ("#edc850","#f9f6f2"),
    1024: ("#edc53f","#f9f6f2"),
    2048: ("#edc22e","#f9f6f2"),
}


class Game:
    def __init__(self, win):
        self.win = win
        win.title("2048 Game")
        self.frame = tk.Frame(win, bg="#faf8ef")
        self.frame.pack(padx=10, pady=10)

        top = tk.Frame(self.frame, bg="#faf8ef")
        top.grid(row=0, column=0, pady=(0,10))

        self.score = tk.IntVar(value=0)
        tk.Label(top, text="Score:", bg="#faf8ef").pack(side="left")
        tk.Label(top, textvariable=self.score, bg="#faf8ef", font=("Arial",12,"bold")).pack(side="left", padx=4)
        tk.Button(top, text="Restart", command=self.reset).pack(side="right")

        size = 110*SIZE + 10*(SIZE+1)
        self.canvas = tk.Canvas(self.frame, width=size, height=size, bg="#faf8ef", highlightthickness=0)
        self.canvas.grid(row=1, column=0)

        self.tiles = []
        for r in range(SIZE):
            row = []
            for c in range(SIZE):
                x = 10 + c*(110+10)
                y = 10 + r*(110+10)
                rect = self.canvas.create_rectangle(x,y,x+110,y+110, fill="#cdc1b4", width=0)
                txt = self.canvas.create_text(x+55, y+55, text="", font=("Verdana",24,"bold"))
                row.append((rect,txt))
            self.tiles.append(row)

        win.bind("<Key>", self.key)

        self.board = new_board()
        self.total = 0
        self.over = False
        self.draw()

    def draw(self):
        for r in range(SIZE):
            for c in range(SIZE):
                v = self.board[r][c]
                rect, txt = self.tiles[r][c]
                bg, fg = TILE.get(v, ("#3c3a32","#f9f6f2"))
                self.canvas.itemconfig(rect, fill=bg)
                self.canvas.itemconfig(txt, text=str(v) if v else "", fill=fg)
        self.score.set(self.total)
        self.win.update_idletasks()

    def lose_anim(self):
        for a in range(255, 120, -15):
            col = f"#{a:02x}{a:02x}{a:02x}"
            for r in range(SIZE):
                for c in range(SIZE):
                    self.canvas.itemconfig(self.tiles[r][c][0], fill=col)
            self.win.update()
            time.sleep(0.03)

        ox = self.win.winfo_x()
        oy = self.win.winfo_y()
        for _ in range(8):
            self.win.geometry(f"+{ox+8}+{oy}")
            self.win.update()
            time.sleep(0.02)
            self.win.geometry(f"+{ox-8}+{oy}")
            self.win.update()
            time.sleep(0.02)

        self.win.geometry(f"+{ox}+{oy}")

    def finish(self):
        self.over = True
        s_lose()
        self.lose_anim()
        messagebox.showinfo("Game Over", f"Skor kamu: {self.total}")
        self.reset()

    def key(self, e):
        if self.over: return
        k = e.keysym
        moved = False
        gain = 0

        if k in ("Left","a","A"): moved, gain = move_left(self.board)
        elif k in ("Right","d","D"): moved, gain = move_right(self.board)
        elif k in ("Up","w","W"): moved, gain = move_up(self.board)
        elif k in ("Down","s","S"): moved, gain = move_down(self.board)
        else:
            return

        if moved:
            if gain > 0: s_merge()
            else: s_move()
            self.total += gain
            add(self.board)
            self.draw()

            if not can_play(self.board):
                self.finish()

    def reset(self):
        self.board = new_board()
        self.total = 0
        self.over = False
        self.draw()


if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
