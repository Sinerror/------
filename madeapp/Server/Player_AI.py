from Players import Player
import math
from Mapcolors import COLOR_MAP, non_play_colors
import copy


class AI_Player(Player):
    """
    @brief Initializes an AI Player object.
    This class represents an AI player in the game, inheriting from the Player class.

    The AI player is capable of making decisions based on certain algorithms.

    @note Inherits attributes and methods from the Player class.
    """

    possible_cells = set()
    possible_color = ""
    is_AI = True

    def calc_flat_score(self, grid_json, Lcells, color):
        """
        @brief Calculates the flat score for the AI player.

        @complexity O(1) - Simple calculation + output

        This method calculates the flat score for the AI player based on various factors such as occupied cells,
        control of key areas, and size of the largest chain.

        @param grid_json The JSON representation of the game grid.
        @param Lcells The cells currently occupied by the player.
        @param color The color chosen by the AI player.
        @return The calculated flat score for the AI player.
        """
        Lcells = copy.copy(Lcells)
        grid_json = copy.deepcopy(grid_json)
        # Score = (w1*Occupied)+(w2*KeyAreasControlBonus)+(w3*LargestChain)+(w4*NextLargestChain)+(w5*OpponentBlockingBonus)
        # ✔1. w1*Occupied = 1 соотведственно - w1 = 1/(колонки*строки) [Бессмысленно чтобы понять какую клетку присоединять]
        # ✔2. KeyAreasControlBonus - Ключевая позиция это занять центр, необходимо проверять какие клетки быстрее преведут к центру. [Не должно быть сильнее 1-2 клеток]
        # 0 - удлинения не произошло , 1 - достигли центра; Возможно реализовать через % удлинения
        # ✔3. LargestChain - Выбор цвета который присоединит максимум клеток; 0 - худший цвет, 1 - лучший цвет
        # ✔4. NextLargestChain - Если определение предыдущего компонента не было слишком ресурсоёмко, то проверяем какой следующий цвет лучше; 0 - худший цвет, 1 - лучший цвет
        # 5. OpponentBlockingBonus - Необходимо блокировать противника. Бонус пара клеток, если выбранный цвет увеличит количество соприкасаемых с противником клеток
        # Без блока не сложно
        # 1:
        W1 = 100
        w1 = 1 / (len(grid_json) * len(grid_json[0])) * W1
        Occupied = len(Lcells)

        # 2:
        W2 = -0.2  # Наказываем за НЕ стремление к центру
        w2_xy = (len(grid_json) / 2, len(grid_json[0]) / 2)

        # Функция для вычисления расстояния между двумя точками
        def distance(point1, point2):
            """
            @brief Calculates the Euclidean distance between two points.

            @complexity O(1) - Simple calculations

            This function calculates the Euclidean distance between two points in a two-dimensional space.

            @param point1 The coordinates of the first point as a tuple (x, y).
            @param point2 The coordinates of the second point as a tuple (x, y).
            @return The Euclidean distance between the two points.
            """
            return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

        # Находим ближайшую клетку к w2_xy (центру поля) [Лишнее действие но может пригодится дл оптимизации]
        nearest_coordinate = min(Lcells, key=lambda point: distance(w2_xy, point))

        # вычисляем Бонус за контроль ключевых точек
        KeyAreasControlBonus = distance(w2_xy, nearest_coordinate)
        # 3:

        W3 = 1
        LargestChain = 0

        cells, _ = self.ai_choose_color(color, grid_json, Lcells)
        LargestChain = max(LargestChain, len(cells))

        LargestChain = LargestChain - len(Lcells)

        Score = (w1 * Occupied) + (W2 * KeyAreasControlBonus) + (W3 * LargestChain)
        return Score

    def make_turn(self, grid_json):
        """
        @brief Makes a calculation of turn for the AI player.
        This method implements the Alpha-Beta Pruning algorithm to determine the best move for the AI player.

        @complexity O(n) - Cycle for color in non_play_colors have complexity O(n)

        @param grid_json The JSON representation of the game grid.
        @return The best move determined by the AI player.
        """
        # 4.
        colors = list(COLOR_MAP.values())

        for color in non_play_colors:
            if color in colors:
                colors.remove(color)

        def alphabeta(board, depth, alpha, beta, maximizing_player, Lcells, Lmove=None):
            """
            @brief Implements the Alpha-Beta Pruning algorithm for decision making.

            @complexity O(n1^n2), where n1 is the average number of possible moves in each position, and n2 is the depth of the search tree

            This function implements the Alpha-Beta Pruning algorithm to determine the best move for the AI player.
            It evaluates the possible moves up to a certain depth and returns the best move along with its score.

            @param board The current state of the game board represented as a JSON.
            @param depth The depth of the search tree to explore.
            @param alpha The alpha value for alpha-beta pruning.
            @param beta The beta value for alpha-beta pruning.
            @param maximizing_player A boolean indicating whether the current player is maximizing.
            @param Lcells The cells currently occupied by the AI player.
            @param Lmove The last move made by the AI player.
            @return A tuple containing the best move and its corresponding score.
            """

            if depth == 0 or len(self.check_possible_moves(board, Lcells)) == 0:
                # Вычисление оценки текущей позиции
                score = self.calc_flat_score(board, Lcells, Lmove)
                return Lmove, score  # Возвращаем ход None и его оценку

            if maximizing_player:
                max_eval = -math.inf
                best_move = None
                for move in colors:
                    # Применяем ход
                    new_cells, new_board = self.ai_choose_color(move, grid_json, Lcells)
                    _, eval = alphabeta(new_board, depth - 1, alpha, beta, False, new_cells, move)
                    max_eval = max(eval, max_eval)
                    if max_eval > alpha:
                        alpha = max_eval
                        best_move = move
                    if beta <= alpha:
                        break  # pragma: no cover
                return best_move, alpha
            else:
                min_eval = math.inf
                best_move = None
                for move in colors:
                    # Применяем ход
                    new_cells, new_board = self.ai_choose_color(move, grid_json, Lcells)
                    _, eval = alphabeta(new_board, depth - 1, alpha, beta, True, new_cells, move)
                    min_eval = min(eval, min_eval)
                    if min_eval < beta:
                        beta = min_eval
                        best_move = move
                    if beta <= alpha:
                        break
                return best_move, beta

        board = copy.deepcopy(grid_json)
        depth = 2
        Cells = copy.copy(self.cells)
        best_move, best_score = alphabeta(board, depth, -math.inf, math.inf, True, Cells)
        print(best_move, best_score)

        return best_move

    # Функция псевдо выбираец цвет и обновляет possible_cells в соотведствии с этим (должно работать и с possible_cells в т.ч.)
    """
    def Quazi_choose_color(self, color, grid_json, Lcells):
        self.possible_color = color
        moves = set()
        pos_moves = set()
        Cells = Lcells
        for i in Lcells: # cells = self.possible_cells = {} или self.cells
            moves.update(self.get_neighbors(grid_json, self.offset_to_cube(i)))

        for j in moves:
            y,x = j
            Lcell = grid_json[x][y]
            if Lcell["player"] == None:
                pos_moves.add(j)

        visited = set()
        left = pos_moves
        leftadd = set()

        while True: #Цикл выполняется пока не будет завершён
            for i in left:
                visited.add(i) #Проверенные элементы заносятся в множество
                y,x = i
                Lcell = grid_json[x][y] #Получаем клетку по координатам

                if Lcell["color"] == color and Lcell["player"] == None: #Если клетка цвета выбранного игроком
                    Cells.add(i) #Добавляем клетку в массив возможных
                    leftadd.update(self.get_neighbors(grid_json, self.offset_to_cube(i))) #Проверяем соседей клетки (Проверка на цветные кластеры)

            left.update(leftadd) # Добавляем что осталось проверить
            left = left.difference(visited) # Вычитаем что уже проверено
            leftadd = set()
            if not left: #Если нечего проверять то выходим
                break
        return copy.copy(Cells)
    """

    # Функция псевдоходов Для просчитывания позиции
    def ai_choose_color(self, color, grid_json, cells):
        """
        @brief Simulates color selection for AI player to calculate the position.

        @complexity O(n+ထ) - Cycle for j in Lcells have O(n). Cycle while True have O(ထ) in worst scenario.

        This method simulates the selection of color for the AI player to calculate the position and determine the potential moves.

        @param color The color to be selected.
        @param grid_json The JSON representation of the game grid.
        @param cells The cells currently occupied by the AI player.
        @return A tuple containing the updated set of cells after the color selection and the updated game grid JSON.
        """

        grid_json = copy.deepcopy(grid_json)
        Lcells = copy.copy(cells)

        for j in Lcells:  # некрасива
            y, x = j
            grid_json[x][y].update({"color": color})

        visited = set()
        left = self.check_possible_moves(grid_json, Lcells)
        leftadd = set()

        while True:  # Цикл выполняется пока не будет завершён
            for i in left:
                visited.add(i)  # Проверенные элементы заносятся в множество
                y, x = i
                cell = grid_json[x][y]  # Получаем клетку по координатам

                if (
                    cell["color"] == color and cell["player"] == None
                ):  # Если клетка цвета выбранного игроком # pragma: no cover
                    Lcells.add(i)  # Добавляем клетку игроку

                    leftadd.update(
                        self.get_neighbors(grid_json, self.offset_to_cube(i))
                    )  # Проверяем соседей клетки (Проверка на цветные кластеры)

                    grid_json[x][y].update(
                        {"player": "AI"}
                    )  # Добавляем клетке игрока, у нас не односторонние отношения

            left.update(leftadd)  # Добавляем что осталось проверить
            left = left.difference(visited)  # Вычитаем что уже проверено
            leftadd = set()
            if not left:  # Если нечего проверять то выходим
                break

        return Lcells, grid_json
