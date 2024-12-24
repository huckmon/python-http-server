import socket
import sys
import mimetypes
import datetime
import re


class HTTP_server:

    http_ver = "HTTP/1.1 "

    def __init__(self, host='127.0.0.1', port=10000):
        self.host = host
        self.port = port

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)

        print('listening at', server_socket.getsockname())

        while True:

            connection, client_addr = server_socket.accept()

            data = connection.recv(1024)

            response = self.request_handler(data)

            #connection.sendall(response)
            connection.close()


    def request_handler(self, data):

        # get length of request for request length
        data = data.decode("utf-8")
        data_length = len(data)


        # split request by line breaks to parse individual headers
        data_array = data.splitlines()
        request_start_line = data_array[0]
        print(request_start_line)

        if ("GET" in request_start_line[0:3]):
            print("GET request confirmed")

            # loop through and seperate the request-target to use later in finding resource
            # probably want to replace this with regex queries later so that it's not so scuffed
            for x in range(len(request_start_line)):
                if (request_start_line[x:(x+8)] == "HTTP/1.1"):
                    # add a dot so that request-target is seached for so the http server can be placed in somewhere other than root directory
                    request_target = "." + request_start_line[4:(x-1)]
                    print("request-target is", request_target)

            # if pointing at root, redirect to index file
            if (request_target == "./"):
                # manually set the request target as the index page so there's a default page
                request_target = "./index.html"

                request_target_file = open(request_target, "r")
                content_length = sys.getsizeof(request_target_file)

                # get the content type and saves as a tuple natively, don't need to modify as can just take part of tuple
                self.get_content_mime_type(request_target)

                response_status_code = "200 OK"


            # no reason to call any but else since can just use except to throw a 400 or 404
            # handles non-root and invalid path requests
            else:
                try:
                    request_target_file = open(request_target, "r")
                    content_length = sys.getsizeof(request_target_file)

                    self.get_content_mime_type(request_target)

                    response_status_code = "200 OK"
                except:
                    response_status_code = "404 Not Found"


            response_start_line = http_ver + response_status_code
            print("response start line is", response_start_line)

            date_header = datetime.datetime.now().strftime("%a, %d, %b, %Y, %H:%M:%S GMT")
            print(date_header)





        elif ("HEAD" in request_start_line[0:4]):
            print("HEAD request confirmed")

        elif ("OPTIONS" in request_start_line[0:7]):
            print("OPTIONS request confirmed")

        else:
            print("Invalid request", request_start_line)


    def get_content_mime_type(self, request_target):
        # quick function to get the mime type and then throw it back so this isn't repeated multiple times'
        content_type = mimetypes.guess_type(request_target)
        print("mime type of request-target is", content_type[0])
        content_type = content_type[0]
        return content_type



if __name__ == '__main__':
    server = HTTP_server()
    server.start()
