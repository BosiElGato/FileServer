import zmq

def main():
    # Address for each server to receive files
    servAddresses = []

    context = zmq.Context()
    servers = context.socket(zmq.REP)
    servers.bind("tcp://*:5555")

    clients = context.socket(zmq.REP)
    clients.bind("tcp://*:6666")

    poller = zmq.Poller()
    poller.register(servers, zmq.POLLIN)
    poller.register(clients, zmq.POLLIN)

    while True:
        socks = dict(poller.poll())
        if clients in socks:
            print("Message from client")
            operation, *msg = clients.recv_multipart()

            if operation.decode('ascii') == "AvailableServersForUpload":
                clients.send_multipart(servAddresses)

            elif operation.decode('ascii') == "Download":
                #print("Operation doesn't supported")
                #clients.send_multipart(servAddresses)
                f = open("InfoFiles.txt","r") #opens file with name of "test.txt"
                #print(f.read(1))
                myList = []
                for line in f:
                    myList.append(line)
                pos = 0
                addrforclient = "Archivo No existe"
                for pos1 in myList:
                    if pos1 == msg[0].decode('ascii')+"\n":
                        #print("El archivo existe")
                        addrforclient = myList[pos + 1]
                    pos+=1
                clients.send(bytes(addrforclient,'ascii'))              

            elif operation.decode('ascii') == "Share":
                print("No implemented yet")

            elif operation.decode('ascii') == "UploadedFile":
                InfoFiles = open("InfoFiles.txt","a")
                InfoFiles.write(msg[0].decode('ascii')+"\n")
                InfoFiles.write(msg[1].decode('ascii')+"\n")
                clients.send(b"File Uploaded Susscesfully")
                InfoFiles.close()

            else:
                print("Operation doesn't supported")


        if servers in socks:
            print("Message from server")
            operation, *rest = servers.recv_multipart()
            if operation == b"newServer":
                servAddresses.append(rest[0])
                print(servAddresses)
                servers.send(b"Ok")


if __name__ == '__main__':
    print("\tBosiElGato")
    print("\tActivated Proxy")
    print("\tAll Rigths Reserved")
    print("\tEnjoy Utorrent")
    main()
