from google_login import login_google_account
import time

# 测试谷歌账号登录
def test_google_login():
    google_account = "ToanChao26Febu157@samboachieshs.com"
    google_pwd = "Voq04168"
    
    print("开始测试谷歌账号登录...")
    try:
        browser = login_google_account(google_account, google_pwd)
        
        if browser:
            print("✅ 谷歌账号登录成功！")
            # 保持浏览器打开一段时间
            print("浏览器将在5秒后关闭...")
            time.sleep(5)
            browser.close()
        else:
            print("❌ 谷歌账号登录失败！")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_google_login()
