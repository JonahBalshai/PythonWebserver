import os
import urllib.parse

class Router:
    # Build the path from the request to make the server able to work with it
    def buildPath(self, request_path, username):
        # Check if the file is supposed to be downloaded or displayed
        if request_path.startswith('/content'):
            # Get file name
            fileName = request_path[request_path[1:].find('/')+2:]
            # Fix the problem with spaces in file names
            fileName = urllib.parse.unquote_plus(fileName)
            # Build the path
            file_path = 'content/users/{}/{}'.format(username, fileName)
        else:
            # Get the extension of the requested file
            request_ext = os.path.splitext(request_path)[1]
            # Check if the request is for index.html file since these need to be covered separately
            if request_ext == '':
                # Build the path to look for and normalize it to cover edge case "/"
                file_path = os.path.normpath(('templates{}/index.html').format(request_path))
            else:
                # Build the path to look for display files that are not html
                file_path = os.path.normpath(('templates{}').format(request_path))
        return file_path

    # Check the internal files to find out if the file exists and the user is allowed access to it
    def checkPath(self, check_path, username):
        # Check if file path is valid
        if not os.path.isfile(check_path):
            return 404
        else:
            # Check for all kinds of forbidden things in the request
            if '..' in check_path:
                return 403
            
            # Check if accessing repositories while not logged in
            if username == '' and check_path.startswith('templates/repositories'):
                return 403
        # If request passes everything return OK
        return 200