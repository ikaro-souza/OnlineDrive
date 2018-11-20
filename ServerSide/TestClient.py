import json
import socket

from ServerSide import communication


class Client:
    def __init__(self, name):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.server_response = str()

    def test(self, request: dict):
        self.connect()
        self.send_request(request)
        self.show_server_response()

    def connect(self):
        self.sock.connect(communication.SERVER_ADDRESS)

    def send_request(self, request: dict):
        print('{}: Eviando \'{}\''.format(self.name, request))
        self.sock.sendall(json.dumps(request).encode('utf-8'))

    def show_server_response(self):
        while True:
            data = self.sock.recv(communication.BUFFSIZE)
            decoded_data = data.decode('UTF-8')
            response = json.loads(decoded_data)

            if 'file_name' in response:
                print('{}: Recebeu arquivo {}'.format(self.name, response['file_name']))
                self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                self.receive_files(response['file_name'])
            else:
                if response['message'] == 'RECV_FILES':
                    self.server_response = 'Usuário logado com sucesso.'
                    self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                else:
                    if response['message'] == 'NO_FILES':
                        self.server_response = 'Usuário não possui arquivos no servidor.'
                    elif response['message'] == 'LOG_FAIL':
                        self.server_response = 'Usuário não cadastrado.'
                    elif response['message'] == 'REG_SUCCESS':
                        self.server_response = 'Usuário cadastrado com sucesso.'
                    elif response['message'] == 'REG_FAIL':
                        self.server_response = 'Usuário já existente.'
                    else:
                        self.server_response = response['message']
                    break

        print('{}: Servidor diz \'{}\''.format(self.name, self.server_response))
        self.sock.sendall(json.dumps({'action': communication.ACTIONS[2]}).encode('utf-8'))

    def receive_files(self, file_name: str):
        total_data = bytes()

        while True:
            file_data = self.sock.recv(communication.BUFFSIZE)
            total_data += file_data

            if len(file_data) < communication.BUFFSIZE or not file_data:
                self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                break

        print('{}: Dados recebidos \'{}\''.format(self.name, total_data))