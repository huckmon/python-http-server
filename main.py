import socket
import sys
import mimetypes
import datetime
import re


class HTTP_server:

    # A constant used the append the http version. This should never change
    HTTP_VER = "HTTP/1.1 "
    TOTAL_CONNECTIONS = 1
    DATA_TO_READ = 1024

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

            # accept a connection. The return value is a pair (connection, address)
            # connection is a new socket object usable to send and recieve data on the connection (i.e. connecting socket)
            # client_address is the address bound to the socket on the other end of the connection
            connection, client_addr = server_socket.accept()
            print('Connection accepted ' )
            # recieve data from the socket. Specify a maximum amount of data to be read at once (currently first 1024 bytes)
            data = connection.recv(self.DATA_TO_READ)

            #if data:
            # Generate the response message by calling the request_handler function with the data recieved from the connection as input
            response_message = self.request_handler(data)
            # send back data to the client
            connection.sendall(response_message)
            print('Response Sent')

            #else:
            # close the connection
            connection.close()
            print('Connection Closed')


    def request_handler(self, data):

        # get length of request for request length
        data = data.decode("utf-8")
        data_length = len(data)

        # split request by line breaks to parse individual headers
        data_array = data.splitlines()
        request_start_line = data_array[0]
        print(request_start_line)
        for x in range(len(request_start_line)):
            # loop throught the request start line and seperate the request type
            if request_start_line[x] == " ":
                current_request_method = request_start_line[0:x]
                print('Current request method: ' + current_request_method)
                break

        # match case sorts through the request methods and then goes to specific function for method
        match current_request_method:
            case "GET":
                response = self.get_method_received(request_start_line)
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

    # Function for receiving GET methods
    def get_method_received(self, request_start_line):
        print("GET Request Confirmed")

        # loop through and seperate the request-target to use later in finding resource
        # probably want to replace this with regex queries later so that it's not so scuffed
        print('request_start_line ' + request_start_line)
        for x in range(len(request_start_line)):
            if (request_start_line[x:(x+8)] == "HTTP/1.1"):
                # add a dot so that request-target is seached for so the http server can be placed in somewhere other than root directory
                request_target = "." + request_start_line[4:(x-1)]
                break

        # if pointing at root, redirect to index file
        if (request_target == "./"):
            # manually set the request target as the index page so there's a default page
            request_target = "./index.html"

            request_target_file = open(request_target, "r")
            content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))
            response_status_code = "200 OK"

        # no reason to call any but else since can just use except to throw a 400 or 404
        # handles non-root and invalid path requests
        else:
            try:
                request_target_file = open(request_target, "r")
                content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))
                response_status_code = "200 OK"
            except:
                # The reuested item wasn't found, return a 404 respose
                response_status_code = "404 Not Found"

                # change the request_target file to the stock 404 file to avoid renaming variables or adding checks. Allows users to edit 404 page
                request_target_file = open("./404-page.html", "r")
                content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))

        response_start_line = self.HTTP_VER + response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(request_target)
        temp_response = response_start_line + "\r\n" + date_header + "\r\n" + content_length_header + "\r\n" + content_type_header + "\r\n"

        http_page_line_array = request_target_file.read().splitlines()
        http_page_line = ""

        # loops through the lines in the request_target_file as an array
        for x in range(len(http_page_line_array)):
            http_page_line = http_page_line + "\r\n" + http_page_line_array[x]

        temp_response_bytes = temp_response.encode(encoding="utf-8")
        http_page_lines_bytes = http_page_line.encode(encoding="utf-8")
        response_message = b"".join([temp_response_bytes, http_page_lines_bytes])

        return response_message

    # Function when receiving HEAD methods
    def head_method_received(self, request_start_line):
        print("HEAD request confirmed")

        # loop through and seperate the request-target to use later in finding resource
        # probably want to replace this with regex queries later so that it's not so scuffed
        for x in range(len(request_start_line)):
            if (request_start_line[x:(x+8)] == "HTTP/1.1"):
                # add a dot so that request-target is seached for so the http server can be placed in somewhere other than root directory"
                request_target = "." + request_start_line[5:(x-1)]
                break

        # if pointing at root, redirect to index file
        if (request_target == "./"):
            # manually set the request target as the index page so there's a default page
            request_target = "./index.html"

            request_target_file = open(request_target, "r")
            content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))
            response_status_code = "200 OK"

        # no reason to call any but else since can just use except to throw a 400 or 404
        # handles non-root and invalid path requests
        else:
            try:
                request_target_file = open(request_target, "r")
                content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))
                response_status_code = "200 OK"
            except:
                response_status_code = "404 Not Found"

                # change the request_target_file to the stock 404 file to avoid renaming variables or adding checks
                request_target_file = open("./404-page.html", "r")
                content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))

        response_start_line = self.HTTP_VER + response_status_code
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")
        content_type_header = self.get_content_mime_type(request_target)

        temp_response = response_start_line + "\r\n" + date_header + "\r\n" + content_length_header + "\r\n" + content_type_header + "\r\n"
        response_message = temp_response.encode(encoding="utf-8")

        return response_message

    # Function for receiving OPTIONS methods
    def options_method_received(self, request_start_line):
        print("OPTIONS request confirmed")

        response_status_code = "204 No Content"
        response_start_line = self.HTTP_VER + response_status_code
        allowed_option_header = "OPTIONS, HEAD, GET"
        date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")

        temp_response = response_start_line + "\r\n" + allowed_option_header + "\r\n" + date_header + "\r\n"
        response_message = temp_response.encode(encoding="utf-8")

        return response_message

    # Function for recieving unimplemented methods
    def not_implemented_response(self, request_start_line):

        response_status_code = "501 Not Implemented"
        response_start_line = self.HTTP_VER + response_status_code
        response_message = response_start_line.encode(encoding="utf-8")

        return response_message

    # Function for returning a bad request method/400 response code
    def invalid_request_method(self, request_start_line):
        print("Invalid request recieved")

        response_status_code = "400 Bad Request"
        response_start_line = self.HTTP_VER + response_status_code
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

    # function gets the MIME type of input
    def get_content_mime_type(self, request_target):
        # quick function to get the mime type and then throw it back so this isn't repeated multiple times'
        content_type = mimetypes.guess_type(request_target)

        #print("mime type of request-target is", content_type[0])

        content_type_header = "Content-Type: " + str(content_type[0])
        print(content_type_header)
        return content_type_header

if __name__ == '__main__':
    # start the http server when script is executed
    server = HTTP_server()
    server.start()
