class Player:
    """
    @brief Initializes a Player object.
    This class represents a player in the game.

    @param name The name of the player.
    @param color The color chosen by the player.
    @param initial_position The initial position of the player on the grid.
    @param grid_json The JSON representation of the game grid.
    """

    def __init__(self, name, color, initial_position, grid_json):
        """
        @brief Checks the possible moves for the player.

        @complexity O(1) - Simple input

        This method checks the possible moves for the player based on the current grid state and player's cells.

        @param grid_json The JSON representation of the game grid.
        @param cells The cells currently occupied by the player.
        @return A set of possible moves for the player.
        """

        self.name = name
        self.color = color
        self.position = initial_position
        self.cells = {initial_position}
        self.possible_moves = set()
        self.IsTurn = False
        self.is_AI = False
        x, y = initial_position
        grid_json[y][x].update({"color": color})
        grid_json[y][x].update({"player": name})

    def check_possible_moves(self, grid_json, cells):
        """
        @brief Allows the player to choose a color.
        This method allows the player to choose a color and updates the grid accordingly.

        @complexity O(2n) - cycles for i in cells and for j in moves are the same and have O(n)

        @param color The color chosen by the player.
        @param grid_json The JSON representation of the game grid.
        """

        moves = set()
        Lpossible_moves = set()
        for i in cells:
            moves.update(self.get_neighbors(grid_json, self.offset_to_cube(i)))
        for j in moves:
            y, x = j
            cell = grid_json[x][y]
            if cell["player"] == None and j not in cells:
                Lpossible_moves.add(j)
        return Lpossible_moves

    def choose_color(self, color, grid_json):
        """
        @brief Allows the player to choose a color.
        This method allows the player to choose a color and updates the grid accordingly.

        @complexity O(n+ထ) - cycle for j in self.cells have O(n). Cycle while True have O(ထ) in worst scenario.

        @param color The color chosen by the player.
        @param grid_json The JSON representation of the game grid.
        """
        self.color = color

        for j in self.cells:  # некрасива
            y, x = j
            grid_json[x][y].update({"color": self.color})

        visited = set()
        left = self.check_possible_moves(grid_json, self.cells)
        leftadd = set()

        while True:  # Цикл выполняется пока не будет завершён
            for i in left:
                visited.add(i)  # Проверенные элементы заносятся в множество
                y, x = i
                cell = grid_json[x][y]  # Получаем клетку по координатам

                if (
                    cell["color"] == color and cell["player"] == None
                ):  # Если клетка цвета выбранного игроком # pragma: no cover
                    self.cells.add(i)  # Добавляем клетку игроку

                    leftadd.update(
                        self.get_neighbors(grid_json, self.offset_to_cube(i))
                    )  # Проверяем соседей клетки (Проверка на цветные кластеры)

                    grid_json[x][y].update(
                        {"player": self.name}
                    )  # Добавляем клетке игрока, у нас не односторонние отношения

            left.update(leftadd)  # Добавляем что осталось проверить
            left = left.difference(visited)  # Вычитаем что уже проверено
            leftadd = set()
            if not left:  # Если нечего проверять то выходим
                break

    # Функции для работы с Json_grid

    # Функция определения соседних клеток для заданной клетки в массиве
    def get_neighbors(self, grid, cube_coord):
        """
        @brief Retrieves the neighboring cells for a given cell in the grid.
        This function retrieves the neighboring cells for a given cell in the grid.

        @complexity O(n) - cycle for i in neighbors is O(n)

        @param grid The grid of the game.
        @param cube_coord The coordinates of the cell in cube representation.
        @return A list of neighboring cells.
        """

        x, y, z = cube_coord
        neighbors = [
            (x + 1, y - 1, z),
            (x + 1, y, z - 1),
            (x, y + 1, z - 1),
            (x - 1, y + 1, z),
            (x - 1, y, z + 1),
            (x, y - 1, z + 1),
        ]
        valid_neighbors = []
        for i in neighbors:
            x1, y1 = self.cube_to_offset(i)
            if 0 <= x1 < len(grid[0]) and 0 <= y1 < len(grid):
                valid_neighbors.append((x1, y1))
        return valid_neighbors

    # Функция конвертации кубических координат в плоские
    def cube_to_offset(self, cube_coord):
        """
        @brief Converts cube coordinates to offset coordinates.
        This function converts cube coordinates to offset coordinates.

        @complexity O(1) - Simple output

        @param cube_coord The cube coordinates to be converted.
        @return The corresponding offset coordinates.
        """
        x, y, z = cube_coord
        col = x
        row = z + (x - (x & 1)) // 2
        return col, row

    # Функция конвертации плоских координат в кубические
    def offset_to_cube(self, offset_coord):
        """
        @brief Converts offset coordinates to cube coordinates.
        This function converts offset coordinates to cube coordinates.

        @complexity O(1) - Simple output

        @param offset_coord The offset coordinates to be converted.
        @return The corresponding cube coordinates.
        """
        col, row = offset_coord
        x = col
        z = row - (col - (col & 1)) // 2
        y = -x - z
        return x, y, z
