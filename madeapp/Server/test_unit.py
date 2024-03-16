import unittest
from unittest.mock import MagicMock, patch
import json
import os
from HtmlTestRunner import HTMLTestRunner
from Catcher import app
from Catcher import (
    handle_connect,
    handle_message,
    send_turn_info,
    handle_disconnect,
    waitroom,
    register,
    clearplayer,
    sendgrid,
    edit_turn,
    AI_turn,
    gamestart,
    is_game_over,
    game_over,
)
from Player_AI import AI_Player
from Mapgen import HexGrid


class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        global connected_clients
        connected_clients = {}
        # Создаем заглушку для CurrentTurn
        global CurrentTurn
        CurrentTurn = "MockTurn"
        # Мы можем использовать MagicMock для имитации объектов, которые мы не хотим тестировать напрямую
        self.request = MagicMock()
        self.request.sid = "dummy_client_id"
        self.socketio = MagicMock()

    def tearDown(self):
        self.app_context.pop()

    def test_menu_route(self):
        with self.app as client:
            response = client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"<!DOCTYPE html>", response.data)

    def test_game_route(self):
        with self.app as client:
            response = client.get("/game")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"<!DOCTYPE html>", response.data)

    def test_docs_route(self):
        with self.app as client:
            response = client.get("/docs")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"<!DOCTYPE html>", response.data)

    @patch("Catcher.app")
    def test_handle_message(self, mock_app):
        # Mocking app object
        mock_app.logger.info = MagicMock()

        # Calling the function to be tested
        handle_message("Test message")

        # Asserting that the logger was called with the correct arguments
        mock_app.logger.info.assert_called_once_with("Received message: %s", "Test message")

    def test_send_turn_info(self):
        # Calling send_turn_info function
        send_turn_info()

        # Asserting that turn information is sent
        self.assertTrue(self.socketio.emit.called_with("turn", CurrentTurn))

    def test_waitroom_game_started(self):
        # Mocking request object
        mocked_request = MagicMock()
        mocked_request.json = {"Player": "Player1", "Use_AI": False}
        mocked_request.json = {"Player": "Player2", "Use_AI": False}

        # Mocking app.logger object
        mocked_app_logger = MagicMock()

        # Mocking response object
        mocked_response = MagicMock()

        # Setting up the application context
        with (
            patch("Catcher.request", mocked_request),
            patch("Catcher.request", mocked_request),
            patch("Catcher.app.logger", mocked_app_logger),
            patch("Catcher.jsonify", MagicMock(return_value=mocked_response)),
        ):

            # Calling the function to be tested
            response = waitroom()

        # Asserting that the game started response is correct
        self.assertEqual(response, mocked_response)

    def test_waitroom_game_not_started(self):
        # Mocking request object
        mocked_request = MagicMock()
        mocked_request.json = {"Player": "Player1", "Use_AI": False}

        # Mocking app.logger object
        mocked_app_logger = MagicMock()

        # Mocking response object
        mocked_response = MagicMock()

        # Setting up the application context
        with (
            patch("Catcher.request", mocked_request),
            patch("Catcher.request", mocked_request),
            patch("Catcher.app.logger", mocked_app_logger),
            patch("Catcher.jsonify", MagicMock(return_value=mocked_response)),
        ):

            # Calling the function to be tested
            response = waitroom()

        # Asserting that the game not started response is correct
        self.assertEqual(response, (mocked_response, 200))

    @patch("Catcher.uuid")
    @patch("Catcher.request")
    @patch("Catcher.app")
    def test_register(self, mock_app, mock_request, mock_uuid):
        # Mocking request and app objects
        mock_request.json.get.return_value = "Player1"
        mock_uuid.uuid4.return_value = "unique_id"
        mock_app.logger.info = MagicMock()

        # Calling the function to be tested
        response = register("Player1")

        # Asserting that the response is correct
        self.assertEqual(response, "unique_id")

    @patch("Catcher.request")
    @patch("Catcher.app")
    def test_clearplayer_player_found(self, mock_app, mock_request):
        # Mocking request and app objects
        mock_request.json.get.return_value = "Player1"
        mock_app.logger.info = MagicMock()

        # Calling the function to be tested
        response = clearplayer()

        # Asserting that the response is correct
        self.assertTrue(response)

    @patch("Catcher.request")
    @patch("Catcher.app")
    def test_clearplayer_player_not_found(self, mock_app, mock_request):
        # Mocking request and app objects
        mock_request.json.get.return_value = "Player1"
        mock_app.logger.warning = MagicMock()

        # Calling the function to be tested
        response = clearplayer()

        # Asserting that the response is correct
        self.assertFalse(response)

    @patch("Catcher.open")
    @patch("Catcher.json")
    @patch("Catcher.app")
    def test_sendgrid(self, mock_app, mock_json, mock_open):
        # Mocking app object
        mock_app.logger.debug = MagicMock()

        # Mocking json file data
        mock_json.load.return_value = {"grid": "data"}

        # Calling the function to be tested
        response = sendgrid()

        # Asserting that the response is correct
        self.assertEqual(response.json, {"grid": "data"})

    def test_register(self):
        # Mocking request object
        mocked_request = MagicMock()
        mocked_request.json.get.return_value = "Test Player"

        # Mocking uuid.uuid4() function to return a specific value
        mocked_uuid = MagicMock(return_value="mocked_uuid")

        # Mocking app.logger object
        mocked_app_logger = MagicMock()

        # Setting up the application context
        with (
            patch("Catcher.request", mocked_request),
            patch("Catcher.uuid.uuid4", mocked_uuid),
            patch("Catcher.app.logger", mocked_app_logger),
        ):

            # Calling the function to be tested
            player_id = register("Test Player")

        # Asserting that the player was registered correctly
        self.assertEqual(player_id, "mocked_uuid")

    def test_clearplayer(self):
        # Mocking request object
        mocked_request = MagicMock()
        mocked_request.json.get.return_value = {"Player": "Test Player"}

        # Mocking Players list
        Players = ["Test Player", "Other Player"]

        # Mocking app.logger object
        mocked_app_logger = MagicMock()

        # Setting up the application context
        with (
            patch("Catcher.request", mocked_request),
            patch("Catcher.Players", Players),
            patch("Catcher.app.logger", mocked_app_logger),
        ):

            # Calling the function to be tested
            response = clearplayer()

        # Asserting that the player was removed correctly
        self.assertEqual(response[1], 200)  # response is a tuple, get the first element

    def test_clearplayer_player_found(self):
        # Mocking request object
        mocked_request = MagicMock()
        mocked_request.json.get.return_value = {"Player": "Test Player"}

        # Mocking Players list
        Players = ["Test Player", "Other Player"]

        # Mocking app.logger object
        mocked_app_logger = MagicMock()

        # Setting up the application context
        with (
            patch("Catcher.request", mocked_request),
            patch("Catcher.Players", Players),
            patch("Catcher.app.logger", mocked_app_logger),
        ):

            # Calling the function to be tested
            response = clearplayer()

        # Asserting that the player was found and removed correctly
        self.assertEqual(response[1], 200)  # response is a tuple, get the first element

    def test_clearplayer_player_not_found(self):
        # Mocking request object
        mocked_request = MagicMock()
        mocked_request.json.get.return_value = {"Player": "Nonexistent Player"}

        # Mocking Players list
        Players = ["Test Player", "Other Player"]

        # Mocking app.logger object
        mocked_app_logger = MagicMock()

        # Setting up the application context
        with (
            patch("Catcher.request", mocked_request),
            patch("Catcher.Players", Players),
            patch("Catcher.app.logger", mocked_app_logger),
        ):

            # Calling the function to be tested
            response = clearplayer()

        # Asserting that the player was not found
        self.assertEqual(response[1], 200)  # response is a tuple, get the first element

    def test_sendgrid(self):
        # Mocking open() function
        mocked_open = MagicMock()
        mocked_open.return_value.__enter__.return_value = MagicMock()
        mocked_open.return_value.__enter__.return_value.read.return_value = '{"grid": "test grid"}'

        # Setting up the application context
        with patch("Catcher.open", mocked_open):

            # Calling the function to be tested
            response = sendgrid()

        # Asserting that the correct grid was sent
        self.assertEqual(response.json, {"grid": "test grid"})

    @patch("Catcher.json.load")
    @patch("Catcher.json.dump")
    @patch("Catcher.is_game_over")
    def test_AI_turn(self, mock_is_game_over, mock_json_dump, mock_json_load):
        OBJPlayers = [MagicMock(name="Player1"), MagicMock(name="Player2")]
        global CurrentTurn
        CurrentTurn = "Player1"
        with patch("Catcher.OBJPlayers", OBJPlayers):
            with patch("Catcher.is_game_over", return_value=False) as mock_is_game_over:
                with patch("Catcher.game_over"):
                    self.assertIsNone(AI_turn())
                    mock_json_load.assert_called_once()
                    mock_json_dump.assert_called_once()
                    mock_is_game_over.assert_called_once()

    @patch("Catcher.json.loads")
    @patch("Catcher.json.dump")
    @patch("Catcher.HexGrid")
    @patch("Catcher.Player")
    @patch("Catcher.AI_Player")
    @patch("Catcher.random.choice")
    @patch("Catcher.open")
    def test_gamestart(
        self,
        mock_open,
        mock_random_choice,
        mock_AI_Player,
        mock_Player,
        mock_HexGrid,
        mock_dump,
        mock_loads,
    ):
        # Mocking data
        Players_name = ["Player1", "Player2", "AI"]
        mock_loads.return_value = [["#FFFFFF"], ["#FFFFFF"]]
        mock_HexGrid_instance = MagicMock()
        mock_HexGrid.return_value = mock_HexGrid_instance
        mock_AI_Player_instance = MagicMock()
        mock_AI_Player.return_value = mock_AI_Player_instance
        mock_Player_instance = MagicMock()
        mock_Player.return_value = mock_Player_instance
        mock_random_choice.return_value = "Player1"

        result = gamestart(Players_name)

        mock_HexGrid.assert_called_once()
        mock_HexGrid().json_self.assert_called_once()
        mock_HexGrid().set_walls.assert_called_once_with([(1, 1), (1, 2)])

    @patch("Catcher.json.load")
    @patch("Catcher.open")
    def test_is_game_over(self, mock_open, mock_load):
        # Mocking data
        mock_load.return_value = [
            ["#FFFFFF"],
            ["#FFFFFF"],
            ["#FFFFFF"],
            ["#FFFFFF"],
            ["#FFFFFF"],
            ["#FFFFFF"],
        ]
        global OBJPlayers
        OBJPlayers = [MagicMock(cells=[(0, 0), (1, 1)]), MagicMock(cells=[(0, 1), (1, 0)])]
        global num_walls
        num_walls = 2

        self.assertFalse(is_game_over())

        OBJPlayers[0].cells = [(0, 0), (1, 1), (2, 2)]

        with patch("Catcher.OBJPlayers", OBJPlayers):
            self.assertTrue(is_game_over())

    @patch("Catcher.socketio.emit")
    def test_game_over(self, mock_emit):
        # Mocking data
        global OBJPlayers
        OBJPlayers = [MagicMock(cells=[(0, 0), (1, 1)]), MagicMock(cells=[(0, 1), (1, 0)])]
        with patch("Catcher.OBJPlayers", OBJPlayers):
            with patch("Catcher.socketio.emit") as mock_emit:
                game_over()
                # Assert that the winner is emitted to the client
                mock_emit.assert_called_once_with("GameOver", OBJPlayers[0].name)


