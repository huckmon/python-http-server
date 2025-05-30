import socket
import mimetypes
import datetime
import re

class HTTP_server:

    # Needs the trailing whitespace to avoid multiple `+ " "` additions in other areas of the code
    HTTP_VER = "HTTP/1.1 "
    MAX_CONNECTIONS = 1
    TOTAL_BYTES_TO_READ = 1024
    BLANK_LINE = "\r\n".encode(encoding="utf-8")

    client_method = None
    is_404 = None
    response_status_code = None
    request_target = None

    def __init__(self, host='127.0.0.1', port=10002):
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(self.MAX_CONNECTIONS)
        print('listening at:', server_socket.getsockname())

        while True:
            connection, client_addr = server_socket.accept()
            print(f'Connection Accepted from: {client_addr}')
            data = connection.recv(self.TOTAL_BYTES_TO_READ)

            response_message = self.request_handler(data)
            connection.sendall(response_message)
            print(f'Response to Client: {self.HTTP_VER, self.response_status_code} at {client_addr}')

            connection.close()
            print(f'Connection Closed to: {client_addr} \r\n---------------------------')

    def request_handler(self, data):

        self.is_404 = False
        data = data.decode("utf-8")
        data_array = data.splitlines()
        request_start_line = data_array[0].split(" ")
        print(f'Client Request line : {str(request_start_line)}')
        self.client_method = request_start_line[0]

        if len(request_start_line) > 1:
            # this statment gets around issue of some browsers not sending a URI for homepages
            self.request_target = request_start_line[1]

        match self.client_method:
            case "GET":
                response = self.get_method_received(request_start_line, self.request_target)
                return response
            case "HEAD":
                response = self.head_method_received(request_start_line, self.request_target)
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

        body_response = self.parse_request_target(self.request_target)

        response_start_line = self.HTTP_VER + self.response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(self.request_target)

        #response_headers = (response_start_line + "\r\n" + date_header + "\r\n" + content_type_header + "\r\n").encode(encoding="utf-8")

        if ((self.is_404 is True) or (body_response == "fail")):
            response_headers = (response_start_line + "\r\n" + date_header + "\r\n").encode(encoding="utf-8")
            response_message = response_headers
        else:
            response_headers = (response_start_line + "\r\n" + date_header + "\r\n" + content_type_header + "\r\n").encode(encoding="utf-8")
            response_message = b"".join([response_headers, self.BLANK_LINE, body_response])

        return response_message

    def head_method_received(self, request_start_line, request_target):

        body_response = self.parse_request_target(self.request_target)

        response_start_line = self.HTTP_VER + self.response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(self.request_target)

        if ((self.is_404 is True) or (body_response == "fail")):
            response_headers = (response_start_line + "\r\n" + date_header + "\r\n").encode(encoding="utf-8")
            response_message = response_headers
        else:
            response_headers = (response_start_line + "\r\n" + date_header + "\r\n" + content_type_header + "\r\n").encode(encoding="utf-8")

        return response_headers

    def options_method_received(self, request_start_line):

        self.response_status_code = "204 No Content"
        response_start_line = self.HTTP_VER + self.response_status_code
        allowed_option_header = "Allow: OPTIONS, HEAD, GET" # hard coded because I'm  lazy and I don't intend to add more methods currently
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")

        response_headers = (response_start_line + "\r\n" + allowed_option_header + "\r\n" + date_header + "\r\n").encode(encoding="utf-8")

        return response_headers

    def not_implemented_response(self, request_start_line):

        self.response_status_code = "501 Not Implemented"
        response_headers = (self.HTTP_VER + self.response_status_code).encode(encoding="utf-8")

        return response_headers

    def invalid_request_method(self, request_start_line):

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

        if( re.search(r'\.\.\/', self.request_target) != None ):
            request_target_file = "fail".encode(encoding="utf-8")
            self.response_status_code = "404 Not Found"
            self.is_404 = True;
            return request_target_file
        elif(self.request_target == "/"):
            self.request_target = "index.html"
        else:
            self.request_target = self.request_target[1:]

        try:
            print(f'Opening and reading request target: {self.request_target}')
            with open(self.request_target, "rb") as f:
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

    def get_content_mime_type(self, request_target):
        try:
            content_type_header = "Content-Type: " + mimetypes.guess_type(request_target)[0]
            print(f'Requested Content Type is: \"{content_type_header}\"')
            return content_type_header
        except:
            return

    def get_content_length(self, request_target):
        try:
            content_length_header = "Content-Length: " + str(request_target_file.__sizeof__())
        except Exception as e:
            print(e)
            content_length_header = "Content-Length: 0"
        print(f'Returning content length: \"{content_length_header}\"')
        return content_length_header

if __name__ == '__main__':
    server = HTTP_server()
    server.start()
