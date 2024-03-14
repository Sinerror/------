from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from Mapgen import HexGrid
import json
from Players import Player
from Player_AI import AI_Player
import uuid
import random
import logging
import os

"""
@file
@brief This is Main server file called "Catcher"

This is Main server file. Execute it to start game server and connect to / to accces the game
"""

app = Flask(__name__, template_folder="./templates")
CORS(app, origins="*")  # origins=['file://', 'http://', 'https://'])
socketio = SocketIO(app)

gamesroute = "./Server/games/"

rows = 21  # настройки
cols = 47  # настройки

num_walls = 0

a_grid = 0  # global

Players = []  # global
OBJPlayers = []  # global

CurrentTurn = ""  # global

num_of_players = 2  # 2-4 -> config

game_is_running = False

if not os.path.exists("logs"):
    os.makedirs("logs")  # pragma: no cover

log_file_path = os.path.join("logs", "app.log")

logging.basicConfig(filename=log_file_path, level=logging.DEBUG)

error_log_file_path = os.path.join("logs", "error.log")

file_handler = logging.FileHandler(error_log_file_path)
file_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)
app.logger.addHandler(stream_handler)

### Страницы


@app.route("/")
def menu():
    """
    @brief Renders the menu page.

    @complexity O(1) - Simple output

    Renders the Menu.html template when the root URL is accessed.
    """
    app.logger.info("Rendering menu page")
    return render_template("Menu.html")


@app.route("/game")
def game():
    """
    @brief Renders the game page.

    @complexity O(1) - Simple output

    Renders the GUI.html template when the /game URL is accessed.
    """
    app.logger.info("Rendering game page")
    return render_template("GUI.html")


@app.route("/docs")
def docs():
    """
    @brief Renders the documentation page.

    @complexity O(1) - Simple output

    Renders the docs.html template when the /docs URL is accessed.
    """
    app.logger.info("Rendering documentation page")
    return render_template("docs.html")


### Подключения

connected_clients = {}
player_id_map = {}


@socketio.on("connect")
def handle_connect():
    """
    @brief Handles client connection.

    @complexity O(n) - Array Insertion O(n)

    Handles client connection events and adds the client to the list of connected clients.
    """

    client_id = request.sid
    global connected_clients
    connected_clients[client_id] = True
    app.logger.info("Client connected: %s", client_id)


@socketio.on("message")
def handle_message(message):
    """
    @brief Handles receiving messages from clients.

    @complexity O(1) - Simple output

    Handles receiving messages from clients. Currently, it only prints the received message.

    @param message The received message.
    """
    app.logger.info("Received message: %s", message)


# Чей ход?
@socketio.on("get_turn")
def send_turn_info():
    """
    @brief Sends information about the current turn.

    @complexity O(1) - Simple output

    Sends information about the current turn to clients upon receiving a 'get_turn' event.
    """
    app.logger.info("Sending turn information")
    socketio.emit("turn", CurrentTurn)


@socketio.on("disconnect")
def handle_disconnect():
    """
    @brief Handles client disconnection.

    @complexity O(n) - Array Deletion O(n)

    Handles client disconnection events and removes the client from the list of connected clients.
    """
    client_id = request.sid
    global connected_clients
    connected_clients.pop(client_id, None)
    app.logger.info("Client disconnected: %s", client_id)


### Функции


@app.route("/wait_room", methods=["POST"])
def waitroom():
    """
    @brief Handles player registration and game start.

    @complexity O(1) - Access to Dictionary O(1) + Insertion to Dictionary O(1)

    This route handles player registration and starts the game once the required number of players
    has joined. If an AI player is included, it is also added to the player list.

    @return JSON The response indicating whether the game has started and the player ID.
    """
    app.logger.info("Handling wait room request")

    # Получаем данные (Имя игрока) из запроса
    print(request.json)
    player = request.json["Player"]
    is_AI = request.json["Use_AI"]
    player_id = register(player)
    global Players
    if is_AI:
        Players.append("AI")  # pragma: no cover
    if player in Players:
        if len(Players) == num_of_players:  # pragma: no cover
            app.logger.info("Starting game...")
            gamestart(Players)  # Начинаем игру
            return jsonify({"Gamestarted": True, "id": player_id}), 200
        else:
            return jsonify({"Gamestarted": False, "id": player_id}), 200

    Players.append(player)  # Превратить в множество

    app.logger.info("%s joined the game", player)
    app.logger.debug("Current players: %s", Players)

    if len(Players) == num_of_players:
        app.logger.info("Starting game...")
        gamestart(Players)  # Начинаем игру
        return jsonify({"Gamestarted": True, "id": player_id})
    elif len(Players) > num_of_players:
        Players = []
        app.logger.error("Error: too many Players")
        return jsonify({"Gamestarted": False, "id": player_id}), 501
    return jsonify({"Gamestarted": False, "id": player_id}), 200


