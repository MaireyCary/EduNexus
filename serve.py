import os
import sys
import socket
import time
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer


class SpaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 处理打包后的资源路径
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        dist_path = os.path.join(base_dir, 'dist')
        super().__init__(*args, directory=dist_path, **kwargs)

    def do_GET(self):
        # 处理静态资源请求
        if self.path.startswith('/static/') or self.path in [
            '/favicon.ico',
            '/logo.svg',
            '/platform-config.json'
        ]:
            return super().do_GET()
        
        # SPA路由回退到index.html
        self.path = '/index.html'
        return super().do_GET()


def start_serve():
    port = 8000
    ip_address = socket.gethostbyname(socket.gethostname())

    print("="*50)
    print(f"EduNexus前端服务已启动:")
    print(f"访问地址: http://{ip_address}:{port}")
    print("="*50)
    print("按 Ctrl+C 停止服务")

    httpd = TCPServer(("0.0.0.0", port), SpaHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    # 添加主循环保持程序运行
    try:
        start_serve()
    except Exception as e:
        print(f"服务异常终止: {str(e)}")
        print("5秒后尝试重启...")
        time.sleep(5)
