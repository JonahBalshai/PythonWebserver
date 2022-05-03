# Placeholder object for requests without .read function
class MockFile():
    def read(self):
        return None


class RequestHandler():
    def __init__(self):
        self.contentType = ""
        self.contents = MockFile()

    # Get contents of file
    def getContents(self):
        return self.contents.read()

    # Get file to read
    def read(self):
        return self.contents

    # Set status
    def setStatus(self, status):
        self.status = status

    # Get status
    def getStatus(self):
        return self.status

    # Get Content Type
    def getContentType(self):
        return self.contentType