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
        self.sock.setblocking(False)
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
            data = self.sock.recv(communication.BUFFSIZE)
            response = json.loads(data.decode())

            if 'file_name' in response:
                # Recebe o nome do arquivo.
                print('Received file name. Preparing to receive file data.')
                self.recv_file_data(response['file_name'])
            else:
                if response == communication.RESULTS[0]:
                    print('response:', response['message'])

    def recv_file_data(self, file_name):
        # Recebe os dados do arquivo.
        with open(os.path.join('downloads', file_name), 'wb') as file:
            while True:
                print('Recebendo dados do arquivo.')
                data = self.sock.recv(communication.BUFFSIZE)
                file.write(data)

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