# Присваиваем каждому юзеру уникальный индитификатор
def register(player_name):
    """
    @brief Registers a player and assigns them a unique identifier.

    @complexity O(1) - Insertion to Dictionary O(1)

    This function registers a player by assigning them a unique identifier and storing the mapping
    between the player's ID and name.

    @param player_name The name of the player.
    @return str The unique identifier assigned to the player.
    """

    player_name = request.json.get("player_name")
    if player_name:
        player_id = str(uuid.uuid4())
        player_id_map[player_id] = player_name
        app.logger.info(f"Player {player_name} registered with ID {player_id}")
        return player_id
    else:
        app.logger.error("No player name provided during registration")
        return None


@app.route("/wait_room", methods=["DELETE"])
def clearplayer():
    """
    @brief Removes a player from the player list.

    @complexity O(1) - Access to Dictionary O(1) + Deletion in Dictionary O(1)

    This route removes a player from the player list when they leave the waiting room.

    @return JSON The response indicating whether the player was successfully removed.
    """
    player = request.json.get("Player")
    if player:
        if player in Players:
            Players.remove(player)
            app.logger.info(f"Player {player} removed from waiting room")
            return jsonify(True), 200
        else:
            app.logger.warning(f"Player {player} not found in waiting room")
            return jsonify(False), 200
    else:  # pragma: no cover
        app.logger.error("No player specified for removal")
        return jsonify(False), 400


# Отправить игроку поле
@app.route("/send_grid", methods=["GET"])
def sendgrid():
    """
    @brief Sends the game grid to the client.

    @complexity O(1) - Simple output

    This route sends the current state of the game grid to the client in JSON format.

    @return JSON The current state of the game grid.
    """
    # Отправляем сетку игры клиенту в формате JSON
    with open(gamesroute + "currentgame.json", "r") as json_file:
        data = json.load(json_file)
    app.logger.debug("Sent game grid to client")
    return jsonify(data)


# Обработка хода игрока
@app.route("/turn", methods=["POST"])
def edit_turn():
    """
    @brief Processes a player's move.

    @complexity O(n) - cycle for in range(len(OBJPlayers)) have O(n); call for other function: [Player Object].choose_color(color, grid)

    This route processes a player's move by updating the game grid with the chosen color.
    If it's the AI's turn, the AI player makes a move automatically.

    @return JSON True if the move was successfully processed; otherwise, False.
    """

    Player = request.json["Player"]
    color = request.json["Color"]
    global CurrentTurn
    CurrentPlayerIndex = 0

    for i in range(len(OBJPlayers)):
        if OBJPlayers[i].name == CurrentTurn:
            CurrentPlayerIndex = i
            break

    if Player != CurrentTurn:
        app.logger.warning(f"Invalid turn by {Player}. It's {CurrentTurn}'s turn.")
        return jsonify(False)

    # Смотрим что у нас в сетке
    with open(gamesroute + "currentgame.json", "r") as json_file:
        data = json.load(json_file)

    grid = data

    OBJPlayers[CurrentPlayerIndex].choose_color(color, grid)
    app.logger.info(f"Player {Player} chose color {color}")

    with open(gamesroute + "currentgame.json", "w") as grid_file:
        json.dump(grid, grid_file)

    if CurrentPlayerIndex + 1 >= len(OBJPlayers):
        CurrentPlayerIndex -= len(OBJPlayers)
    CurrentTurn = OBJPlayers[CurrentPlayerIndex + 1].name

    if is_game_over():
        game_over()
        app.logger.info("Game over")

    if CurrentTurn == "AI":
        AI_turn()
        app.logger.info("AI's turn")

    return jsonify(True)


