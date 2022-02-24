import socket
import sys

out_filename = r"D:\IITH\Networks\comp"
#out_filename = r"D:\IITH\Networks\out.txt"

ofile = open(out_filename, "wb")

MSS = 33000
S_PORT = 5051
S_IP = "192.168.116.110"
ADDR = (S_IP, S_PORT)
FORMAT = 'utf-8'

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((S_IP,S_PORT))

R_IP = '192.168.116.110'
R_PORT = 10001

clt_send_addr = (R_IP,R_PORT)

print ("Server is listening!!!!")

FIN = 0
expected_seqnum = 0
buffer = {}

while FIN!=1:
    # send a thank you message to the client. encoding to send byte type.
    ack = server.recvfrom(MSS)
    rec_mes = ack[0].split(b';', 3)
    SYN = ack[0].split(b';')[0]
    SYN = int(SYN)
    print(SYN)
    FIN = ack[0].split(b';')[1]
    FIN = int(FIN)
    print(FIN)
    seqnum = ack[0].split(b';')[2]
    seqnum = int(seqnum)
    print(seqnum)
    if FIN == 0 and SYN == 0:
        # if expected_seqnum == seqnum:
        #     if data == None:
        #         data = ack[0].decode('utf-8').split(';')[3]
        #     else:
        #         data += ack[0].decode('utf-8').split(';')[3]
        #     expected_seqnum += 1
        # else:
        buffer[seqnum] = b""
        buffer[seqnum] = buffer[seqnum].join(rec_mes[3:])
        # buffer[seqnum] = b""
        # data = ack[0].split(b';')[3:]
        # for i in range(0, len(data)):
        #     buffer[seqnum] += data[i]
        #     if i != len(data) - 1:
        #         buffer[seqnum] += b';'
        #buffer[seqnum] = ack[0].split(b':')[3]
        #print(buffer[seqnum])
        send_syn = (str(0)+";").encode()
        send_fin = (str(0)+";").encode()
        send_seqnum = str(seqnum).encode()
        send_ack = send_syn+send_fin+send_seqnum
        server.sendto(send_ack, clt_send_addr)

    else:
        print(ack[0])
        server.sendto(ack[0],clt_send_addr)

ordered_seq = sorted(buffer.keys())

for seq in ordered_seq:
    ofile.write(buffer[seq])

print("server is sleeping")
server.close()
ofile.close()

