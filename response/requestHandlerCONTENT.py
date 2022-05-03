import mimetypes
from response.requestHandler import RequestHandler


class RequestHandlerCONTENT(RequestHandler):
    def __init__(self):
        super().__init__()

    def find(self, file_path):
        # Split path
        mimeType = mimetypes.guess_type(file_path)[0]

        # Get mode in which file needs to be opened
        if mimeType.startswith('test'):
            mode = 'rt'
        else:
            mode = 'rb'
        
        # Open file and read in chunks
        with open(file_path, mode) as file:
            # Set content type and status code
            self.setContentType(mimeType)
            self.setStatus(200)
            i = 0
            while True:
                i += 1
                self.contents = file.read(1024 * 1024)
                if not self.contents:
                    break
                yield i

    def setContentType(self, mimeType):
        self.contentType = mimeType