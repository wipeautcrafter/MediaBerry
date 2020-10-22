from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import subprocess
import time
import os

hostname = 'localhost'
port = 80

current = None

commands = {
    'spotify': {
        'start': lambda: 'systemctl start raspotify',
        'stop': lambda: 'systemctl stop raspotify'
    },
    'radio': {
        'start': lambda addr: f'mplayer {addr} -cache 1024 -cache-min 30 &',
        'stop': lambda: 'killall mplayer'
    }
}

def RunService(service, *args):
    global current

    if not current is None:
        os.system(commands[current]['stop']())

    if service in commands:
        current = service
        os.system(commands[current]['start'](*args))

class HttpServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global current

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(open('index.html', 'r').read().encode('utf-8'))

        if self.path == '/status':
            vol_out = subprocess.check_output('amixer sget Headphone', shell=True)
            vol_line = str(vol_out.splitlines()[4])
            volume = vol_line[vol_line.index('[')+1:vol_line.index('%')]

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(('{"volume":%s,"current":"%s"}' % (volume, current)).encode('utf-8'))

        if self.path.startswith('/volume?'):
            os.system("amixer sset Headphone " + self.path[8:] + "%")

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        if self.path.startswith('/radio?'):
            RunService('radio', unquote(self.path[7:]))

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

    web_server = HTTPServer(('', port), HttpServer)
    print('Server started http://%s:%s' % (hostname, port))

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print('Server stopped.')
