import socket
import sys
import magic


class HTTP_server:

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

            connection.sendall(response)
            connection.close()

    def request_handler(self, data):

        # get length of request for request length
        data_length = len(data)


        # split request by line breaks to parse individual headers
        data_array = data.splitlines()
        request_start_line = data_array[0]

        if ("GET" in request_start_line[0:3]):
            print("GET request confirmed")

            # loop through and seperate the request-target to use later in finding resource
            for x in range(len(request_start_line)):
                if (request_start_line[x:(x+8)] == "HTTP/1.1"):
                    # add a dot so that request-target is seached for so the http server can be placed in somewhere other than root directory
                    request_target = "." + request_start_line[4:(x-1)]
                    print("request-target is", request_target)

            # verify if the request-target is valid here


            try:
                #request_target_file = open(request_target, "r")
                #sys.getsizeof(request_target_file)
                self.get_response_body(request_target)

            # add an except to prevent error from interupting service if request-target is invalid
            except:
                if (request_target == "./"):
                    # set the index file as the body response
                    #request_target_file = open(request_target, "r")
                    #sys.getsizeof(request_target_file)
                    # manually set the request target as the index page so there's a default page
                    request_target = "./index.html"
                    self.get_response_body(request_target)

                else:
                    print("request-target is 404 Not Found")
                    response_status_code = "404 Not Found"


            # get the length of the content and content type here

            response_start_line = "HTTP/1.1 " + response_status_code

            #content_type_response_header = request_target_type

        elif ("HEAD" in request_start_line[0:4]):
            print("HEAD request confirmed")

        elif ("OPTIONS" in request_start_line[0:7]):
            print("OPTIONS request confirmed")

        else:
            print("Invalid request")


    def get_response_body(self, request_target):
        request_target_file = open(request_target, "r")
        sys.getsizeof(request_target_file)

        mime = magic.open(magic.MAGIC_MIME)
        mime.load()
        mime.file(request_target)





if __name__ == '__main__':
    server = HTTP_server()
    server.start()
