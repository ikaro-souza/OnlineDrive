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
        self.files_received = Queue()
        self.file_receiving_handler = Thread(target=self.handle_file_receiving)
        self.view = ClientView.View(self)
        self.user = dict()
        self.user_logged = False
        self.request = dict()
        self.server_response = str()

    def handle_server_response(self):
        while True:
            data = self.sock.recv(communication.BUFFSIZE)

            with self.view.lock:
                decoded_data = data.decode('UTF-8')

                try:
                    response = json.loads(decoded_data)

                    if response['message'] == 'RECV_FILES':
                        self.user_logged = True
                        self.server_response = 'Usuário logado com sucesso.'
                        self.sock.sendall(json.dumps({'message': 'CONFIRM'}).encode('utf-8'))
                    elif response['message'] == 'ALL_FILES':
                        self.server_response = 'Todos os arquivos foram enviados.'
                    elif response['message'] == 'NO_FILES':
                        self.server_response = 'Você não tem nenhum arquivo guardado.'
                    elif response['message'] == 'LOG_FAIL':
                        self.server_response = 'Usuário não cadastrado.'
                    elif response['message'] == 'REG_SUCCESS':
                        self.server_response = 'Usuário cadastrado com sucesso.'
                    elif response['message'] == 'REG_FAIL':
                        self.server_response = 'Usuário já existente.'
                    else:
                        self.server_response = response['message']
                except TypeError:
                    self.server_response = 'Recebendo arquivo...'
                    self.files_received.put(decoded_data.split(',', 2))

    def handle_file_receiving(self):
        while True:
            if self.files_received.empty() is False:
                file_name, file_data = self.files_received.get()
                print("File:", file_name)
                # with open(os.path.join('files_from_server', file_name), 'w') as f:
                #     f.write(file_data)

                self.files_received.task_done()

    def send_request(self, request: dict):
        self.sock.sendall(json.dumps(request).encode('utf-8'))

    def start(self):
        self.sock.connect(communication.SERVER_ADDRESS)
        self.server_response_handler.start()
        self.file_receiving_handler.start()
        self.view.start()


if __name__ == '__main__':
    c = ClientController()
    c.start()
