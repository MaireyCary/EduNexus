import socket
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer


class SpaHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="dist", **kwargs)

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

    with TCPServer(("0.0.0.0", port), SpaHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止")


if __name__ == "__main__":
    start_serve()
