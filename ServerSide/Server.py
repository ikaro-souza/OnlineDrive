import json
import os
import socket
from queue import Queue
from threading import Thread, current_thread, Lock
from ServerSide import communication


class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users_database_access_lock = Lock()
        self.file_transfer_requests = Queue()

    def setup_socket(self):
        self.sock.bind(communication.SERVER_ADDRESS)
        self.sock.listen(30)

    def start_server(self):
        self.setup_socket()

        while True:
            print('Main-Thread: Aguardando conexão...\n')
            conn, addr = self.sock.accept()
            connection_handler = Thread(target=self.handle_connection, args=(conn,))
            connection_handler.start()

    def handle_connection(self, client_connection: socket.socket):
        thread_name = current_thread().name
        print('\t\t{}: conectado à {}\n'.format(thread_name, client_connection.getsockname()))

        while True:
            data = client_connection.recv(communication.BUFFSIZE)
            decrypted_data = self.decrypt(data)
            request = json.loads(decrypted_data.decode())

            if request['action'] == communication.ACTIONS[0]:
                print('\t\t{}: {} quer se logar.\n'.format(thread_name, request['user']['user_name']))
                res = self.authenticate_login(request['user'])

                if res == communication.RESULTS[0]:
                    client_connection.sendall(json.dumps({'message': res}).encode())
                    self.send_user_files(request['user']['user_name'], client_connection)
                else:
                    client_connection.sendall(json.dumps({'message': res}).encode())

            elif request['action'] == communication.ACTIONS[1]:
                print('\t\t{}: {} quer se cadastrar.\n'.format(thread_name, request['user']['user_name']))
                res = self.register(request['user'])
                client_connection.sendall(json.dumps({'message': res}).encode())

            elif request['action'] == communication.ACTIONS[2]:
                client_connection.close()
                print('\t\t{}: Usuário desconectou.\n'.format(thread_name))
                break

            # elif request['action'] == communication.ACTIONS[2]:
            #     self.update_user_dir(request['user']['user_name'])

    def authenticate_login(self, user: dict):
        thread_name = current_thread().name
        
        with self.users_database_access_lock:
            print('\t\t{}: Autenticando login de {}\n'.format(thread_name, user['user_name']))
            registered_users = self.get_registered_users()
            return communication.RESULTS[0] if user in registered_users else communication.RESULTS[1]

    def register(self, user: dict):
        thread_name = current_thread().name
        with self.users_database_access_lock:
            print('\t\t{}: Registrando {}\n'.format(thread_name, user['user_name']))
            registered_users = self.get_registered_users()
            print('\t\t{}: Acesso feito ao banco de dados de usuários.\n'.format(thread_name))

            for registered_user in registered_users:
                if user['user_name'] == registered_user['user_name']:
                    print('\t\t{}: {} já existe.\n'.format(thread_name, user['user_name']))
                    return communication.RESULTS[3]

            with open('registered_users.json', 'w') as f:
                print('\t\t{}: Atualizando ao banco de dados de usuários.\n'.format(thread_name))

                registered_users.append(user)
                json.dump(registered_users, f, indent=2)
                f.close()

                print('\t\t{}: Usuário registrado.\n'.format(thread_name))

                self.create_user_dir(user['user_name'])
                return communication.RESULTS[2]

    def update_user_dir(self, user_name: str):
        pass

    def create_user_dir(self, user_name: str):
        thread_name = current_thread().name
        print('\t\t{}: Cirando diretório do usuário {}.\n'.format(thread_name, user_name))
        user_dir_path = self.get_user_dir(user_name)
        os.makedirs(user_dir_path)
        print('\t\t{}: Diretório criado.\n'.format(thread_name))

    def send_user_files(self, user_name: str, connection: socket.socket):
        thread_name = current_thread().name
        print('\t\t{}: Checking files for {}'.format(thread_name, connection.getsockname()))

        user_dir = self.get_user_dir(user_name)

        for root, dirs, files in os.walk(user_dir):
            if not files:
                print('\t\t{}: No files to send.'.format(thread_name))
                connection.sendall(json.dumps({'message': communication.RESULTS[6]}).encode())
            else:
                print('\t\t{}: Sending files.'.format(thread_name))
                for file_name in files:

                    # Envia o nome do arquivo
                    print('\t\t{}: Sending file name.'.format(thread_name))
                    connection.sendall(json.dumps({'file_name': file_name}).encode())

                    # Envia os dados do arquivo
                    with open(os.path.join(user_dir, file_name), 'rb') as file:
                        print('\t\t{}: Sending file data.'.format(thread_name))
                        file_data = file.read(communication.BUFFSIZE)

                        while file_data:
                            connection.sendall(file_data)
                            file_data = file.read(communication.BUFFSIZE)

    @staticmethod
    def encrypt(data: bytes):
        return data

    @staticmethod
    def decrypt(data: bytes):
        return data

    @staticmethod
    def get_registered_users():
        """
            Tenta abrir o arquivo em modo de leitura, caso não consiga, o arquivo com uma lista vazia.
            Retorna uma lista vazia ou com os usuários cadastrados.
        """
        thread_name = current_thread().name
        print('\t\t{}: Acessando banco de dados de usuários.\n'.format(thread_name))
        try:
            with open('registered_users.json') as file:
                users = json.load(file)
                file.close()
                print('\t\t{}: Retornando lista de usuários...\n'.format(thread_name))
                return users
        except FileNotFoundError:
            print('\t\t{}: Banco de dados não existe, criando banco...\n'.format(thread_name))
            with open('registered_users.json', 'w') as file:
                json.dump([], file)
                file.close()
                print('\t\t{}: Banco criado.\n'.format(thread_name))
            return []

    @staticmethod
    def get_user_dir(user_name: str):
        return os.path.join('users_data', user_name)


if __name__ == '__main__':
    s = Server()
    s.start_server()
