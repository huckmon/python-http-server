import socket
import mimetypes
import datetime

class HTTP_server:

    # A constant used the append the http version. This should never change. Always needs a space afterwards for less code.
    HTTP_VER = "HTTP/1.1 "
    TOTAL_CONNECTIONS = 1
    DATA_TO_READ = 1024
    BLANK_LINE = "\r\n".encode(encoding="utf-8")

    # variables for client request
    client_uri = None
    client_http_ver = None
    client_method = None
    is_404 = None
    response_status_code = None

    # initial function that declares the host and port for the http server
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
        print('listening at', server_socket.getsockname())

        while True:
            #try:
                # accept a connection. The return value is a pair (connection, address)
                # connection is a new socket object usable to send and recieve data on the connection (i.e. connecting socket)
                # client_address is the address bound to the socket on the other end of the connection
                connection, client_addr = server_socket.accept()
                print(f'Connection accepted from {client_addr}')
                # recieve data from the socket. Specify a maximum amount of data to be read at once (currently first 1024 bytes)
                data = connection.recv(self.DATA_TO_READ)

                # Generate the response message by calling the request_handler function with the data recieved from the connection as input
                response_message = self.request_handler(data)
                # send back data to the client
                connection.sendall(response_message)
                print(f'Response Sent to {client_addr}')

                connection.close()
                print(f'Connection Closed to {client_addr}' + "\r\n" + '---------------------------')

    def request_handler(self, data):

        # set is a 404 request to false by default, correct later if needed
        self.is_404 = False

        # get length of request for request length
        data = data.decode("utf-8")

        # split request by line breaks to parse individual headers
        data_array = data.splitlines()
        request_start_line = data_array[0].split(" ")
        print(request_start_line)
        self.client_method = request_start_line[0]
        print('Current request method: ' + self.client_method)

        # two if staments get around issue of browsers that don't send URI for homepages
        # bumped up the numbers for both if statements by one because the request_start_line became a list instead of array(?)
        if len(request_start_line) > 2:
            request_target = request_start_line[1]

        if len(request_start_line) > 3:
            request_target = request_start_line[2]

        # match case sorts through the request methods and then goes to specific function for method
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

        print("GET Request Confirmed")

        # loop through and seperate the request-target to use later in finding resource
        # probably want to replace this with regex queries later so that it's not so scuffed
        print('request_start_line ' + str(request_start_line))

        # get the targeted file and response code from this func
        # if pointing at root, redirect to index file
        if (request_target == "/"):
            # manually set the request target as the index page so there's a default page
            request_target = "index.html"

            # read and save the requested file as a variable
            print(f'opening and reading {request_target}')
            #request_target_file_open = open(request_target, "rb")
            #request_target_file = request_target_file_open.read()

            with open(request_target, "rb") as f:
                    request_target_file = f.read()

            self.response_status_code = "200 OK"


        # no reason to call any but else since can just use except to throw a 400 or 404
        # handles non-root and invalid path requests
        else:
            request_target = request_target.strip('/')
            try:
                print(f'request target path is {request_target}')

                #request_target_file_open = open((request_target), "rb")
                #request_target_file = request_target_file_open.read()
                print(request_target)
                print(f'opening and reading {request_target}')
                with open(request_target, "rb") as f:
                    request_target_file = f.read()

                self.response_status_code = "200 OK"

            except Exception as e:
                print(e)
                print("opening/reading requested file failed")
                # The reuested item wasn't found so return a 404 respose
                self.response_status_code = "404 Not Found"

                # change the request_target file to the stock 404 file to avoid renaming variables or adding checks. Allows users to edit 404 page
                # this currently doesn't work because it doesn't take into account non html content type requests
                self.is_404 = True;
                #request_target_file = open("./404-page.html", "rb")

        # combine http version and response code for http response
        response_start_line = self.HTTP_VER + self.response_status_code
        # generate the date header of http response
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        # call a function to get the mime type of the requested target
        content_type_header = self.get_content_mime_type(request_target)

        # reponse is the http version, response code, date time and content type header
        # add them together for encoding. Don't bother with a line break at the end because it doesn't save
        response = response_start_line + "\r\n" + date_header + "\r\n" + content_type_header + "\r\n"

        # encode the response from ascii/str to bytes
        response_bytes = response.encode(encoding="utf-8")

        # simple check if a 404 is declared
        if (self.is_404 == True):
            print("returning 404 reponse")
            response_message = b"".join([response_bytes])
        #elif(is404 and requested_content_type == "text/html"):
        #    response_message = b"".join([response_bytes, (request_target_file = open("./404-page.html", "rb")])
        else:
            response_message = b"".join([response_bytes, self.BLANK_LINE, request_target_file])

        return response_message

    # Function when receiving HEAD methods
    def head_method_received(self, request_start_line, request_target):
        print("HEAD request confirmed")

        # only running this for the response code rather than the request target
        request_target_file = read_request_target(request_target)

        response_start_line = self.HTTP_VER + self.response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(request_target)

        temp_response = response_start_line + "\r\n" + date_header + "\r\n" + content_length_header + "\r\n" + content_type_header + "\r\n"
        response_message = temp_response.encode(encoding="utf-8")

        return response_message

    # Function for receiving OPTIONS methods
    def options_method_received(self, request_start_line):
        print("OPTIONS request confirmed")

        self.response_status_code = "204 No Content"
        response_start_line = self.HTTP_VER + self.response_status_code
        allowed_option_header = "OPTIONS, HEAD, GET"
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")

        temp_response = response_start_line + "\r\n" + allowed_option_header + "\r\n" + date_header + "\r\n"
        response_message = temp_response.encode(encoding="utf-8")

        return response_message

    # Function for recieving unimplemented methods
    def not_implemented_response(self, request_start_line):

        self.response_status_code = "501 Not Implemented"
        response_start_line = self.HTTP_VER + self.response_status_code
        response_message = response_start_line.encode(encoding="utf-8")

        return response_message

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

        temp_response = response_start_line + "\r\n"
        temp_response_bytes = temp_response.encode(encoding="utf-8")
        response_message = b"".join([temp_response_bytes, body_response])

        return response_message

    # function reads the request target and returns it
    def read_request_target(self, request_target):

        # if pointing at root, redirect to index file
        if (request_target == "/"):
            # manually set the request target as the index page so there's a default page
            request_target = "index.html"

            # read and save the requested file as a variable
            print(f'opening and reading {request_target}')
            #request_target_file_open = open(request_target, "rb")
            #request_target_file = request_target_file_open.read()

            with open(request_target, "rb") as f:
                    request_target_file = f.read()

            self.response_status_code = "200 OK"


        # no reason to call any but else since can just use except to throw a 400 or 404
        # handles non-root and invalid path requests
        else:
            request_target = request_target.strip('/')
            try:
                print(f'request target path is {request_target}')

                #request_target_file_open = open((request_target), "rb")
                #request_target_file = request_target_file_open.read()
                print(request_target)
                print(f'opening and reading {request_target}')
                with open(request_target, "rb") as f:
                    request_target_file = f.read()

                self.response_status_code = "200 OK"

            except Exception as e:
                print(e)
                print("opening/reading requested file failed")
                # The reuested item wasn't found so return a 404 respose
                self.response_status_code = "404 Not Found"

                # change the request_target file to the stock 404 file to avoid renaming variables or adding checks. Allows users to edit 404 page
                # this currently doesn't work because it doesn't take into account non html content type requests
                self.is_404 = True;
                #request_target_file = open("./404-page.html", "rb")

            if (request_target_file == None):
                return
            else:
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
        # throw exception if can't get mime type (usually means file doesn't exist)
        except:
            return

    def get_content_length(self, request_target):
        # set the length of the content header to size of file
        try:
            content_length_header = "Content-Length: " + str(request_target_file.__sizeof__())
            #content_length_header = "Content-Length: " + str(sys.getsizeof(request_target))
        except Exception as p:
            print(p)
            content_length_header = "Content-Length: 0"

        print(f'Sending {content_length_header}')

if __name__ == '__main__':
    # start the http server when script is executed

    server = HTTP_server()
    server.start()
