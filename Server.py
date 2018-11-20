import socket
import json
import os
import communication
from queue import Queue
from threading import Thread, current_thread, local, Lock


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
            request = json.loads(decrypted_data.decode('utf-8'))

            if request['action'] == communication.ACTIONS[0]:
                print('\t\t{}: {} quer se logar.\n'.format(thread_name, request['user']['user_name']))
                res = self.authenticate_login(request['user'])

                if res == 'LOG_SUCCESS':
                    self.send_user_files(request['user']['user_name'], client_connection)
                else:
                    client_connection.sendall(json.dumps({'message': res}).encode('utf-8'))

            elif request['action'] == communication.ACTIONS[1]:
                print('\t\t{}: {} quer se cadastrar.\n'.format(thread_name, request['user']['user_name']))
                res = self.register(request['user'])
                client_connection.sendall(json.dumps({'message': res}).encode('utf-8'))

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
            return 'LOG_SUCCESS' if user in registered_users else 'LOG_FAIL'

    def register(self, user: dict):
        thread_name = current_thread().name
        with self.users_database_access_lock:
            print('\t\t{}: Registrando {}\n'.format(thread_name, user['user_name']))
            registered_users = self.get_registered_users()
            print('\t\t{}: Acesso feito ao banco de dados de usuários.\n'.format(thread_name))

            for registered_user in registered_users:
                if user['user_name'] == registered_user['user_name']:
                    print('\t\t{}: {} já existe.\n'.format(thread_name, user['user_name']))
                    return 'REG_FAIL'

            with open('registered_users.json', 'w') as f:
                print('\t\t{}: Atualizando ao banco de dados de usuários.\n'.format(thread_name))
                registered_users.append(user)
                json.dump(registered_users, f, indent=2)
                f.close()
                print('\t\t{}: Usuário registrado.\n'.format(thread_name))
                self.create_user_dir(user['user_name'])

                return 'REG_SUCCESS'

    def update_user_dir(self, user_name: str):
        pass

    def create_user_dir(self, user_name: str):
        thread_name = current_thread().name
        print('\t\t{}: Cirando diretório do usuário {}.\n'.format(thread_name, user_name))
        user_dir_path = self.get_user_dir(user_name)
        os.makedirs(user_dir_path)
        print('\t\t{}: Diretório criado.\n'.format(thread_name))

    def send_user_files(self, user_name: str, connection: socket.socket):
        user_dir = self.get_user_dir(user_name)
        thread_name = current_thread().name

        try:
            for root, dirs, files in os.walk(user_dir):
                print('\t\t{}: Informando ao cliente sobre que o servidor irá enviar seus arquivos...\n'.format(
                    thread_name
                ))

                res = connection.sendall(json.dumps({'message': 'RECV_FILES'}).encode('utf-8'))

                print('\t\t{}: Aguardando confirmação do cliente...\n'.format(thread_name))
                connection.recv(communication.BUFFSIZE)

                if files:
                    file_names = []
                    for file_name in files:
                        file_names.append(file_name)

                        # print('\t\t{}: Preparando arquivo para envio...\n'.format(thread_name))
                        #
                        # file_path = os.path.join(root, file_name)
                        #
                        # file_data = bytes()
                        #
                        # with open(file_path, 'rb') as f:
                        #     data_read = f.read(4096)
                        #
                        #     while data_read:
                        #         file_data += data_read
                        #         data_read = f.read(4096)
                        #
                        #     f.close()
                        #
                        # print('\t\t{}: Enviando nome do arquivo...\n'.format(thread_name))
                        # connection.sendall(json.dumps({'file_name': file_name}).encode('utf-8'))
                        #
                        # print('\t\t{}: Aguardando confirmação...\n'.format(thread_name))
                        # connection.recv(communication.BUFFSIZE)
                        #
                        # print('\t\t{}: Enviando os dados do arquivos...\n'.format(thread_name))
                        # connection.sendall(file_data)
                        #
                        # print('\t\t{}: Aguardando confirmação...\n'.format(thread_name))
                        # connection.recv(communication.BUFFSIZE)

                    res = connection.sendall(json.dumps(file_names).encode('utf-8'))
                    if res is None:
                        print('\t\t{}: Arquivos enviados.\n'.format(thread_name))
                        res = 'ALL_SENT'
                else:
                    print('\t\t{}: O usuário não possui nenhum arquivo no servidor.\n'.format(thread_name))
                    res = 'NO_FILES'

                connection.sendall(json.dumps({'message': res}).encode('utf-8'))
        except Exception as err:
            print(err)
            connection.sendall(json.dumps({'message': str(err)}).encode('utf-8'))

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
