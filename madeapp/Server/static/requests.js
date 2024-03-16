/**
 * This function sends the selected color to the server via a POST request
 * to update the game state.
 * <br>Comlexity is: O(1) - Send Message to the server
 * @brief Sends the selected color to the server.
 *
 * @param {str} url The URL of the server to send the color data.
 * @param {str} color The color selected by the player.
 * @param {str} PlayerName The name of the player sending the color.
 * @return void
 */

function sendColor (url, color, PlayerName) {
  // Создаем новый объект XMLHttpRequest
  const xhr = new XMLHttpRequest()

  // Определяем обработчик события загрузки
  xhr.onload = function () {
    // Проверяем, был ли запрос успешным (код 200)
    if (xhr.status === 200) {
      // Получаем ответ от сервера
      console.log('Отправка цветов на сервер успешна')
    } else {
      // Если запрос не успешен, выводим сообщение об ошибке
      console.error('Ошибка при отправке запроса: ' + xhr.status)
    }
  }

  // Формируем запрос POST на URL сервера для обновления игрового состояния
  xhr.open('POST', url + '/turn', true)

  // Устанавливаем заголовок Content-Type для указания типа передаваемых данных (JSON)
  xhr.setRequestHeader('Content-Type', 'application/json')

  // Преобразуем данные (выбранный цвет) в формат JSON и отправляем на сервер
  xhr.send(JSON.stringify({ Player: PlayerName, Color: color }))
}
// let Plname = "bob"
// let url = "http://127.0.0.1:5000"

/**
* This function asynchronously sends a GET request to the server to
* retrieve the color grid data. It returns a promise that resolves with
* the received color grid data.
* <br>Comlexity is: O(1) - Send Message to the server and waiting for response
* @brief Asynchronously requests the color grid data from the server.
*
* @param {str} url The URL of the server to request the color grid data.
* @return Promise that resolves with the color grid data.
*/

async function colorask (url) {
  return new Promise((resolve, reject) => {
    // Создаем новый объект XMLHttpRequest
    const xhr = new XMLHttpRequest()

    // Определяем обработчик события загрузки
    xhr.onload = function () {
      // Проверяем, был ли запрос успешным (код 200)
      if (xhr.status === 200) {
        // Получаем ответ от сервера
        const colors = []

        const data = JSON.parse(xhr.responseText)

        for (let i = 0; i < data.length; i++) {
          colors[i] = []
          for (let j = 0; j < data[i].length; j++) {
            colors[i][j] = data[i][j].color
          }
        }
        resolve(colors) // Резолвим промис с полученными данными
      } else {
        // Если запрос не успешен, выводим сообщение об ошибке
        const error = 'Ошибка при отправке запроса: ' + xhr.status
        reject(error)
      }
    }

    // Формируем запрос GET на URL сервера для получения данных
    xhr.open('GET', url + '/send_grid', true)

    xhr.setRequestHeader('Content-Type', 'application/json')

    // Отправляем запрос на сервер
    xhr.send({ success: true })
  })
}

/**
 * This function parses the query parameters from a given query string and returns
 * an object containing key-value pairs representing the parameters.
 * <br>Comlexity is: O(1) - Simple output
 * 
 * @brief Parses the query parameters from a query to string.
 *
 * @param {str} queryString The query string to parse.
 * @return Object An object containing key-value pairs representing the parsed query parameters.
 */

function parseQueryParams (queryString) {
  const queryParams = {}
  // Удаляем знак вопроса из строки параметров запроса, если он присутствует
  if (queryString.charAt(0) === '?') {
    queryString = queryString.substring(1)
  }
  // Разбиваем строку на части по символу "&", который разделяет пары ключ-значение
  const pairs = queryString.split('&')
  // Обрабатываем каждую пару
  pairs.forEach(function (pair) {
    const keyValue = pair.split('=')
    const key = decodeURIComponent(keyValue[0]) // декодируем ключ
    const value = decodeURIComponent(keyValue[1]) // декодируем значение
    // Если ключ уже существует, превращаем его в массив для хранения нескольких значений
    if (queryParams[key]) {
      if (!Array.isArray(queryParams[key])) {
        queryParams[key] = [queryParams[key]]
      }
      queryParams[key].push(value)
    } else {
      queryParams[key] = value
    }
  })
  return queryParams
}
