@echo off
chcp 65001 >nul
java -Dfile.encoding=UTF-8 -Dsun.stdout.encoding=UTF-8 -Dsun.stderr.encoding=UTF-8 -jar "D:\Codes\atkhttp\target\atk_python_sdk_service.jar"
pause
