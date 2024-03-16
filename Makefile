PYTHON_SCRIPTS_DIR := Server
STATIC_DIR := $(PYTHON_SCRIPTS_DIR)\\static
TEMPLATES_DIR := $(PYTHON_SCRIPTS_DIR)\\templates
MADE_APP_DIR := madeapp\\Server
MADE_APP_STATIC_DIR := $(MADE_APP_DIR)\\static
MADE_APP_TEMPLATES_DIR := $(MADE_APP_DIR)\\templates

# Копирование HTML файлов
copy_html:
	xcopy $(TEMPLATES_DIR)\\docs.html $(MADE_APP_TEMPLATES_DIR)\\ /y
	xcopy $(TEMPLATES_DIR)\\GUI.html $(MADE_APP_TEMPLATES_DIR)\\ /y
	xcopy $(TEMPLATES_DIR)\\Menu.html $(MADE_APP_TEMPLATES_DIR)\\ /y
# Копирование CSS файлов
copy_css:
	xcopy $(STATIC_DIR)\\GUI.css $(MADE_APP_STATIC_DIR)\\ /y
# Компиляция и минификация JavaScript файлов
js_bundle:
	xcopy $(STATIC_DIR)\\*.js $(MADE_APP_STATIC_DIR)\\ /y 
# Компиляция и сборка всех Python файлов
python_compile:
	if not exist "$(MADE_APP_DIR)" mkdir $(MADE_APP_DIR)
	python3 -m compileall -b -d $(MADE_APP_DIR) $(PYTHON_SCRIPTS_DIR)
	xcopy $(PYTHON_SCRIPTS_DIR)\\*.py $(MADE_APP_DIR)\\ /y 
	xcopy $(PYTHON_SCRIPTS_DIR)\\*.pyc $(MADE_APP_DIR)\\ /y
	del $(PYTHON_SCRIPTS_DIR)\\*.pyc

sign:
	xcopy $(PYTHON_SCRIPTS_DIR)\\file_list.txt $(MADE_APP_DIR)\\ /y
	xcopy $(PYTHON_SCRIPTS_DIR)\\sig.bat $(MADE_APP_DIR)\\ /y
	if not exist "$(MADE_APP_DIR)\\signatures" mkdir $(MADE_APP_DIR)\\signatures
	echo $(PYTHON_SCRIPTS_DIR)\\app.key || $(MADE_APP_DIR)\\sig.bat
	del $(MADE_APP_DIR)\\sig.bat
	openssl pkey -pubout -in $(PYTHON_SCRIPTS_DIR)\\app.key -out $(MADE_APP_DIR)\\app.pub
	openssl genpkey -algorithm RSA -out $(MADE_APP_DIR)\\user.key
	openssl pkey -pubout -in $(MADE_APP_DIR)\\user.key -out $(MADE_APP_DIR)\\user.pub
	openssl dgst -sha256 -sign $(PYTHON_SCRIPTS_DIR)\\app.key -out $(MADE_APP_DIR)\\user.sig $(MADE_APP_DIR)\\user.key

# Основной целью по умолчанию является сборка всех файлов
all: python_compile js_bundle copy_html copy_css sign