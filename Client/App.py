import json
import os
import socket
from json import JSONDecodeError
from threading import Thread
from tkinter import Tk
from tkinter import messagebox, BooleanVar, Frame
from Client.Views import LoginViewController
from ServerSide import communication


class App(Tk):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(communication.SERVER_ADDRESS)
        self.title('OnlineDrive - Welcome')
        # Informa à aplicação qual método chamar ao fechar.
        self.protocol('WM_DELETE_WINDOW', self.on_close)
        self.current_frame = Frame()
        self.user_logged = BooleanVar()
        self.user_logged.set(False)
        self.user_logged.trace('w', self.user_state_changed)
        # Inicia o thread que recebe dados do servidor.
        Thread(target=self.get_server_response).start()

    def run(self):
        self.current_frame = LoginViewController.Controller(self).view
        self.mainloop()

    def on_close(self):
        # Abre um pop-up para confirmar se o usuário realmente deseja fechar a aplicação
        if messagebox.askquestion('Quit', 'Você deseja mesmo sair?') == 'yes':
            # Manda uma mensagem para o servidor informando-o para desconectar o cliente
            self.sock.sendall(json.dumps({'action': communication.ACTIONS[2]}).encode())
            self.sock.close()
            # Fecha a aplicação
            self.destroy()

    def send_request(self, request: dict):
        serialized_request = json.dumps(request)
        Thread(target=self.sock.sendall, args=(serialized_request.encode(),)).start()

    def get_server_response(self):
        while True:
            total_data = bytes()

            while True:
                data_received = self.sock.recv(communication.BUFFSIZE)

                if not data_received or len(data_received) < communication.BUFFSIZE:
                    total_data += data_received
                    break

                total_data += data_received

            try:
                decoded_data = total_data.decode()
                response = json.loads(decoded_data)
                print('response:', response)

                if response['message'] == 'RECV_FILES':
                    self.user_logged.set(True)
                    self.sock.sendall('ok'.encode())
                    self.recv_files()

            except (UnicodeDecodeError or JSONDecodeError) as err:
                raise err

    def recv_files(self):
        while True:
            file_name = json.loads(self.sock.recv(communication.BUFFSIZE).decode())['file_name']

            with open(os.path.join('downloads', file_name), 'wb') as file:
                while True:
                    data = self.sock.recv(communication.BUFFSIZE)

                    if not data:
                        break

                    file.write(data)

                self.sock.sendall('ok'.encode())

    def user_state_changed(self, *args):
        if self.user_logged.get() is True:
            # Remove o frame atual da tela.
            for widget in self.slaves():
                widget.destroy()

            # Abre um pop-up que informa que o usuário está logado.
            messagebox.showinfo('UHUU', 'Você está logado')


if __name__ == '__main__':
    app = App()
    app.run()
