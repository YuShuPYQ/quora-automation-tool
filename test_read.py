with open('gui_app.py', 'rb') as f:
    content = f.read()
try:
    text = content.decode('utf-8')
    print('文件读取成功')
except Exception as e:
    print(f'读取失败：{e}')
