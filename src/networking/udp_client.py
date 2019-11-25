import sys, socket, time, yaml
import multiprocessing

if len(sys.argv)>1:
  mes = sys.argv[1]
else:
  mes = "example"
  
def run():
  while(True):
    response = str(sock.recv(2048), 'ascii')
    print("Received: {}".format(response), end = "\n")
    time.sleep(0.1)
    if response[0:2] == 'C|':
      send("ACK")
    time.sleep(0.1)

def send(command):
  sock.sendall(bytes(command, 'ascii'))

if __name__ == '__main__':
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.connect(('localhost', 12342))
  sock.sendall(bytes(mes, 'ascii'))

  server_thread = multiprocessing.Process(target = run)
  server_thread.start()

