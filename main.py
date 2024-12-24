import socket
import sys
import mimetypes
import datetime
import re


class HTTP_server:

    http_ver = "HTTP/1.1 "

    def __init__(self, host='127.0.0.1', port=10002):
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

            #if data:
            response_message = self.request_handler(data)

            connection.sendall(response_message)

            #else:

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
                    # add a dot so that request-target is seached for so the http server can be placed in somewhere other than root directory+ "; charset=UTF-8"
                    request_target = "." + request_start_line[4:(x-1)]

                    #print("request-target is", request_target)

            # if pointing at root, redirect to index file
            if (request_target == "./"):
                # manually set the request target as the index page so there's a default page
                request_target = "./index.html"

                request_target_file = open(request_target, "r")
                content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))

                # get the content type and saves as a tuple natively, don't need to modify as can just take part of tuple
                #self.get_content_mime_type(request_target)

                response_status_code = "200 OK"


            # no reason to call any but else since can just use except to throw a 400 or 404
            # handles non-root and invalid path requests
            else:
                try:
                    request_target_file = open(request_target, "r")
                    content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))

                    #self.get_content_mime_type(request_target)

                    response_status_code = "200 OK"
                except:
                    response_status_code = "404 Not Found"

                    # change the request_target_file to the stock 404 file to avoid renaming variables or adding checks
                    request_target_file = open("./404-page.html", "r")
                    content_length_header = "Content-Length: " + str(sys.getsizeof(request_target_file))


            response_start_line = self.http_ver + response_status_code

            date_header = datetime.datetime.now().strftime("Date: %a, %d, %b, %Y, %H:%M:%S GMT")

            content_type_header = self.get_content_mime_type(request_target)

            temp_response = response_start_line + "\r\n" + date_header + "\r\n" + content_length_header + "\r\n" + content_type_header + "\r\n"

            http_page_line_array = request_target_file.read().splitlines()

            http_page_line = ""

            for x in range(len(http_page_line_array)):
                http_page_line = http_page_line + "\r\n" + http_page_line_array[x]


            temp_response_bytes = temp_response.encode(encoding="utf-8")
            http_page_lines_bytes = http_page_line.encode(encoding="utf-8")

            response_message = b"".join([temp_response_bytes, http_page_lines_bytes])

            return response_message



        elif ("HEAD" in request_start_line[0:4]):
            print("HEAD request confirmed")

        elif ("OPTIONS" in request_start_line[0:7]):
            print("OPTIONS request confirmed")

        else:
            print("Invalid request", request_start_line)


    def get_content_mime_type(self, request_target):
        # quick function to get the mime type and then throw it back so this isn't repeated multiple times'
        content_type = mimetypes.guess_type(request_target)

        #print("mime type of request-target is", content_type[0])

        content_type_header = "Content-Type: " + str(content_type[0])
        print(content_type_header)
        return content_type_header


if __name__ == '__main__':
    server = HTTP_server()
    server.start()
