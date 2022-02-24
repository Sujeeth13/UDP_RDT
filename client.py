import socket
import threading
import time
import sys


def packetseg(i_filename,MSS):
    ifile = open(i_filename, 'rb')

    seqcount = 0
    SYN = (str(0) + ";").encode()
    FIN = (str(0) + ";").encode()
    seqnum = (str(seqcount) + ";").encode()
    header_size = sys.getsizeof(SYN+FIN+seqnum)

    data = []
    byte = ifile.read(MSS)
    #byte = ifile.read(1)
    while byte:
        seqcount += 1
        SYN = (str(0)+";").encode()
        FIN = (str(0)+";").encode()
        seqnum = (str(seqcount)+";").encode()
        data.append(SYN+FIN+seqnum+byte)
        byte = ifile.read(MSS)
        #byte = ifile.read(1)
    ifile.close()
    return data

def send(data,N,r_addr):
    global ACK
    global lock
    base = 0
    nextseq = 0
    datasize = len(data)
    recv = threading.Thread(target=recieve,args=(datasize,r))
    recv.start()
    threads = {}
    while nextseq != datasize:
        while nextseq < base + N and nextseq != datasize:
            pkt = data[nextseq]
            #send packets using threads to improve speed
            lock.acquire()
            s.sendto(pkt,r_addr)
            lock.release()
            ACK[nextseq+1] = False

            threads[nextseq+1] = threading.Thread(target=timer,args=(pkt,r_addr,nextseq+1,N,RTO))
            threads[nextseq+1].start()
            nextseq += 1
        while not ACK[base+1] and nextseq!=datasize:
            pass
        #ACK.pop(base+1)
        threads[base+1].join()
        base += 1
        # while ACK[base+1] and nextseq!=datasize and base < nextseq:
        #     ACK.pop(base+1)
        #     base += 1
        temp = nextseq - 1
        for i in range(base, nextseq):
            if not ACK[i+1]:
                temp = i
                break
            #ACK.pop(i+1)
        base = temp
    recv.join()
    return

def timer(pkt,addr,seqnum,N,RTO):
    global ACK
    global lock
    while True:
        start = time.time()
        #start = curr
        while time.time() - start < RTO:
            if ACK[seqnum]:
                print("Thread exit")
                return
        lock.acquire()
        print('resending pkt')
        s.sendto(pkt,addr)
        lock.release()
    return

def all_ack(ACK):
    for val in ACK.keys():
        if not ACK[val]:
            return False
    return True

def recieve(datasize,r):
    global ACK
    global lock
    FIN  = 0
    seqnum = 0
    while seqnum != datasize:
        pkt = r.recvfrom(MSS)
        print("ack from server")
        SYN,FIN,seqnum = pkt[0].split(b';')
        FIN = int(FIN)
        seqnum = int(seqnum)
        #check if the ack is within or lower than the window
        # if(seqnum < max(ACK.keys())):
        ACK[seqnum] = True

    print('end of recieve')
    return


connection = False

def sendSYN(s,r,r_addr):
    global connection
    SYN = (str(1)+";").encode()
    FIN = (str(0)+";").encode()
    seqnum = (str(0)).encode()
    conn_pkt = SYN+FIN+seqnum
    t = threading.Thread(target=recvSYN,args=(r,))
    t.start()
    s.sendto(conn_pkt, r_addr)
    while not connection :
        print(conn_pkt)
        start = time.time()
        while time.time() - start < RTO:
                if connection:
                    break
        if not connection:
            s.sendto(conn_pkt,r_addr)
    print("ending sendSYN")
    return

def recvSYN(r):
    global connection
    SYN = 0
    while SYN!=1:
        pkt = r.recvfrom(MSS)
        SYN,FIN,seqnum = pkt[0].decode().split(";")
        SYN = int(SYN)
    print("Connection established from server")
    connection = True
    return

def recvFIN(r):
    global connection
    FIN = 0
    while FIN!=1:
        pkt = r.recvfrom(MSS)
        SYN,FIN,seqnum = pkt[0].decode().split(";")
        FIN = int(FIN)
    r.close()
    print("Connection closed from server")
    connection = False
    return

def close_conn(s,r,r_addr):
    SYN = (str(0) + ";").encode()
    FIN = (str(1) + ";").encode()
    seqnum = (str(0)).encode()
    close_pkt = SYN + FIN + seqnum
    t = threading.Thread(target=recvFIN, args=(r,))
    t.start()
    s.sendto(close_pkt, r_addr)
    while connection :
        print(close_pkt)
        start = time.time()
        while time.time() - start < RTO:
                if not connection:
                    break
        if connection:
            s.sendto(close_pkt,r_addr)
    s.close()
    print("ending close_conn")
    return

MSS = 4096
N = 100
RTO = 0.0005
FORMAT = 'utf-8'

inp_filename = r"C:\Users\sujee\Downloads\CS3543_100MB"
#inp_filename = r"D:\IITH\Networks\inp.txt"

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the port on which you want to connect
S_IP = '192.168.116.110'
S_PORT = 5051

#the port on which the client receives ack from the server
R_IP = '192.168.116.110'
R_PORT = 10001

r_addr = (S_IP,S_PORT)  #the server address

# connect to the server on local computer
s.connect((S_IP, S_PORT))

r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
r.bind((R_IP, R_PORT))

ACK = {}
lock = threading.Lock()

data = packetseg(inp_filename,MSS)
sendSYN(s,r,r_addr)
send(data,N,r_addr)
close_conn(s,r,r_addr)
