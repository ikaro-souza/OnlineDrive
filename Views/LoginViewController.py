from App import App
from Views.LoginView import LoginView


class Controller:
    def __init__(self, app: App):
        # Referencia a view pela qual este controlador é responsável
        self.view = LoginView(self, app)
        self.app = app

    def username_var_changed(self, *args):
        username = self.view.username.get()
        password = self.view.password.get()

        # Desbloqueia a entry da senha somente se o usuário digitar algo na entry do nome de usuário
        if username != '':
            self.view.pass_entry['state'] = 'normal'
            # Desbloqueia o botão somente se o nome de usuário e senha tiverem pelo menos 8 caracteres
            self.view.submit_button['state'] = 'normal' if len(username) >= 8 and len(password) >= 8 else 'disabled'

    def password_var_changed(self, *args):
        username = self.view.username.get()
        password = self.view.password.get()

        # Desbloqueia o botão somente se o nome de usuário e senha tiverem pelo menos 8 caracteres
        if password != '':
            self.view.submit_button['state'] = 'normal' if len(username) >= 8 and len(password) >= 8 else 'disabled'

    def submit(self):
        request = {
            'user': {'user_name': self.view.username.get(), 'pass': self.view.password.get()},
            'action': self.view.action.get()
        }

        self.app.send_request(request)