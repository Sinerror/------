@echo off

rem Запрос пути к закрытому ключу
set /p private_key="Path to root.key (For example, C:\path\to\key.pem): "

rem Проверка наличия указанного файла
if not exist "%private_key%" (
    echo Файл ключа не найден: %private_key%
    exit /b
)

rem Считываем список файлов из файла file_list.txt
for /f "usebackq delims=" %%F in ("file_list.txt") do (
    echo sing file: %%F
    openssl dgst -sha256 -sign "%private_key%" -out ".\signatures\%%~nF.signature" "%%F"
    echo Done.
)

pause