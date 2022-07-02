import configparser
import os
import socket
import requests

current_dir = os.getcwd()
config = configparser.ConfigParser()
config.read(current_dir + '/varac_cloudlog_uploader.ini')

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('0.0.0.0', 52001)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(512)
            print('received {!r}'.format(data))
            if data:
                adif = data.decode('utf-8')
                adif = adif[adif.find("<ExternalLogADIF"):]
                adif = adif[adif.find(">") + 1:]

                adif = adif.replace("<mode:4>VARA", "<mode:7>DYNAMIC<submode:7>VARA HF")

                print("ADIF:", adif)

                json_string = {"key":config['DEFAULT']['api'], "station_profile_id":config['DEFAULT']['station_profile_id'], "type":"adif", "string":adif}

                response = requests.post(config['DEFAULT']['url'], json=json_string)
                response.json()
                if response.status_code == 201:
                    print('Data transfered')
                else:
                    print('POST-Error: {}'.format(response.status_code))
            else:
                print('no data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()