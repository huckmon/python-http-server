import socket
import mimetypes
import datetime

class HTTP_server:

    # Needs the trailing whitespace for .
    HTTP_VER = "HTTP/1.1 "
    TOTAL_CONNECTIONS = 1
    DATA_TO_READ = 1024
    BLANK_LINE = "\r\n".encode(encoding="utf-8")

    client_method = None
    is_404 = None
    response_status_code = None

    def __init__(self, host='127.0.0.1', port=10002):
        self.host = host
        self.port = port

    def start(self):
        # Creates a TCP/IP socket using INET (ipv4) address family and Sock Stream (sock stream is a SocketKind)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # binds the socket to the port
        server_socket.bind((self.host, self.port))
        # listen for incoming connection(s)
        server_socket.listen(self.TOTAL_CONNECTIONS)
        print('listening at :', server_socket.getsockname())

        while True:
            # accept a connection. The return value is a pair (connection, address)
            # connection is a new socket object usable to send and recieve data on the connection (i.e. connecting socket)
            # client_address is the address bound to the socket on the other end of the connection
            connection, client_addr = server_socket.accept()
            print(f'Connection accepted from {client_addr}')
            # recieve data from the socket. Specify a maximum amount of data to be read at once (currently first 1024 bytes)
            data = connection.recv(self.DATA_TO_READ)

            response_message = self.request_handler(data)
            # send back data to the client
            connection.sendall(response_message)
            print(f'Response Sent to {client_addr}')

            connection.close()
            print(f'Connection Closed to {client_addr}' + "\r\n" + '---------------------------')

    def request_handler(self, data):

        self.is_404 = False
        data = data.decode("utf-8")
        data_array = data.splitlines()
        request_start_line = data_array[0].split(" ")
        print('request_start_line :' + str(request_start_line))
        self.client_method = request_start_line[0]

        # two if staments get around issue of browsers that don't send URI for homepages
        if len(request_start_line) > 2:
            request_target = request_start_line[1]

        if len(request_start_line) > 3:
            request_target = request_start_line[2]

        match self.client_method:
            case "GET":
                response = self.get_method_received(request_start_line, request_target)
                return response
            case "HEAD":
                response = self.head_method_received(request_start_line)
                return response
            case "OPTIONS":
                response = self.options_method_received(request_start_line)
                return response
            case "POST":
                response = self.not_implemented_response(request_start_line)
                return response
            case "PUT":
                response = self.not_implemented_response(request_start_line)
                return response
            case "DELETE":
                response = self.not_implemented_response(request_start_line)
                return response
            case "CONNECT":
                response = self.not_implemented_response(request_start_line)
                return response
            case "TRACE":
                response = self.not_implemented_response(request_start_line)
                return response
            case "PATCH":
                response = self.not_implemented_response(request_start_line)
                return response
            case _:
                response = self.invalid_request_method(request_start_line)
                return response

    def get_method_received(self, request_start_line, request_target):

        body_response = self.parse_request_target(request_target)

        response_start_line = self.HTTP_VER + self.response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(request_target)

        response_headers = (response_start_line + "\r\n" + date_header + "\r\n" + content_type_header + "\r\n").encode(encoding="utf-8")

        if ((self.is_404 is True) or (body_response == "fail")):
            print("returning 404 reponse")
            response_message = response_encoded
        else:
            response_message = b"".join([response_headers, self.BLANK_LINE, body_response])

        return response_message

    # Function when receiving HEAD methods
    def head_method_received(self, request_start_line, request_target):

        body_response = parse_request_target(request_target)

        response_start_line = self.HTTP_VER + self.response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(request_target)

        response_headers = (response_start_line + "\r\n" + date_header + "\r\n" + content_type_header + "\r\n").encode(encoding="utf-8")

        return response_headers

    # Function for receiving OPTIONS methods
    def options_method_received(self, request_start_line):

        self.response_status_code = "204 No Content"
        response_start_line = self.HTTP_VER + self.response_status_code
        allowed_option_header = "OPTIONS, HEAD, GET"
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")

        response_headers = (response_start_line + "\r\n" + allowed_option_header + "\r\n" + date_header + "\r\n").encode(encoding="utf-8")

        return response_headers

    # Function for recieving unimplemented methods
    def not_implemented_response(self, request_start_line):

        self.response_status_code = "501 Not Implemented"
        response_headers = (self.HTTP_VER + self.response_status_code).encode(encoding="utf-8")

        return response_headers

    # Function for returning a bad request method/400 response code
    def invalid_request_method(self, request_start_line):
        print("Invalid request recieved")

        self.response_status_code = "400 Bad Request"
        response_start_line = self.HTTP_VER + self.response_status_code
        body_response = b"""
        {
            "error": "Bad Request",
            "message": "Request body could not be read properly"
        }
        """

        response_raw = response_start_line + "\r\n"
        response_encoded = response.encode(encoding="utf-8")
        response_message = b"".join([response_encoded, body_response])

        return response_message

    def parse_request_target(self, request_target):

        try:
            if(request_target != "/"):
                request_target = request_target[1:]
            else:
                request_target = "index.html"

            print(f'Opening and reading request target: {request_target}')
            with open(request_target, "rb") as f:
                    request_target_file = f.read()

            self.response_status_code = "200 OK"
            return request_target_file

        except Exception as e:
            print(e)
            self.response_status_code = "404 Not Found"
            self.is_404 = True;
            #request_target_file = open("./404-page.html", "rb")
            request_target_file = "fail".encode(encoding="utf-8")

        return request_target_file

    # function gets the MIME type of input
    def get_content_mime_type(self, request_target):
        try:
            if (request_target == "/"):
                request_target = "index.html"
            # quick function to get the mime type and then throw it back so this isn't repeated multiple times
            content_type = mimetypes.guess_type(request_target)
            #print("mime type of request-target is", content_type[0])
            content_type_header = "Content-Type: " + content_type[0]
            print(content_type_header)
            return content_type_header
        except:
            return

    def get_content_length(self, request_target):
        try:
            content_length_header = "Content-Length: " + str(request_target_file.__sizeof__())
            #content_length_header = "Content-Length: " + str(sys.getsizeof(request_target))
        except Exception as e:
            print(e)
            content_length_header = "Content-Length: 0"
        print(f'Sending {content_length_header}')
        return content_length_header

if __name__ == '__main__':
    # start the http server when script is executed

    server = HTTP_server()
    server.start()
