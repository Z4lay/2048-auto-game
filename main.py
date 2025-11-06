# main.py
import tkinter as tk
from puzzle import GameGrid
from auto import Auto2048

root = tk.Tk()
game = GameGrid()
game.pack()

auto = Auto2048(game)  # 将自动操作绑定到游戏

root.mainloop()
