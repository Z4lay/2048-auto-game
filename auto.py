import random
import copy
import math
import logic  # 假设 logic.py 中包含 up, down, left, right, add_two 函数

class Auto2048:
    def __init__(self, game, speed=100, mc_simulations=10, mc_depth=4):
        self.game = game
        self.speed = speed
        self.running = False
        self.directions = ['up', 'down', 'left', 'right']
        
        self.mc_simulations = mc_simulations  # 模拟次数
        self.mc_depth = mc_depth              # 搜索深度
        self.game.auto = self
        
        # 定义新的锚点：右下角 (3, 3)
        self.anchor_position = (3, 3)

    # --- 核心辅助函数：计算单调性和平滑度 ---

    def calculate_monotonicity(self, board):
        """
        计算棋盘的单调性。奖励数字向左和向上递减排列（从右下角开始）。
        """
        score = 0
        
        # 1. 行单调性：鼓励从右到左递减
        for i in range(4):
            current_row = [tile for tile in board[i] if tile != 0]
            if len(current_row) < 2:
                continue

            # 权重：惩罚递增的趋势 (从左到右)
            for j in range(len(current_row) - 1):
                val1 = math.log2(current_row[j])     # 左侧数字
                val2 = math.log2(current_row[j+1])   # 右侧数字
                
                # 我们希望 val2 > val1 (即从左到右递增，但为了右下角锚定策略，我们希望 val2 < val1)
                # 惩罚 val2 > val1 的情况（即左侧小，右侧大，这不符合右侧大数字的策略）
                if val2 > val1:
                    score -= (val2 - val1) * 2  # 惩罚从左到右递增

        # 2. 列单调性：鼓励从下到上递减
        for j in range(4):
            # 获取当前列，从上到下
            current_col = [board[i][j] for i in range(4) if board[i][j] != 0]
            if len(current_col) < 2:
                continue
            
            # 权重：惩罚向下的趋势 (从上到下递增)
            for i in range(len(current_col) - 1):
                val1 = math.log2(current_col[i])     # 上方数字
                val2 = math.log2(current_col[i+1])   # 下方数字
                
                # 惩罚 val2 > val1 的情况（即上方小，下方大，这不符合下方大数字的策略）
                if val2 > val1:
                    score -= (val2 - val1) * 2 # 惩罚从上到下递增

        # 因为惩罚项是负数，所以最终分数会奖励单调性好的局面
        return score

    def calculate_smoothness(self, board):
        """
        计算平滑度。奖励相邻方块数值相等或接近。
        """
        score = 0
        for i in range(4):
            for j in range(4):
                if board[i][j] != 0:
                    current_log = math.log2(board[i][j])
                    
                    # 检查右侧邻居
                    if j < 3 and board[i][j+1] != 0:
                        neighbor_log = math.log2(board[i][j+1])
                        score -= abs(current_log - neighbor_log) * 1.5

                    # 检查下方邻居
                    if i < 3 and board[i+1][j] != 0:
                        neighbor_log = math.log2(board[i+1][j])
                        score -= abs(current_log - neighbor_log) * 1.5
        
        # 平滑度：差值越小，分数惩罚越少 (即分数越高)
        return score

    def evaluate_board(self, board):
        """根据右下角锚定策略计算分数"""
        score = 0
        empty_spaces = sum(row.count(0) for row in board)
        
        max_tile = max(max(row) for row in board)
        
        # 1. 空格数量奖励 (高权重)
        score += empty_spaces * 80  # 增加权重，鼓励留下更多空格

        # 2. 单调性奖励 (Monotonicity)
        score += self.calculate_monotonicity(board) * 30 

        # 3. 平滑度奖励 (Smoothness)
        score += self.calculate_smoothness(board) * 15
        
        # 4. 最大数字位置惩罚 (Corner Priority)
        # 锚点：右下角 (3, 3)
        anchor_i, anchor_j = self.anchor_position
        
        # 惩罚：如果最大数字不在锚点
        if board[anchor_i][anchor_j] != max_tile:
            score -= 1000 # 极大的惩罚，强制锁定

        # 惩罚：如果锚点方块不是最大方块，且其值很小 (例如 2, 4)
        if board[anchor_i][anchor_j] < max_tile and board[anchor_i][anchor_j] in [2, 4]:
            score -= 500

        # 5. 位置权重：鼓励大数字靠近右下角
        for i in range(4):
            for j in range(4):
                if board[i][j] != 0:
                    # 距离右下角越近，权重越高
                    # 3-i: 越靠下越大; j: 越靠右越大
                    weight = (i) * 0.5 + (3 - j) * 0.5 
                    score += math.log2(board[i][j]) * weight

        return score
    
    # --- 搜索与决策：蒙特卡洛优化 ---
    
    # 保持 find_greedy_move 和 monte_carlo_best_move 不变，
    # 因为它们依赖于上面优化的 evaluate_board 函数来做出决策。
    # ... (find_greedy_move 和 monte_carlo_best_move 保持与上一个回复中的实现一致) ...
    
    def find_greedy_move(self, board):
        """
        快速启发式函数：在蒙特卡洛模拟中，选择能产生最高评估分数的单步移动。
        """
        best_dir = None
        best_score = -float('inf')

        for direction in self.directions:
            board_copy = copy.deepcopy(board)
            
            # 使用逻辑函数移动一步
            board_moved, moved, _ = getattr(logic, direction)(board_copy)

            if moved:
                # 评估移动后的棋盘状态 (不添加新数字)
                current_score = self.evaluate_board(board_moved)
                if current_score > best_score:
                    best_score = current_score
                    best_dir = direction
        
        return best_dir if best_dir else random.choice(self.directions)


    def monte_carlo_best_move(self):
        """使用蒙特卡洛模拟选择最优移动方向"""
        best_dir = None
        best_score = -float('inf')
        max_tile = max(max(row) for row in self.game.matrix)
        anchor_i, anchor_j = self.anchor_position

        for direction in self.directions:
            board_start = copy.deepcopy(self.game.matrix)
            
            # 1. 执行目标方向的首次移动
            # 这一步是关键：检查移动是否会导致最大方块离开锚点
            
            # 记录最大方块在移动前的位置
            max_tile_pre_move = board_start[anchor_i][anchor_j]
            
            board_moved, moved_start, score_start = getattr(logic, direction)(board_start)
            
            if not moved_start:
                continue # 无法移动，跳过

            # 严格防止最大方块离开锚点：如果移动后锚点的值变小了，则惩罚（除非锚点本来就不是最大值）
            if max_tile_pre_move == max_tile and board_moved[anchor_i][anchor_j] < max_tile:
                # 如果最大方块被推出了锚点，则大幅降低本次移动的评分，避免选择它
                current_total_score = -200000 
            else:
                current_total_score = 0
                for _ in range(self.mc_simulations):
                    board_sim = copy.deepcopy(board_moved)
                    
                    # 模拟新增数字
                    board_sim = logic.add_two(board_sim) 
                    
                    for _ in range(self.mc_depth):
                        # 使用贪心策略选择后续移动
                        next_dir = self.find_greedy_move(board_sim) 
                        
                        board_sim, moved_next, _ = getattr(logic, next_dir)(board_sim)
                        
                        if not moved_next:
                            break 
                            
                        # 模拟新增数字
                        board_sim = logic.add_two(board_sim)

                    current_total_score += self.evaluate_board(board_sim)
            
            avg_score = current_total_score / self.mc_simulations
            
            if avg_score > best_score:
                best_score = avg_score
                best_dir = direction

        return best_dir

    # --- 运行控制 ---

    def auto_step(self):
        if self.running:
            best_move = self.monte_carlo_best_move()
            
            if best_move:
                self.game.move(best_move)
                self.game.after(self.speed, self.auto_step)
            else:
                print("自动操作：无有效移动，游戏可能结束。")
                self.stop()


    def start(self):
        if not self.running:
            self.running = True
            self.auto_step()
            print("自动操作启动")

    def stop(self):
        self.running = False
        print("自动操作停止")