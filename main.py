from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os

hostname = 'localhost'
port = 8080

current = ''

commands = {
    'spotify': {
        'start': lambda: 'systemctl start raspotify',
        'stop': lambda: 'systemctl stop raspotify'
    },
    'radio': {
        'start': lambda addr: f'mplayer {addr} &',
        'stop': lambda: 'killall mplayer'
    }
}

def RunService(service, **args):
    global current

    if current != '':
        os.system(commands[service]['stop']())

    if service in commands:
        os.system(commands[service]['start'](**args))
        current = service

class HttpServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global current

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(open('index.html', 'r').read().encode('utf-8'))

        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path.startswith('/radio?'):
            RunService('radio', self.path[7:])

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path == '/spotify':
            RunService('spotify')

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

if __name__ == '__main__':
    RunService('spotify')

    web_server = HTTPServer((hostname, port), HttpServer)
    print('Server started http://%s:%s' % (hostname, port))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print('Server stopped.')
