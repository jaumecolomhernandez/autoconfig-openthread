import sys, socket, time, yaml
import multiprocessing

if len(sys.argv)>1:
  mes = sys.argv[1]
else:
  mes = "example"

remote = '147.83.39.50'
local = 'localhost'

def decode_msg(msg):
  args = msg.split('|')
  print(f"Decoded message -> Header: '{args[1]}' Payload: '{args[2]}'")
  return args[1], args[2]

def run():
  while(True):
    response = str(sock.recv(2048), 'ascii')
    print("Received: {}".format(response), end = "\n")
    headers, payload = decode_msg(response)
    time.sleep(0.1)
    if 'C' in headers:
      print(f"Sent ACK to ({remote},12342)")
      send("ACK")
    time.sleep(0.1)

def send(command):
  sock.sendall(bytes(command, 'ascii'))

if __name__ == '__main__':
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.connect((local, 12342))
  sock.sendall(bytes(mes, 'ascii'))

  server_thread = multiprocessing.Process(target = run)
  server_thread.start()

