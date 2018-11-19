import time
from threading import Thread, Lock
import ClientController
import communication
from re import match


class View(Thread):
    def __init__(self, controller: ClientController):
        Thread.__init__(self)
        self.controller = controller
        self.lock = Lock()

    def run(self):
        print(' BEM-VINDO '.center(100, '*'))
        print('\n')
        self.show_login_view()
        self.show_main_view()

    def show_main_view(self):
        print(' SEUS ARQUIVOS '.center(100, '*'))

    def show_login_view(self):
        while self.controller.user_logged is False:
            action = self.get_action()
            self.show_requirements()
            user_name = self.get_username()
            request = {}

            if action == communication.ACTIONS[2]:
                request['user'] = {'user_name': user_name}
                request['action'] = action
            else:
                password = self.get_password()
                request['user'] = {'user_name': user_name, 'pass': password}

            self.controller.send_request()
            while self.lock.locked():
                time.sleep(0.01)

            print('\nServidor diz:', self.controller.server_response)
            print(60*'-')

    def get_action(self):
        print('+{}+'.format(' Escolha a ação '.center(58, '-')))
        print('| {:56} |'.format('1. Login'))
        print('| {:56} |'.format('2. Registrar'))
        print('| {:56} |'.format('3. Sair'))
        print('+{}+'.format(58*'-'))
        choice = int(input('Escolha: '))

        if 1 <= choice <= 3:
            return communication.ACTIONS[choice]
        else:
            print('\n{}\n'.format(' Escolha inválida '.center(30, '*')))
            return self.get_action()

    def get_username(self):
        user_name = input("Usuário: ")

        if len(user_name) >= 6:
            return user_name
        else:
            print('\n{}\n'.format(' Nome de usuário inválido '.center(30, '*')))
            return self.get_username()

    def get_password(self):
        password = input("Senha: ")

        if match(r'^(?=.*\d).{6,}$', password):
            return password
        else:
            print('\n{}\n'.format(' Senha inválida '.center(30, '*')))
            return self.get_password()

    @staticmethod
    def show_options_list(options):
        print('+{}+'.format(58*'-'))
        for i in range(len(options)):
            print('| {]. {}'.format(i+1, options[0]))
        print('+{}+'.format(58 * '-'))

    @staticmethod
    def show_requirements():
        print('\n+----{:-<54}+'.format('REQUISITOS'))
        print('| {:56} |'.format('Nome de usuário deve conter pelo menos 6 caracteres.'))
        print('| {:56} |'.format('O tamanho mínimo da senha é 6.'))
        print('| {:56} |'.format('A senha deve conter pelo menos 1 número.'))
        print('+{:58}+\n'.format(58 * '-'))


if __name__ == '__main__':
    c = View(Thread())
    c.start()
