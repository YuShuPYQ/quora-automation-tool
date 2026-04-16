@echo off
chcp 65001 >nul
set "TCL_LIBRARY=C:\Users\yushu\Desktop\quora发帖\.conda\Library\lib\tcl8.6"
set "TK_LIBRARY=C:\Users\yushu\Desktop\quora发帖\.conda\Library\lib\tk8.6"
set "PATH=C:\Users\yushu\Desktop\quora发帖\.conda\Library\bin;%PATH%"
"C:\Users\yushu\Desktop\quora发帖\.conda\python.exe" "C:\Users\yushu\Desktop\quora发帖\gui_app.py"
pause
