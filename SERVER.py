import sys
import socket
import threading
def server_loop(localhost,localport,remotehost,remoteport,receivefirst):
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    try:
        server.bind((localhost,localport))
    except:
        print("Please connect correctly!")
        sys.exit(0)
    print("listening on %s:%d"%(localhost,localport))
    server.listen(5)
    while True:
        s,addr=server.accept()
        print("Receiving from%s:%d"%(addr[0],addr[1]))
        proxy_thread=threading.Thread(target=proxyhandler,
                    args=(clientsocket,remotehost,remoteport,receivefirst))
        proxy_thread.start()

def proxyhandler(clientsocket,remotehost,remoteport,receivefirst):
    remotehost=socket.gethostname()
    remoteport=80
    remotesocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    remotesocket.bind((remotehost,remoteport))
    if receivefirst:
        remotebuffer=receivefrom(remotesocket)
        hexdump(remotebuffer)
        remotebuffer=responsehandler(remotebuffer)
        if len(remotebuffer):
            print("Sending %data bytes to localhost."%len(remotebuffer))
            clientsocket.send(remotebuffer)
    while True:
        lacalbuffer=receivefrom(clientsocket)
        if len(localbuffer):
            print("Receiving %d bytes from localhost"%len(localbuffer))
            hexdump(localbuffer)
            localbuffer=requesthandler(localbuffer)
            remmotesocket.send(localbuffer)
            print("Send to remote.")
        remotebuffer=receivefrom(remotesocket)
        if len(remotebuffer):
            print("Receiving %d bytes from localhost"%len(remotebuffer))
            hexdump(remotebuffer)
            remotebuffer=requesthandler(remotebuffer)
            clientsocket.send(remotebuffer)
            print("Send to localhost.")
        if not len(localbuffer) or not len(remotebuffer):
            clientsocket.close()
            remotesocket.close()
            print("No data.Closing connections")
            break
def requesthandler(buffer):
    return buffer

def responsehandler(buffer):
    return buffer
            
def hexdump(src,length=16):
    result=[]
    digits=4 if isinstance(src,unicode) else 2#判断src是否为unicode类型；
    for i in range(0,len(src),length):
        s=src[i:i+length]#构建字典;
        hexa=b''.join(["%0*X"%(digits,ord(x)) for x in s])
        text=b''.join([x if 0x20<=ord(x)<0x0f else b'.' for x in s])
    print(b'\n'.join(result))
    
def receivefrom(connection):
    buffer=""
    connection.settimeout(2)
    try:
        while True:
            data=connection.recv(4096)
            if not data:
                break
            buffer+=data
    except:
        pass
    return buffer
def main():
    localhost=socket.gethostname()
    localport=80
    
    remotehost=socket.gethostname()
    remoteport=80

    receivefirst="True"

    if "True" in receivefirst:
        receicefirst=True
    else:
        receivefirst=False
    server_loop(localhost,localport,remotehost,remoteport,receivefirst)

if __name__=="__main__":
    main()
    
            
