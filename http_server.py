#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os

class StaticServer(BaseHTTPRequestHandler):

    def do_GET(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
        parsed_url = urllib.parse.urlparse(self.path)

        if parsed_url.path == '/':
            filename = root + '/templates/index.html'
        else:
            filename = root + self.path

        self.send_response(200)
        if filename[-4:] == '.css':
            self.send_header('Content-type', 'text/css')
        elif filename[-5:] == '.json':
            self.send_header('Content-type', 'application/javascript')
        elif filename[-3:] == '.js':
            self.send_header('Content-type', 'application/javascript')
        elif filename[-4:] == '.ico':
            self.send_header('Content-type', 'image/x-icon')
        else:
            self.send_header('Content-type', 'text/html')
        self.end_headers()

        try:
            with open(filename, 'rb') as fh:
                html = fh.read()
                self.wfile.write(html)
        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")
        except Exception as e:  # Handle other exceptions
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>500 Internal Server Error</h1>")


    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>POST request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_PUT(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>PUT request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_DELETE(self):    
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>DELETE request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_PATCH(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>PATCH request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>OPTIONS request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>HEAD request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_CONNECT(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>CONNECT request received</h1>")
        self.wfile.flush()
        self.wfile.close()
    def do_TRACE(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>TRACE request received</h1>")
        self.wfile.flush()
        self.wfile.close()
        

def run(server_class=HTTPServer, handler_class=StaticServer, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Server is running on http://localhost:{}'.format(port))
    httpd.serve_forever()

run()