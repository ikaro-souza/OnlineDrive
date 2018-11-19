from tkinter import *
import ClientController


class LoginView(Frame):
    def __init__(self, root: Tk):
        super().__init__(master=root)
        self['padx'] = 2
        self['pady'] = 2
        self.pack(

        )
        self.username_label = Label(master=self, text='Username')
        self.username_label.grid(row=0, column=0)
        self.username_entry = Entry(master=self)
        self.username_entry.grid(row=0, column=1)
        self.pass_label = Label(master=self, text='Password')
        self.pass_label.grid(row=1, column=0)
        self.pass_entry = Entry(master=self, show='*')
        self.pass_entry.grid(row=1, column=1)

if __name__ == '__main__':
    root = Tk()
    v = LoginView(root)
    root.mainloop()

