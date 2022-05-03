import json
import secrets
import time
import os
import re
from response.requestHandler import RequestHandler


class RequestHandlerPOST(RequestHandler):
    def __init__(self):
        super().__init__()
        #TODO: vielleicht ist das besser machbar da variable ja nur für kreierung gebraucht wird und nur bei login kreiert wird
        self.session_token = ""

    def assignAction(self, post_content):
        action = post_content['tagPOST'][0]

        # Check if valid action
        if not self.valid_string(action):
            self.setStatus(403)
            self.contentType = 'text/plain'
            self.contents = 'Invalid action'
            return
        
        # Choose action based on tag
        actions = {
            'login': self.do_login,
            'signup': self.do_signup,
            'uploadFile': self.do_upload,
            'deleteFile': self.do_delete,
            'repositoryContent': self.do_repository_content
        }
        actions[action](post_content)

    def do_login(self, post_content):
        username = post_content['loginUsername'][0]
        password = post_content['loginPassword'][0]

        # Check if username and password valid
        if not self.valid_string(username) or not self.valid_string(password):
            self.setStatus(403)
            self.contentType = 'text/plain'
            self.contents = 'Invalid username or password'
            return

        # Open and read pseudo database
        with open('./data/users.json', 'r') as users_database:
            users = json.loads(users_database.read())
        users_list = users['users']
        # MAYBE: implement search algorithm that finds user based on username can maybe be used for account creation as well

        # Special case when userdatabase empty (MAYBE: maybe not necessary if i just create a mock/admin user so that database has at least 1 user at any point)
        if len(users_list) == 0:
            self.setStatus(403)
            self.contentType = 'text/plain'
            self.contents = 'Invalid Username/Password combination'

        for user in users_list:
            if user['username'] == username and user['password'] == password:
                self.setStatus(200)
                self.contentType = 'text/plain'

                self.session_token = self.do_create_session_token(user['username'], user['password'])
                # Write session token into database list and start the session
                user['session_token'] = self.session_token
                user['session_start'] = time.time()
                users['users'] = users_list

                # Jsonify database list
                json_data = json.dumps(users)

                # MAYBE: delete when delete func
                json_data = self.beautify(json_data)

                #Write data into database
                with open('./data/users.json', 'w') as users_database:
                    users_database.write(json_data)

                self.contents = 'Successful login.'
                break
            else:
                self.setStatus(403)
                self.contentType = 'text/plain'
                self.contents = 'Invalid Username/Password combination.'

    def do_signup(self, post_content):
        username = post_content['signupUsername'][0]
        password = post_content['signupPassword'][0]

        # Check if username and password valid
        if not self.valid_string(username) or not self.valid_string(password):
            self.setStatus(403)
            self.contentType = 'text/plain'
            self.contents = 'Invalid username or password'
            return

        with open('./data/users.json', 'r') as users_database:
            users = json.loads(users_database.read())
        users_list = users['users']

        # MAYBE: implement search algorithm that checks if any other user already has that username and then returns an
        # index. can maybe be used for login as well
        for user in users_list:
            if user['username'] == username:
                self.setStatus(403)
                self.contentType = 'text/plain'
                self.contents = 'Username already in use.'
                return

        self.session_token = self.do_create_session_token(username, password)
        # Create new user dictionary
        new_user = {
            "username": username,
            "password": password,
            "session_token": self.session_token,
            "session_start": str(time.time())
        }
        users_list.append(new_user)
        users['users'] = users_list
        json_data = json.dumps(users)

        #MAYBE: Delete this if you delete the func
        json_data = self.beautify(json_data)

        # Write data back to json file
        with open('./data/users.json', 'w') as database:
            database.write(json_data)

        # Create user repository
        os.mkdir('./content/users/{}'.format(username))
        
        self.setStatus(200)
        self.contentType = 'text/plain'
        self.contents = 'Successful signup.'

    # Method that takes file from request and saves it in server files
    def do_upload(self, post_content):
        username = post_content['username']
        fileName = post_content['fileName'][0]
        filePath = post_content['filePath'][0]
        chunk = post_content['chunkNum'][0]

        # Check if fileName, -path and chunk valid
        if not self.valid_string(fileName) or not self.valid_path(filePath) or not chunk.isdigit():
            self.setStatus(403)
            self.contentType = 'text/plain'
            self.contents = 'Invalid input'
            return

        filePath = filePath[14:] + username
        chunk = int(chunk)

        # TODO: you gotta change that to make that workable with multiple folders
        repository_list = os.listdir('./content/users/{}'.format(filePath))
        originalfileName = fileName
        # Check if the file name is already taken
        if chunk == 0 and fileName in repository_list:
            self.contents = 'Changed filename.\n'
            # Iterate possible filenames until working one found
            i = 1
            while True:
                if fileName in repository_list:
                    fileName = originalfileName
                    # TODO: this doesnt work with nested extensions so be careful
                    tempfileName, fileExt = os.path.splitext('{}'.format(fileName))
                    fileName = tempfileName + ' ({})'.format(i) + fileExt
                    i += 1
                else:
                    break
            self.contents = self.contents + '{}'.format(fileName)
        else:
            self.contents = 'Successful upload.'
        # Create the new file and fill it with the request data
        with open('./content/users/{}/{}'.format(filePath, fileName), 'ab') as newFile:
            newFile.write(post_content['payload'][0])
        self.setStatus(200)
        self.contentType = 'text/plain'

    # Method that deletes a requested file
    def do_delete(self, post_content):
        # Get information
        username = post_content['username']
        fileName = post_content['fileName'][0]
        filePath = post_content['filePath'][0]

        # Check if input valid
        if not self.valid_string(fileName) or not self.valid_path(filePath):
            self.setStatus(403)
            self.contentType('text/plain')
            self.contents('Invalid input')
            return
        
        filePath = filePath[14:] + username

        # Build filepath, check if file exists and delete it
        file_path = './content/users/{}/{}'.format(filePath, fileName)
        if os.path.isfile(file_path):
            os.remove(file_path)

        self.setStatus(200)
        self.contentType = 'text/plain'
        self.contents = 'Successfully deleted'

    # Method that returns the files in a repository
    def do_repository_content(self, post_content):
        username = post_content['username']
        #MAYBE: Don't like that i have to convert this to a string for JS maybe JS can somehow take a 
        # "stringified" python list and turn it into a list again?
        # TODO: make this work with nested folders
        repository_list = os.listdir('./content/users/{}/'.format(username))
        repository_files = ""
        for file in repository_list:
            repository_files += file + ";"
        repository_files = repository_files[:-1]
        self.setStatus(200)
        self.contentType = 'text/plain'
        self.contents = 'Files returned.\n{}'.format(repository_files)

    # TODO: maybe make that based on something else (name, password, time)?
    # Method that creates random 32 character session token        
    def do_create_session_token(self, user, password):
        session_token = secrets.token_urlsafe(32)
        return session_token

    # Check if string only contains characters, number, dashes and underscores
    def valid_string(self, string):
        if re.match('^[.A-Za-z0-9 ()öäü_-]+$', string):
            return True
        else:
            return False

    # Check if path valid
    def valid_path(self, path):
        if re.match('^[/A-Za-z0-9 ()öäü_-]+$', path):
            return True
        else:
            return False


    # Beautify the data MAYBE: DELETE FOR PERFORMANCE IF DATABASE GETS TOO BIG
    def beautify(self, json_data):
        space_characters = ['[', ']', '{', '}', ',']
        index = 0
        while index < len(json_data):
            if json_data[index] in space_characters:
                json_data = json_data[:index+1] + '\n' + json_data[index+1:]
                index += 1
            index += 1
        return json_data


    # MAYBE: Finish this algorithm once bigger database established
    def search_user_list(self, user_list, searched_username):
        # Divide the list in two
        list_middle = len(user_list)//2
        # Set the index
        index = list_middle
        # Set check variable
        user_found = False
        # Loop until user found
        while not user_found:
            # Check if username greater less or equal to the username in the list middle
            user_found = True