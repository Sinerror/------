# Компиляция и сборка всех Python файлов
python_compile:
	python3 -m compileall -b -d ../Made_app Server
# Компиляция и минификация JavaScript файлов
js_bundle:
	glifyjs Server/static/GUI_script.js Server/static/Menu_script.js Server/static/popups.js Server/static/requests.js -o Made_app/bundle.min.js
# Копирование HTML файлов
copy_html:
	cp Server/templates/docs.html Made_app/docs.html
	cp Server/templates/GUI.html Made_app/GUI.html
	cp Server/templates/Menu.html Made_app/Menu.html
# Копирование CSS файлов
copy_css:
	cp Server/static/GUI.css Made_app/bundle.css
# Основной целью по умолчанию является сборка всех файлов
all: python_compile js_bundle copy_html copy_css