def AI_turn():
    """
    @brief Processes the AI player's move.

    @complexity O(n) - cycle for in range(len(OBJPlayers)) have O(n); call for other functions: [AI_Player Object].make_turn(grid), [Player Object].choose_color(color, grid)

    This function processes the AI player's move by automatically choosing a color and updating the game grid.
    """

    Player = "AI"
    global CurrentTurn
    CurrentPlayerIndex = 0
    for i in range(len(OBJPlayers)):
        if OBJPlayers[i].name == CurrentTurn:
            CurrentPlayerIndex = i
            break

    # Смотрим что у нас в сетке
    with open(gamesroute + "currentgame.json", "r") as json_file:
        data = json.load(json_file)

    grid = data
    AI_choise = OBJPlayers[CurrentPlayerIndex].make_turn(grid)
    OBJPlayers[CurrentPlayerIndex].choose_color(AI_choise, grid)
    app.logger.info(f"AI chose color {AI_choise}")

    with open(gamesroute + "currentgame.json", "w") as grid_file:
        json.dump(grid, grid_file)

    if CurrentPlayerIndex + 1 >= len(OBJPlayers):
        CurrentPlayerIndex -= len(OBJPlayers)  # pragma: no cover
    CurrentTurn = OBJPlayers[CurrentPlayerIndex + 1].name

    if is_game_over():
        game_over()  # pragma: no cover
        app.logger.info("Game over")  # pragma: no cover


# Обработка начала игры
def gamestart(Players_name):
    """
    @brief Handles the start of the game.

    @complexity O(n) - cycle for i in Players_name have O(n); call for other functions: [HexGrid Object].__init__, [HexGrid Object].set_walls(walls)

    This function initializes the game by creating the game grid, setting up player objects,
    determining the initial turn, and sending the game grid to the client.

    @param Players_name A list of player names participating in the game.
    @return JSON The initial game grid.
    """

    a_grid = HexGrid(rows, cols)
    if a_grid:
        app.logger.info("HexGrid Object was created")  # pragma: no cover
    else:
        app.logger.errro("HexGrid Object wasn't created")  # pragma: no cover

    walls = [(1, 1), (1, 2)]

    global num_walls
    num_walls = len(walls) * 2

    a_grid.set_walls(walls)

    app.logger.info("Added walls to HexGrid Object")

    json_grid = json.loads(a_grid.json_self())
    colors = [
        "#ADD8E6",
        "#FFFF00",
        "#FFC0CB",
        "#FFA500",
    ]
    initial_positions = [
        (0, 0),
        (a_grid.cols - 1, 0),
        (a_grid.rows - 1, a_grid.cols - 1),
        (0, a_grid.rows - 1),
    ]

    j = 0

    for i in Players_name:
        global OBJPlayers
        if i == "AI":
            OBJPlayers.append(AI_Player(i, colors[j], initial_positions[j], json_grid))
        else:
            OBJPlayers.append(Player(i, colors[j], initial_positions[j], json_grid))
        j += 1

    global CurrentTurn
    if not game_is_running:
        real_Players_name = [x for x in Players_name if x != "AI"]
        CurrentTurn = random.choice(real_Players_name)

    app.logger.info("First turn was chosen")

    with open(gamesroute + "currentgame.json", "w") as grid_file:
        json.dump(json_grid, grid_file)

    # Отправляем сетку игры клиенту в формате JSON
    with open(gamesroute + "currentgame.json", "r") as json_file:
        data = json.load(json_file)

    app.logger.info("Game started")
    return jsonify(data)


def is_game_over():
    """
    @brief Checks if the game is over.

    @complexity O(n) -  cycle for i in OBJPlayers have O(n);

    This function checks if the game is over by comparing the total number of cells in the grid
    with the number of cells occupied by players.

    @return bool True if the game is over; otherwise, False.
    """

    with open(gamesroute + "currentgame.json", "r") as json_file:
        data = json.load(json_file)

    field = len(data) * len(data[0])
    players_cells = 0

    for i in OBJPlayers:
        players_cells += len(i.cells)

    if field - num_walls <= players_cells:
        app.logger.debug("Game over check: True")
        return True
    else:
        app.logger.debug("Game over check: False")
        return False


def game_over():
    """
    @brief Handles the end of the game.

    @complexity O(n) -  cycle for i in OBJPlayers have O(n);

    This function determines the winner of the game and emits a "GameOver" event to the client
    with the name of the winner.
    """

    winner = OBJPlayers[0]

    for i in OBJPlayers:
        if len(winner.cells) < len(i.cells):
            winner = i  # pragma: no cover
    socketio.emit("GameOver", winner.name)
    app.logger.info("Game over. Winner: %s", winner.name)


if __name__ == "__main__":
    app.run(debug=True)  # pragma: no cover
