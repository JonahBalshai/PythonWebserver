import urllib.parse
import cgi
import json
import time
#TODO: Maybe do cookies later with  http.cookie? look into this lib
import http.cookies
from routes.router import Router
from http.server import BaseHTTPRequestHandler
from response.requestHandlerGET import RequestHandlerGET
from response.requestHandlerPOST import RequestHandlerPOST
from response.requestHandlerCONTENT import RequestHandlerCONTENT

switch = {
    403: "403 Forbidden",
    404: "404 Not Found"
}

class Server(BaseHTTPRequestHandler):
    # Methode for header data
    def do_HEAD(self):
        return

    def do_GET(self):
        # Check if user is in a session
        username = self.authenticate(self.headers['Cookie'])
        # Create router object and check requested file in combination with username
        router = Router()
        file_path = router.buildPath(self.path, username)
        router_response = router.checkPath(file_path, username)
        
        # Get file and check router response
        if self.path.startswith('/content'):
            handler = RequestHandlerCONTENT()

            if router_response == 200:
                # Iterate throught yielded file chunks
                for chunk_index in handler.find(file_path):
                    # Check if EOF reached
                    if not handler.contents:
                        break
                    else:
                        # Get content and write into file stream
                        self.handle_CONTENT(handler, username, chunk_index)
            else:
                handler.setStatus(router_response)

                # Get content and write into file stream
                self.handle_GET(handler, username)  
        else:
            handler = RequestHandlerGET()
            if router_response == 200:
                handler.find(file_path)
            else:
                handler.setStatus(router_response)

            # Get content and write into file stream
            self.handle_GET(handler, username)

    # POST-Method
    def do_POST(self):
        # Check if user is in a session
        username = self.authenticate(self.headers['Cookie'])
        # Find out content length
        content_length = int(self.headers['Content-Length'])
        # Find out content type
        content_type, pdict = cgi.parse_header(self.headers['Content-Type'])
        # 'Bytefy' pdict[boundary]
        if pdict.get('boundary'):
            pdict['boundary'] = bytes(pdict.get('boundary'), 'utf-8')
        # Find out content encoding
        content_encoding = self.headers['Content-Encoding']
        # Parse content based on content type
        if content_type == 'multipart/form-data': 
            post_content = cgi.parse_multipart(self.rfile, pdict)
            for key in post_content.keys():
                if(hasattr(key, 'decode')):
                    post_content[key][0] = post_content[key][0].decode(content_encoding)
        elif content_type == 'application/x-www-form-urlencoded':
            post_content = urllib.parse.parse_qs(self.rfile.read(content_length).decode(content_encoding), keep_blank_values=True)
        elif content_type == 'application/json':
            post_content = json.loads(self.rfile.read(content_length))
        else:
            post_content = None
        
        # Append username to post_content
        post_content['username'] = username
        # Execute correct action
        handler = RequestHandlerPOST()
        handler.assignAction(post_content)

        # Get content and write into file
        self.handle_POST(handler)

    # GET-handler
    def handle_GET(self, handler, username):
        # Get status code
        status_code = handler.getStatus()

        # Send status code
        self.send_response(status_code)

        # Send content type
        self.send_header('Content-type', handler.getContentType())

        # Send username
        self.send_header('Username', username)

        # End headers
        self.end_headers()

        # Check status code
        if status_code == 200:
            # Send content type and get content
            content = handler.getContents()
        else:
            # Send failure status code
            content = self.get_code_content(status_code)

        # Check if content in bytes / a bytearray
        if isinstance(content, (bytes, bytearray)):
            self.wfile.write(content)
            return

        self.wfile.write(bytes(content, "UTF-8"))

    # Content-File handler
    def handle_CONTENT(self, handler, username, chunk_index):
        # Check if first index in which case headers must be sent first
        if chunk_index == 1:
            # Get status code
            status_code = handler.getStatus()

            # Send status code
            self.send_response(status_code)

            # Send content type to signal automatic browser download
            self.send_header('Content-Type', 'application/octet-stream')

            # Send username
            self.send_header('Username', username)

            # End headers
            self.end_headers()
        
        # Check for str becaus of unreadable type
        if hasattr(handler.contents, 'read'):
            content = handler.getContents()
        else:
            content = handler.contents

        # Check if content in bytes / a bytearray
        if isinstance(content, (bytes, bytearray)):
            self.wfile.write(content)
            return

        self.wfile.write(bytes(content, "UTF-8"))

    # POST-handler
    def handle_POST(self, handler):
        # Get status code
        status_code = handler.getStatus()

        # Send status code
        self.send_response(status_code)

        # Send content type
        self.send_header('Content-type', handler.getContentType())

        #TODO: unhappy that you always have to check maybe theres a way to only do that when you just logged in
        # Send session_token after a login
        if handler.session_token != "":
            self.send_header('Set-cookie', 'sid=' + handler.session_token)

        # End headers
        self.end_headers()

        # Check for str becaus of unreadable type
        if hasattr(handler.contents, 'read'):
            content = handler.getContents()
        else:
            content = handler.contents

        # Check if content in bytes / a bytearray
        if isinstance(content, (bytes, bytearray)):
            self.wfile.write(content)
            return

        self.wfile.write(bytes(content, "UTF-8"))

    # Authenticate the user by returning a username if in valid session otherwise return empty string
    def authenticate(self, cookies):
        # Check if the user has any cookies
        if cookies != None:
            # Convert the cookies into dictionary
            cookies = dict(subString.split("=", 1) for subString in str(cookies).replace(" ", "").split(";"))
            # Get the sid
            sid = cookies['sid']
            # Load database
            with open('./data/users.json') as users_database:
                users = json.loads(users_database.read())
            users_list = users['users']

            for user in users_list:
                # TODO: the time limit doesnt work properly yet check this
                # Check if the correct user is requested and if the session cookie is still valid
                if user['session_token'] == sid and (time.time() - float(user['session_start'])) < (20 * 60):
                    user['session_start'] = time.time()
                    return user['username']
            return ""
        else:
            return ""

    # Get message corresponding to error code
    def get_code_content(self, code):
        return switch[code]