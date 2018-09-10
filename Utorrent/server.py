
import zmq
import sys


partSize = 1024 * 1024 * 10

def main():
    if len(sys.argv) != 4:
        print("Sample call: python ftserver <address> <port> <folder>")
        exit()

    clientsPort = sys.argv[2]
    clientsAddress = sys.argv[1]
    serversFolder = sys.argv[3]
    clientsAddress = clientsAddress + ":" + clientsPort

    context = zmq.Context()
    proxy = context.socket(zmq.REQ)
    proxy.connect("tcp://localhost:5555")

    clients = context.socket(zmq.REP)
    clients.bind("tcp://{}".format(clientsAddress))

    proxy.send_multipart([b"newServer", bytes(clientsAddress, "ascii")])
    m = proxy.recv()
    print(m)

    while True:
        print("Waitting for useres operations!!!")
        
        operation, *rest = clients.recv_multipart()
        if operation == b"upload":
            filename, byts, sha1byts, sha1complete = rest
            storeAs = serversFolder + sha1byts.decode("ascii")
            print("Storing {}".format(storeAs))
            with open(storeAs, "wb") as f:
                f.write(byts)
            print("Uploaded as {}".format(storeAs))
            clients.send(b"Done")

        elif operation == b"download":
            print("1")
            with open(serversFolder+rest[0].decode('ascii'),"rb") as InfoParts:            
                bt = InfoParts.read(partSize)
                clients.send(bt)
            #response = clients.recv()
            #print("Received reply for client {} ".format(response))
        else:
            print("2")
            print("Unsupported operation: {}".format(operation))
        #clients.send(b"Done")

if __name__ == '__main__':
    main()
