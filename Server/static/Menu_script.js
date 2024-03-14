/**
 * This function retrieves the player name from the input field, sends it to the server along with information
 * about whether the player wants to play against an AI opponent, and starts waiting for the game to start.
 * It sets up an interval to repeatedly send requests to the server to check if the game has started.
 * 
 * <br>Comlexity is: O(1) - Simple manipulations
 * 
 * @brief Initiates the game by sending player information to the server and waiting for the game to start.
 *
 * @return void
 */

function startGame () {
  const playerName = document.getElementById('playerName').value
  document.getElementById('players').innerText = 'Current players 1/2... - waiting'
  // Переход на другую страницу при ответе сервера
  counter = 400 // Интервал сброса на 200 секунд
  intervalId = setInterval(() => send_and_wait(playerName), 500) // Каждые 0.5 секунд
}

/**
 * This function sends the player's information, including their name and whether they want to play against
 * an AI opponent, to the server. It then waits for the server's response to start the game.
 * <br>Comlexity is: O(1) - Send message to the server and wait (counter/2 seconds)
 * 
 * @brief Sends player information to the server and waits for the game to start.
 *
 * @param {str} playerName The name of the player.
 * @return void
 */
// Отправить информацио о игроке на сервер и ждать игры (также отправить на сервер информацию - хочет ли игрок играть с Компьютерным противником)
function send_and_wait (playerName) {
  if (counter < 1) {
    clearInterval(intervalId)
    document.getElementById('players').innerText = 'Превышено время ожидания - перезагрузите страницу'
    return
  };

  // Создаем новый объект XMLHttpRequest
  const xhr = new XMLHttpRequest()

  // Определяем обработчик события загрузки
  xhr.onload = function () {
    // Проверяем, был ли запрос успешным (код 200)
    if (xhr.status === 200) {
      // Получаем ответ от сервера
      const updatedState = JSON.parse(xhr.responseText)

      // Если получен ответ, останавливаем интервал
      if (updatedState.Gamestarted) {
        clearInterval(intervalId)
        window.location.href = url + '/game' + '?name=' + playerName
      }
    } else {
      // Если запрос не успешен, выводим сообщение об ошибке
      console.error('Ошибка при отправке запроса: ' + xhr.status)
      document.getElementById('players').innerText = 'Что-то пошло не так - перезагрузите страницу'
      clearInterval(intervalId)
      counter -= 1
    }
  }

  // Формируем запрос POST на URL сервера для обновления игрового состояния
  xhr.open('POST', url + '/wait_room', true)

  // Устанавливаем заголовок Content-Type для указания типа передаваемых данных (JSON)
  xhr.setRequestHeader('Content-Type', 'application/json')

  // Преобразуем данные (выбранный цвет) в формат JSON и отправляем на сервер
  xhr.send(JSON.stringify({ Player: playerName, Use_AI: document.getElementById('myCheckbox').checked }))
}

/**
 * This function redirects the player to the game page after the game has started.
 * <br>Comlexity is: O(1) - Send message to the server
 * @brief Redirects the player to the game page after the game has started.
 *
 * @param {str} Playername The name of the player.
 * @param {str} url The URL of the server.
 * @return void
 */
// Когда получен ответ от сервера обработать начало игры
function gamestart (Playername, url) {
  // Создаем новый объект XMLHttpRequest
  const xhr = new XMLHttpRequest()

  // Определяем обработчик события загрузки
  xhr.onload = function () {
    // Проверяем, был ли запрос успешным (код 200)
    if (xhr.status === 200) {
      // Получаем ответ от сервера
      const game = JSON.parse(xhr.responseText)

      // Обновляем игровое поле на основе полученных данных
      window.location.href = game
    } else {
      // Если запрос не успешен, выводим сообщение об ошибке
      console.error('Ошибка при отправке запроса: ' + xhr.status)
    }
  }

  // Формируем запрос POST на URL сервера для обновления игрового состояния
  xhr.open('POST', url + '/starting_game', true)

  // Устанавливаем заголовок Content-Type для указания типа передаваемых данных (JSON)
  xhr.setRequestHeader('Content-Type', 'application/json')

  // Преобразуем данные (выбранный цвет) в формат JSON и отправляем на сервер
  xhr.send(JSON.stringify({ Pname: Playername }))
}
