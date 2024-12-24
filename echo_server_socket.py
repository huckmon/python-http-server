import socket

# test echo server to understand python socket functionality

# Creates a TCP/IP socket using INET (ipv4) address family and Sock Stream (sock stream is a SocketKind)
echo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# binds the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address))
echo_socket.bind(server_address)

# listen for a single incoming connection
echo_socket.listen(1)

while True:
    # wait for a connection
    print('waiting for connection')

    # accept a connection. The return value is a pair (conn, address)
    # connection is a new socket object usable to send and recieve data on the connection (i.e. connecting socket)
    # client_address is the address bound to the socket on the other end of the connection
    connection, client_address = echo_socket.accept()
    try:
        print('connection from ', client_address)

        # recieve data in small chunks and retransmit it
        while True:

            # recieve data from the socket. Specify a maximum amount of data to be recieved at once at 16 bytes
            data = connection.recv(4096)
            print('recieved ', data)
            if data:
                print('sending data back to client')
                # specifies to send all data to socket
                connection.sendall(data)
            else:
                print('no data from', client_address)
                # break loop as soon as no data is being recieved
                break

    # block ensures that close is always called
    finally:
        # end connection to clean socket
        print('closing connection')
        connection.close()
