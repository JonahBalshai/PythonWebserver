# Import packages
import time
from http.server import HTTPServer
from server import Server

# Set host and port
HOST_NAME = "localhost"
PORT_NUMBER = 8000

# Check if file executed
if __name__ == "__main__":
    # Create server address tuple
    server_address = (HOST_NAME, PORT_NUMBER)
    # Create http-object
    httpd = HTTPServer(server_address, Server)
    # Show that server up
    print(time.asctime(), "Server UP - %s:%s" % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server DOWN - %s:%s" % (HOST_NAME, PORT_NUMBER))
