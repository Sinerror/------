import numpy as np
from Mapcolors import COLOR_MAP, non_play_colors
import json


class Hexagon:
    """
    @brief Represents a hexagon on the grid.

    This class defines properties and methods related to a hexagon on the grid, including its color, player, coordinates, and additional data.
    """

    def __init__(self, color, crd):
        """
        @brief Initializes a Hexagon object.

        @complexity O(1) - simple input

        @param color The color of the hexagon.
        @param crd The coordinates of the hexagon.
        """

        self.color = color
        self.player = None
        self.crd = crd
        self.GUIpos = None
        self.data = None

    def __str__(self):
        """
        @brief Returns a string representation of the Hexagon object.

        @complexity O(1) - simple output

        @return str A string containing information about the hexagon's color, player, coordinates, GUI position, and additional data.
        """

        return f"Hexagon: Color - {self.color}, Player - {self.player}, Coordinates - {self.crd}, Center - {self.GUIpos}, Other Data - {self.data}"  # pragma: no cover


class HexGrid:
    """
    @brief Represents a hexagonal grid.

    This class defines properties and methods for generating and manipulating a hexagonal grid.
    """

    def __init__(self, rows, cols):
        """
        @brief Initializes a HexGrid object.

        @complexity O(1) - Simple input

        @param rows The number of rows in the grid.
        @param cols The number of columns in the grid.
        """

        self.rows = abs(int(rows))
        self.cols = abs(int(cols))
        self.grid = self.generate_hex_grid()

    # Функция генерации массива гексагонального поля
    def generate_hex_grid(self):
        """
        @brief Generates a hexagonal grid.

        @complexity O(n1*n2) - cycles for i in range(self.rows) and for j in range(self.cols) have O(n1) and O(n2) respectively

        @return list A 2 dimensional matrix representing the hexagonal grid.
        """

        colors = list(COLOR_MAP.values())

        grid = []
        for color in non_play_colors:
            if color in colors:
                colors.remove(color)

        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(
                    Hexagon(color=np.random.choice(colors), crd=self.offset_to_cube((i, j)))
                )
            grid.append(row)
        return grid

    # Функция конвертации плоских координат в кубические
    def offset_to_cube(self, offset_coord):
        """
        @brief Converts offset coordinates to hexagonal coordinates.

        @complexity O(1) - Simple output

        @param offset_coord The offset coordinates to be converted.
        @return tuple The hexagonal coordinates.
        """

        col, row = offset_coord
        x = col
        z = row - (col - (col & 1)) // 2
        y = -x - z
        return x, y, z

    # Функция конвертации кубических координат в плоские
    def cube_to_offset(self, cube_coord):  # pragma: no cover
        """
        @brief Converts hexagonal coordinates to offset coordinates.

        @complexity O(1) - Simple output

        @param cube_coord The hexagonal coordinates to be converted.
        @return tuple The offset coordinates.
        """

        x, y, z = cube_coord
        col = x
        row = z + (x - (x & 1)) // 2
        return col, row

    # Функция читает данные по кубическим координатам
    def get_value(self, cube_coord):  # pragma: no cover
        """
        @brief Gets the value of a hexagon at the specified hexagonal coordinates.

        @param cube_coord The hexagonal coordinates of the hexagon.
        @return Hexagon The hexagon object.
        """

        x, y, z = cube_coord
        if 0 <= x < self.cols and 0 <= y < self.rows and 0 <= z < min(self.rows, self.cols):
            t_coord = self.cube_to_offset(cube_coord)
            x, y = t_coord
            return self.grid[x][y]

    # Устанавливает стены на поле
    def set_walls(self, wall_positions):
        """
        @brief Sets walls on the grid.

        @complexity O(n) - Cycle for wall in wall_positions have O(n)

        @param wall_positions A list of wall positions.
        """

        for wall in wall_positions:
            x, y = wall
            if (
                0 <= y < self.cols
                and 0 <= x < self.rows
                and not ((y == 0 or y == self.cols and x == 0 or x == self.rows))
            ):
                self.grid[x][y] = Hexagon(color="#000000", crd=self.offset_to_cube((x, y)))
                self.grid[x][self.cols - y - 1] = Hexagon(
                    color="#000000", crd=self.offset_to_cube((x, y))
                )

    # Преобразует себя из формы обьекта Python в JSON
    def json_self(self):
        """
        @brief Converts the HexGrid object to JSON format.

        @complexity O(n1*n2) - cycles for row in self.grid and for or col in row have O(n1) and O(n2) respectively

        @return str The JSON representation of the HexGrid object.
        """

        tmp_grid = []

        for row in self.grid:
            tmp_grid_row = []
            for col in row:
                dic = col.__dict__
                tmp_grid_row.append(dic)
            tmp_grid.append(tmp_grid_row)
        dic = tmp_grid
        return json.dumps(dic)


# Пример использования
# rows = 3
# cols = 3

# Создание объекта класса HexGrid
# hex_grid = HexGrid(rows, cols)

# Вывод сгенерированного гексагонального поля
# print("Hexagonal Grid:")
# print(hex_grid.grid[0][0].color)
# print(json.loads(hex_grid.json_self()))

# Пример определения соседних клеток для заданной клетки

# cube_coord = hex_grid.offset_to_cube((8,8))
# print(cube_coord)
# print(hex_grid.cube_to_offset(cube_coord))
# neighbors = hex_grid.get_neighbors(cube_coord)
# print("Neighbors of", cube_coord, ":", neighbors)
# for i in neighbors:
#    print(hex_grid.cube_to_offset(i))

# print(hex_grid.grid[9,9])
