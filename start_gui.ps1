# 获取当前脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置环境变量
$env:TCL_LIBRARY = Join-Path $scriptDir ".conda\Library\lib\tcl8.6"
$env:TK_LIBRARY = Join-Path $scriptDir ".conda\Library\lib\tk8.6"
$env:PATH = (Join-Path $scriptDir ".conda\Library\bin") + ";$env:PATH"

# 启动 GUI
$pythonPath = Join-Path $scriptDir ".conda\python.exe"
$guiPath = Join-Path $scriptDir "gui_app.py"
& $pythonPath $guiPath
