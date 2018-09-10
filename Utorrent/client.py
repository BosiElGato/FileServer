import zmq
import sys
import hashlib

partSize = 1024 * 1024 * 10

context = zmq.Context()
proxy = context.socket(zmq.REQ)
proxy.connect("tcp://localhost:6666")

def uploadFile2(filename, socket):
    with open(filename, "rb") as f:
        finished = False
        part = 0
        while not finished:
            print("Uploading part {}".format(part))
            f.seek(part*partSize)
            bt = f.read(partSize)
            socket.send_multipart([filename, bt])
            response = socket.recv()
            print("Received reply  [%s ]" % (response))
            part = part + 1
            if len(bt) < partSize:
                finished = True

def computeHashFile(filename):
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    sha1 = hashlib.sha1()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def computeHash(bytes):
    sha1 = hashlib.sha1()
    sha1.update(bytes)
    return sha1.hexdigest()

def uploadFile(context, filename, servers):
    sockets = []

    InfoServers = open("InfoServers.txt","w+")

    for ad in servers:
        s = context.socket(zmq.REQ)
        s.connect("tcp://"+ ad.decode("ascii"))
        sockets.append(s)

    sha1complete = 0

    with open(filename, "rb") as f:
        completeSha1= bytes(computeHashFile(filename), "ascii")

        if sha1complete ==0:
            InfoServers.write(filename.decode('ascii')+"\n")
            InfoServers.write(completeSha1.decode('ascii')+"\n")
            sha1complete = 1

        finished = False
        part = 0
        while not finished:
            print("Uploading part {}".format(part))
            f.seek(part*partSize)
            bt = f.read(partSize)
            sha1bt = bytes(computeHash(bt), "ascii")
            s = sockets[part % len(sockets)]
            s.send_multipart([b"upload", filename, bt, sha1bt, completeSha1])
            response = s.recv()
            print("Received reply for part {} ".format(part))
            

            InfoServers.write(sha1bt.decode('ascii')+"\n")
            InfoServers.write(servers[part%len(sockets)].decode('ascii')+"\n")
            part = part + 1

            if len(bt) < partSize:
                finished = True
        InfoServers.close()
        Hash1Info = bytes(computeHashFile("InfoServers.txt"),'ascii')
        with open("InfoServers.txt","rb") as InfoParts:            
            bt = InfoParts.read(partSize)
            s = sockets[part % len(sockets)]
            s.send_multipart([b"upload", b"InfoServers.txt", bt, Hash1Info, completeSha1])
            response = s.recv()
            print("Received reply for part {} ".format(part))

        #InfoServers.write(str(servers[part%len(sockets)])+"\n")
        locationInfo =servers[part%len(sockets)]
        proxy.send_multipart([bytes("UploadedFile",'ascii'),Hash1Info,locationInfo])
        RespuestaProxy = proxy.recv()
        print(RespuestaProxy)

        with open("UploadedFiles.txt", "a") as UF:
            UF.write(Hash1Info.decode('ascii')+" "+filename.decode('ascii')+"\n")
         #opens file with name of "test.txt"
        #print(InfoParts.read())


def main():
    if len(sys.argv) != 4:
        print("Sample call: python ftclient <username> <operation> <filenameOrKey>")
        exit()


    username = sys.argv[1]
    operation = sys.argv[2]
    filename = sys.argv[3].encode('ascii')

       

    print("Operation: {}".format(operation))

    if operation == "upload":
        proxy.send_multipart([bytes("AvailableServersForUpload", 'ascii')])
        servers = proxy.recv_multipart()        
        print("There are {} available servers".format(len(servers)))        
        uploadFile(context, filename, servers)        
        print("File {} was uploaded.".format(filename))

    elif operation == "download":
        proxy.send_multipart([bytes("Download", 'ascii'), filename])
        #servers = proxy.recv_multipart()
        #print(filename.decode('ascii'))
        server = proxy.recv()
        if server.decode('ascii') == "Archivo No existe":
            print(server.decode('ascii'))
        else:
            server = server.decode('ascii').split("\n")
            print(server[0])
            #print("Archivo existe, servidor "+ server.decode('ascii'))
            s = context.socket(zmq.REQ)
            s.connect("tcp://"+ server[0])
            s.send_multipart([b"download",filename])
            infofiles = s.recv()

            with open(filename.decode('ascii')+".txt","wb")  as f:
                f.write(infofiles)
            f = open(filename.decode('ascii')+".txt","r") #opens file with name of "test.txt"
            myList = []
            for line in f:
                myList.append(line.rstrip())

            with open("copy-"+myList[0],"wb") as fdown:
                for pos in range (len(myList)-1):
                    if pos >1:
                        if pos%2 == 0:
                            s = context.socket(zmq.REQ)
                            s.connect("tcp://"+myList[pos+1])
                            s.send_multipart([b"download",bytes(myList[pos],'ascii')])
                            print("16")
                            respSer = s.recv()
                            print("17")
                            #s.send("Received")
                            fdown.write(respSer)
                            print("18")
                print("downloaded  as {}".format("copy-"+myList[0]))

    elif operation == "share":
        print("Not implemented yet")
    else:
        print("Operation not found!!!")

if __name__ == '__main__':
    main()
