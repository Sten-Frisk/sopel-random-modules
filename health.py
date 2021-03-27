#!/usr/bin/env python3
# Bot health check service

from http.server import BaseHTTPRequestHandler, HTTPServer
from sopel import module, config
import multiprocessing
import os

irc_connection = True

@module.event('PART', 'QUIT', 'KICK')
def set_variable(bot, trigger):
    global irc_connection
    
    irc_connection = False

@module.event('JOIN')
def reset_variable(bot, trigger):
    global irc_connection
    
    settings = config.Config(f"/{os.environ['HOME']}/.sopel/default.cfg", validate=False)
    joined_channels = [str(channel).lower() for channel in bot.channels]
    settings_channels = [channel.lower() for channel in settings.core.channels]
    if sorted(joined_channels) == sorted(settings_channels):
        irc_connection = True
    else:
        irc_connection = False

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        global irc_connection

        if irc_connection:
            self.send_response(200)
        else:
            self.send_response(503)

        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("health {}".format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    

th = multiprocessing.Process(target=run)

def setup(bot):
    th.start()

def shutdown(bot):
    th.terminate()
