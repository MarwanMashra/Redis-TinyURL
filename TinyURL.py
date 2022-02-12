import hashlib, base64
import redis
from tkinter import *
from tkinter.font import Font

def center(win):
    """centers a tkinter window

    Args:
        win (obj): the main window or Toplevel window to center
    """

    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

class TinyURL():
    def __init__(self,host='localhost',port=6379):
        self.redis = self.make_server()
        if not self.redis:
            print(f"ERROR: Redis server is not running [{host=},{port=}]")
        else:
            self.run()

    def make_server(self):
        try:
            r = redis.Redis(host='localhost',port=6379)
            if r.ping():
                return r
            else:
                return None
        except:
            return None

    def get_hash(self,value):
        return base64.urlsafe_b64encode(hashlib.md5(value.encode('utf-8')).digest()).decode('utf-8')[:-2]

    def short_to_long(self,short):
        value = self.redis.get(short)
        if value:
            email, long = value.decode('utf-8').split()
            if email == self.email:
                return long

        print('URL not found')
        return None

    def long_to_short(self,long):
        value = f'{self.email} {long}'
        short = self.get_hash(value)
        self.redis.set(short,value)
        print(f"{long} => {short}")
        return short

    def set_text(self,text):
        self.text.set(text)

    def is_email(self,email):
        return email
    
    def login(self):
        email = self.input_email.get()
        if not self.is_email(email):
            self.set_text("Enter a valid email")
        else:
            if self.redis.get(email):
                self.email = email
                self.set_text("Connected")
            else:
                self.redis.set(email,0)
                self.email = email
                self.set_text("New user registered")

            self.input_email.destroy()
            self.button_login.destroy()
            self.label_email.destroy()

            self.button_logout = Button(self.app, text ="Logout", command = self.logout)
            self.button_logout.pack()

            self.add_url_section()

    def add_url_section(self):
        return

    def logout(self):
        self.email = None
        self.set_text("Signed out")
        self.button_logout.destroy()
        self.add_email_section()

    def add_email_section(self):
        self.label_email = Label(text="Email : ")
        
        self.label_email.pack(padx=(0,0), pady=(50,0), fill='both')

        self.input_email = Entry(self.app)
        self.input_email.pack(padx=(0,0), pady=(50,0), fill='both')

        self.button_login = Button(self.app, text ="Login", command = self.login)
        self.button_login.pack()

    def run(self):
        self.app = Tk()
        self.app.geometry("500x500")
        self.app.title("TinyURL")
        center(self.app)

        # create elements for first configuration (screen mode)
        self.text = StringVar()
        label = Label(self.app, textvariable=self.text)
        label.pack()

        self.add_email_section()
        


        mainloop()
