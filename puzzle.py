# puzzle.py
from tkinter import Frame, Label, Button, CENTER
import logic   # 你的2048逻辑文件
import constants as c

class GameGrid(Frame):
    def __init__(self, auto=None):
        Frame.__init__(self)
        self.grid()
        self.master.title("2048 - Enhanced Version")
        self.master.bind("<Key>", self.key_down)
        self.master.focus_set()

        # 自动操作
        self.auto = auto

        # 分数初始化
        self.score = 0
        self.best_score = logic.load_best_score()

        # 历史记录
        self.history_matrixs = []
        self.history_scores = []

        # 界面初始化
        self.grid_cells = []
        self.init_grid()
        self.init_matrix()

    def init_matrix(self):
        self.matrix = logic.new_game(c.GRID_LEN)
        self.update_grid_cells()

    def get_board(self):
        return [row[:] for row in self.matrix]

    def move(self, direction):
        """执行移动并更新分数"""
        func = getattr(logic, direction)
        self.history_matrixs.append([row[:] for row in self.matrix])
        self.history_scores.append(self.score)

        self.matrix, done, move_score = func(self.matrix)
        if done:
            self.score += move_score
            if self.score > self.best_score:
                self.best_score = self.score
                logic.save_best_score(self.best_score)
            self.matrix = logic.add_two(self.matrix)
            self.update_grid_cells()
        else:
            self.history_matrixs.pop()
            self.history_scores.pop()

    def init_grid(self):
        # 标题和分数
        title_frame = Frame(self, bg=c.BACKGROUND_COLOR_GAME)
        title_frame.grid(row=0, column=0, pady=(10,0))

        Label(title_frame, text="2048", font=c.FONT_TITLE,
              fg="#776e65", bg=c.BACKGROUND_COLOR_GAME).grid(row=0,column=0,padx=(0,20))

        score_frame = Frame(title_frame, bg=c.BACKGROUND_COLOR_GAME)
        score_frame.grid(row=0, column=1)

        # 当前分数
        current_score_frame = Frame(score_frame, bg=c.BACKGROUND_COLOR_SCORE, width=100, height=50)
        current_score_frame.grid(row=0,column=0,padx=(0,10))
        current_score_frame.grid_propagate(False)
        Label(current_score_frame,text="SCORE", font=("Verdana",10,"bold"),
              fg="#eee4da", bg=c.BACKGROUND_COLOR_SCORE).grid(row=0)
        self.score_label = Label(current_score_frame, text=str(self.score),
                                 font=("Verdana",14,"bold"), fg="white", bg=c.BACKGROUND_COLOR_SCORE)
        self.score_label.grid(row=1)

        # 最佳分数
        best_score_frame = Frame(score_frame, bg=c.BACKGROUND_COLOR_SCORE, width=100, height=50)
        best_score_frame.grid(row=0,column=1)
        best_score_frame.grid_propagate(False)
        Label(best_score_frame,text="BEST", font=("Verdana",10,"bold"),
              fg="#eee4da", bg=c.BACKGROUND_COLOR_SCORE).grid(row=0)
        self.best_score_label = Label(best_score_frame, text=str(self.best_score),
                                      font=("Verdana",14,"bold"), fg="white", bg=c.BACKGROUND_COLOR_SCORE)
        self.best_score_label.grid(row=1)

        # 按钮
        button_frame = Frame(self, bg=c.BACKGROUND_COLOR_GAME)
        button_frame.grid(row=1, column=0, pady=10)
        Button(button_frame,text="New Game (N)", font=("Verdana",12,"bold"),
               bg="#8f7a66", fg="white", command=self.new_game).grid(row=0,column=0,padx=(0,10))
        Button(button_frame,text="Undo (B)", font=("Verdana",12,"bold"),
               bg="#8f7a66", fg="white", command=self.undo_move).grid(row=0,column=1)

        # 游戏网格
        background = Frame(self, bg=c.BACKGROUND_COLOR_GAME, width=c.SIZE, height=c.SIZE)
        background.grid(row=2,column=0,pady=10)
        for i in range(c.GRID_LEN):
            grid_row = []
            for j in range(c.GRID_LEN):
                cell = Frame(background, bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                             width=c.SIZE/c.GRID_LEN, height=c.SIZE/c.GRID_LEN)
                cell.grid(row=i,column=j,padx=c.GRID_PADDING,pady=c.GRID_PADDING)
                t = Label(cell, text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY,
                          justify=CENTER, font=c.FONT, width=5, height=2)
                t.grid()
                grid_row.append(t)
            self.grid_cells.append(grid_row)

    def update_grid_cells(self):
        for i in range(c.GRID_LEN):
            for j in range(c.GRID_LEN):
                num = self.matrix[i][j]
                if num == 0:
                    self.grid_cells[i][j].configure(text="", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
                else:
                    self.grid_cells[i][j].configure(text=str(num),
                        bg=c.BACKGROUND_COLOR_DICT[num],
                        fg=c.CELL_COLOR_DICT[num])
        self.score_label.configure(text=str(self.score))
        self.best_score_label.configure(text=str(self.best_score))
        self.update_idletasks()

            # 检查游戏是否失败
        if logic.game_state(self.matrix) == 'lose':
            for i in range(c.GRID_LEN):
                for j in range(c.GRID_LEN):
                    self.grid_cells[i][j].configure(bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][1].configure(text="You", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            self.grid_cells[1][2].configure(text="Lose!", bg=c.BACKGROUND_COLOR_CELL_EMPTY)
            # 停止自动模式
            if self.auto:
                self.auto.stop()

    def new_game(self):
        self.score = 0
        self.init_matrix()

    def undo_move(self):
        if self.history_matrixs:
            self.matrix = self.history_matrixs.pop()
            self.score = self.history_scores.pop() if self.history_scores else 0
            self.update_grid_cells()

    def key_down(self,event):
        key = event.keysym.lower()
        key_map = {'w':'up','s':'down','a':'left','d':'right','i':'up','k':'down','j':'left','l':'right'}
        if key == 'n':
            self.new_game()
        elif key == 'b':
            self.undo_move()
        elif key in ['up','down','left','right','w','a','s','d','i','j','k','l']:
            self.move(key_map.get(key,key))
        elif key == 'u' and self.auto:
            self.auto.start()
        elif key == 'o' and self.auto:
            self.auto.stop()
