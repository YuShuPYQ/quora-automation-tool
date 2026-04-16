@echo off
REM 启动第一个 Chrome 实例 (端口 9222)
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeProfiles\Profile1" --disable-features=ChromeSignInUI,TranslateUI,Translate,ChromeBrowserSync --password-store=basic --no-first-run --no-default-browser-check --start-maximized --disable-profile-picker --no-new-window --disable-sync --disable-infobars --disable-notifications
echo Launched Chrome on port 9222

REM 启动第二个 Chrome 实例 (端口 9223)
REM start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9223 --user-data-dir="C:\ChromeProfiles\Profile2" --disable-features=ChromeSignInUI,TranslateUI,Translate,ChromeBrowserSync --password-store=basic --no-first-run --no-default-browser-check --start-maximized --disable-profile-picker --no-new-window --disable-sync --disable-infobars --disable-notifications
REM echo Launched Chrome on port 9223

REM以此类推，您可以取消注释或添加更多实例
pause
