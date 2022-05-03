import mimetypes
from response.requestHandler import RequestHandler


class RequestHandlerGET(RequestHandler):
    def __init__(self):
        super().__init__()

    def find(self, file_path):
        # Split path
        mimeType = mimetypes.guess_type(file_path)[0]
        
        if mimeType.startswith('text'):
            self.contents = open(file_path)
        else:
            self.contents = open(file_path, 'rb')

        # Set content type and status code
        self.setContentType(mimeType)
        self.setStatus(200)

    def setContentType(self, mimeType):
        self.contentType = mimeType