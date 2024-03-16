/**

 * This function creates a toast element to display an error message
 * on the webpage. The toast message automatically disappears after
 * a certain period.
 * <br>Comlexity is: O(1) - Simple output
 * @brief Display an error message as a toast.
 *
 * @param {str} message The error message to be displayed.
 * @return void
 */

// Функция сообщения об ошибке
function showError (message) {
  // Создаем элемент сообщения
  const toast = document.createElement('div')
  toast.classList.add('toast-error')
  toast.textContent = message

  // Добавляем его на страницу
  document.body.appendChild(toast)

  setTimeout(function () {
    toast.classList.add('hide')
  }, 4000) // 4000 миллисекунд (Анимация изчезовения запустится через 4 секунды)

  // Автоматически скрываем сообщение через некоторое время
  setTimeout(function () {
    toast.remove()
  }, 5000) // 5000 миллисекунд (Сообщение пропадёт через 5 секунд)
}

/**

 * This function creates a popup message element to display a message
 * on the webpage. The message automatically disappears after a certain
 * period. Optionally, it can be displayed over an overlay.
 * <br>Comlexity is: O(1) - Simple output
 * @brief Display a popup message on the webpage.
 *
 * @param {str} message The message to be displayed.
 * @param {str} style The style of the popup message (defaults to 'toast').
 * @param {bool} q_overlay Whether to display the message over an overlay (defaults to false).
 * @return void
 */

// styles = 'toast-big', 'toast', 'toast-small'
function showPopup (message, style = 'toast', q_overlay = false) {
  const overlay = document.getElementById('overlay')
  const toast = document.createElement('div')
  toast.classList.add(style)
  toast.textContent = message

  // Добавляем его на страницу

  if (q_overlay) {
    overlay.appendChild(toast)
    overlay.style.display = 'flex'
  } else {
    document.body.appendChild(toast)
  }

  setTimeout(function () {
    toast.classList.add('hide')
  }, 2000) // 4000 миллисекунд (Анимация изчезовения запустится через 4 секунды)

  // Автоматически скрываем сообщение через некоторое время
  setTimeout(function () {
    toast.remove()
    document.getElementById('overlay').style.display = 'none'
  }, 3000) // 5000 миллисекунд (Сообщение пропадёт через 5 секунд)
}

// Изменить прогрессбар
/* function setProgress(className, percent) {
    const progressBars = document.querySelectorAll("." + className);
    progressBars.forEach(function(bar) {
        bar.style.height = percent + "%";
    });
} */
