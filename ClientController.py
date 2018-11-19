import communication
import os
import json
import socket
from queue import Queue
from threading import Thread
import ClientView


class ClientController:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_response_handler = Thread(target=self.handle_server_response)
        self.view = ClientView.View(self)
        self.user = dict()
        self.user_logged = False
        self.request = dict()

    def handle_server_response(self):
        while True:
            data = self.sock.recv(communication.BUFFSIZE)

            with self.view.lock:
                decoded_data = data.decode('UTF-8')
                response = json.loads(decoded_data)

                if 'file_name' in response:
                    self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                    self.handle_file_receiving(response['file_name'])
                else:
                    if response['message'] == 'RECV_FILES':
                        self.view.server_response = 'Usuário logado com sucesso.'
                        self.user_logged = True
                        self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                    else:
                        if response['message'] == 'NO_FILES':
                            self.view.server_response = 'Usuário não possui arquivos no servidor.'
                        elif response['message'] == 'LOG_FAIL':
                            self.view.server_response = 'Usuário não cadastrado.'
                        elif response['message'] == 'REG_SUCCESS':
                            self.view.server_response = 'Usuário cadastrado com sucesso.'
                        elif response['message'] == 'REG_FAIL':
                            self.view.server_response = 'Usuário já existente.'
                        else:
                            self.view.server_response = response['message']

    def handle_file_receiving(self, file_name: str):
        print('Arquivo recebido \'{}\''.format(file_name))
        while True:
            total_data = bytes()

            while True:
                file_data = self.sock.recv(communication.BUFFSIZE)
                total_data += file_data

                if len(file_data) < communication.BUFFSIZE or not file_data:
                    self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                    break

            print('Dados recebidos \'{}\''.format(total_data))

    def send_request(self, request: dict):
        self.sock.sendall(json.dumps(request).encode('utf-8'))

    def start(self):
        self.sock.connect(communication.SERVER_ADDRESS)
        self.server_response_handler.start()
        self.view.start()


if __name__ == '__main__':
    c = ClientController()
    c.start()