class TestAIPlayerMethods(unittest.TestCase):
    def setUp(self):
        # Инициализация тестовых данных, если необходимо
        self.ai_player = AI_Player(
            "AI", "#FF0000", (0, 0), json.loads(HexGrid(3, 3).json_self())
        )  # Создание экземпляра класса для тестирования

    def test_calc_flat_score(self):
        # Подготовка тестовых данных
        grid_json = json.loads(HexGrid(3, 3).json_self())
        Lcells = {(0, 0), (1, 1), (2, 2)}
        color = "#FF0000"

        # Выполнение тестируемого метода
        result = self.ai_player.calc_flat_score(grid_json, Lcells, color)

        # Проверка результата
        self.assertIsInstance(result, float)  # Убедимся, что результат - число с плавающей точкой

    # Здесь можно добавить еще тесты для других методов, если это необходимо

    @patch("Player_AI.AI_Player.ai_choose_color")
    @patch("Player_AI.AI_Player.check_possible_moves")
    @patch("Player_AI.AI_Player.calc_flat_score")
    def test_make_turn(
        self, mock_calc_flat_score, mock_check_possible_moves, mock_ai_choose_color
    ):
        # Подготовка тестовых данных
        grid_json = json.loads(HexGrid(3, 3).json_self())
        expected_move = "#FFFFFF"
        expected_score = 100

        mock_calc_flat_score.return_value = expected_score
        mock_check_possible_moves.return_value = {(0, 0), (1, 1), (2, 2)}
        mock_ai_choose_color.return_value = ([(0, 0), (1, 1), (2, 2)], grid_json)

        # Выполнение тестируемого метода
        result = self.ai_player.make_turn(grid_json)

        # Проверка вызовов методов и возвращаемого результата
        mock_calc_flat_score.assert_called()
        mock_check_possible_moves.assert_called()
        mock_ai_choose_color.assert_called()
        self.assertEqual(result, expected_move)  # Проверка результата

    # Здесь можно добавить еще тесты для других методов, если это необходимо


if __name__ == "__main__":
    # unittest.main()
    # Создайте экземпляр TestLoader для загрузки тестов
    loader = unittest.TestLoader()

    # Создайте TestSuite, содержащий ваши тесты
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestAppRoutes))
    suite.addTests(loader.loadTestsFromTestCase(TestAIPlayerMethods))

    # Определите текущий каталог скрипта
    current_directory = os.path.dirname(os.path.realpath(__file__))

    # Перейдите на один уровень вверх по иерархии каталогов
    parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

    # Составьте абсолютный путь к файлу отчета
    report_path = os.path.join(parent_directory, "tests", "test_report", "test_report.html")

    # Создайте экземпляр HTMLTestRunner и передайте ему файл для записи отчета
    with open(report_path, "w") as report_file:

        runner = HTMLTestRunner(stream=report_file, verbosity=2)

        # Запустите тесты и сгенерируйте отчет
        result = runner.run(suite)

    # Опционально, выведите результаты тестирования в консоль
    print(result)
