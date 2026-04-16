
import sys
import argparse
from google_login import login_google_account

def main():
    parser = argparse.ArgumentParser(description='Google Login Worker')
    parser.add_argument('--port', required=True, type=int)
    parser.add_argument('--account', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--default-website')
    parser.add_argument('--enable-nav', action='store_true')
    parser.add_argument('--exit-on-pw-submit', action='store_true', help='Exit immediately after password submission.')
    args = parser.parse_args()

    # 使用 print 作为简单的日志记录器
    def worker_logger(msg):
        print(f"WORKER: {msg}", flush=True)

    worker_logger(f"接收到登录任务，端口: {args.port}, 账号: {args.account}")
    worker_logger(f"预设网站: {args.default_website}")
    worker_logger(f"是否启用导航: {args.enable_nav}")
    worker_logger(f"是否提交后立即退出: {args.exit_on_pw_submit}")

    try:
        browser = login_google_account(
            google_account=args.account,
            google_pwd=args.password,
            logger=worker_logger,
            port=args.port,
            default_website=args.default_website,
            enable_website_navigation=args.enable_nav,
            exit_on_pw_submit=args.exit_on_pw_submit
        )
        if browser:
            sys.exit(0) # 成功退出
        else:
            sys.exit(1) # 失败退出
    except Exception as e:
        worker_logger(f"登录时发生未捕获的异常: {e}")
        sys.exit(1) # 失败退出

if __name__ == '__main__':
    main()
