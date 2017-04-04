import BaseHTTPServer
from optparse import OptionParser

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        request_path = self.path
        print(request_path)
        
    def do_POST(self):   
        request_path = self.path
        print(request_path)

    
    do_PUT = do_POST
    do_DELETE = do_GET

def wait_for_request(server_class=BaseHTTPServer.HTTPServer, handler_class=RequestHandler, path='/callback/'):
	server_address = ('', 8888)
	httpd = server_class(server_address, handler_class)
	httpd.handle_request()

wait_for_request()