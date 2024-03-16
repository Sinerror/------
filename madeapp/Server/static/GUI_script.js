/**
 * This function emit a message to server via web socket
 * <br>Comlexity is: O(1) - simple output
 * @brief This function emit a message
 *
 * @param {str} message message to be emited.
 * @return void
 */

function sendMessage (message) {
  socket.send(message)
}

/**
 * This function draws a single hexagon on the canvas at the specified coordinates with the given color and border color.
 * <br>Comlexity is: O(1) - cycle does not depend on the input
 * @brief Draws a single hexagon on the canvas.
 *
 * @param {number} x The x-coordinate of the center of the hexagon.
 * @param {number} y The y-coordinate of the center of the hexagon.
 * @param {str} color The fill color of the hexagon.
 * @param {str} borderColor The color of the hexagon's border.
 * @return void
 */

// Функция для рисования гексагона
function drawHex (x, y, color, borderColor) {
  ctx.beginPath()
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i // Изменяем угол на 30 градусов (Math.PI / 6)
    const x_i = x + hexSize * Math.cos(angle)
    const y_i = y + hexSize * Math.sin(angle)
    ctx.lineTo(x_i, y_i)
  }
  ctx.closePath()
  ctx.fillStyle = color
  ctx.fill()

  ctx.strokeStyle = borderColor
  ctx.stroke()
}

/**
 * This function draws a group of hexagons on the canvas with the specified border color.
 * <br>Comlexity is: O(n) - Cycle hexagons.forEach(hexagon =>... have complexity of O(n)
 * @brief Draws a group of hexagons on the canvas.
 *
 * @param {array} hexagons An array of objects representing the hexagons to draw.
 * @param {str} borderColor The color of the hexagons' borders.
 * @return void
 */

// Обвести группу гексагонов
function drawHexGroup (hexagons, borderColor) {
  ctx.strokeStyle = borderColor
  ctx.lineWidth = 2 // Ширина обводки

  hexagons.forEach(hexagon => {
    ctx.beginPath()
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i
      const x_i = hexagon.x + hexSize * Math.cos(angle)
      const y_i = hexagon.y + hexSize * Math.sin(angle)
      if (i === 0) {
        ctx.moveTo(x_i, y_i)
      } else {
        ctx.lineTo(x_i, y_i)
      }
    }
    ctx.closePath()
    ctx.stroke()
  })
}

/**
 *
 * This function draws the entire hexagon field on the canvas using the colors retrieved from the server.
 * <br>Comlexity is: O(n1*n2) - cycles for (let i = 0; i < numRows; i++) and for (let j = 0; j < numCols; j++) have O(n1) and O(n2) respectively
 * @brief Draws the hexagon field on the canvas.
 *
 * @return void
 */

// Функция для рисования всего поля
function drawHexagonField () {
  if (colors[0] == undefined) {
    showError('Не удалось получить цвета с сервера')
    return 0
  }

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  for (let i = 0; i < numRows; i++) {
    for (let j = 0; j < numCols; j++) {
      const x = (j) * (hexSize * 1.5) - cameraX
      const y = (i) * (hexSize * Math.sqrt(3)) + ((j % 2) * hexSize * Math.sqrt(3) / 2) - cameraY
      drawHex(x, y, colors[i][j], 'rgba(0, 0, 0, 0.2)')
    }
  }
}

/**
 * This function calculates the width and height of the hexagon field based on the number of columns, rows,
 * and the size of each hexagon.
 * <br>Comlexity is: O(1) - Simple calculations and output
 *
 * @brief Calculates the size of the hexagon field.
 *
 * @return Object An object containing the width and height of the hexagon field.
 */
function calculateFieldSize () {
  const fieldWidth = numCols * hexSize * 1.5 // Ширина поля
  let fieldHeight = numRows * hexSize // Высота поля

  // Учитываем дополнительный отступ по Y для нечётных строк
  if (numCols % 2 === 1) {
    fieldHeight += (numRows - 1) * (hexSize * Math.sqrt(3) / 2)
  } else {
    fieldHeight += numRows * (hexSize * Math.sqrt(3) / 2)
  }

  return { width: fieldWidth, height: fieldHeight }
}

/**
 *
 * This function adjusts the camera position based on the mouse movement to allow panning across the canvas.
 * <br>Comlexity is: O(1) - Simple reaction onto the event
 * 
 * @brief Handles the mouse move event.
 * @param {Object} event The mouse move event.
 * @return void
 */
function onMouseMove (event) {
  if (colors[0] == undefined) {
    return 0
  }

  const rect = canvas.getBoundingClientRect()
  const mouseX = event.clientX - rect.left
  const mouseY = event.clientY - rect.top

  if (mouseX < window.innerWidth * 0.14 && cameraX >= -window.innerWidth * 0.01) { // Если курсор мыши приблизился к левому краю Canvas
    cameraX -= window.innerWidth * 0.01
  } else if (mouseX > window.innerWidth - window.innerWidth * 0.14 && cameraX <= calculateFieldSize().width - window.innerWidth) { // Если курсор мыши приблизился к правому краю Canvas
    cameraX += window.innerWidth * 0.01
  }

  if (mouseY < window.innerHeight * 0.14 && cameraY >= -window.innerHeight * 0.01) { // Если курсор мыши приблизился к верхнему краю Canvas
    cameraY -= window.innerHeight * 0.01
  } else if (mouseY > window.innerHeight - window.innerHeight * 0.14 && cameraY <= calculateFieldSize().height - window.innerHeight) { // Если курсор мыши приблизился к нижнему краю Canvas
    cameraY += window.innerHeight * 0.01
  }

  drawHexagonField()
}

// Получить с сервера полную информацию о пользователе
/* function set_playerdata(){

} */

/**

 * This function emits a 'get_turn' event to the server using the socket connection
 * to request the current turn. Upon receiving the turn from the server, it updates
 * the overlay element with the current turn information.
 * <br>Comlexity is: O(1) - Simple Output
 * 
 * @brief Requests and displays the current turn from the server.
 *
 * @return void
 */

function refreshTurn () {
  socket.emit('get_turn')
  socket.on('turn', function (message) {
    const turn_pl = document.getElementById('overlay')
    const turn_text = document.getElementById('turn_text')
    turn_text.textContent = 'Сейчас ход: ' + message
  })
}
