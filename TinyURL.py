import hashlib, base64
import redis
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
import re
from tabulate import tabulate
from ttkthemes import ThemedTk, ThemedStyle

EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
STATS_FILE = "stats.txt"
STYLE = "yaru"

def print_color(text,color):
    if color=="green":
        header = '\033[92m'
    elif color=="red":
        header = '\033[91m'
    elif color=="yellow":
        header = '\033[93m'
    end = '\033[0m'

    print(header + text + end)


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
        self.redis = self.make_server(host,port)
        if not self.redis:
            print_color(f"Redis server is not running on [{host=},{port=}]","red")
        else:
            print_color(f"Connected to Redis server on [{host=},{port=}]","green")
            self.run()

    def make_server(self,host,port):
        try:
            r = redis.Redis(host,port)
            if r.ping():
                return r
            else:
                return None
        except:
            return None

    def get_hash(self,value):
        return base64.urlsafe_b64encode(hashlib.md5((self.email+value).encode('utf-8')).digest()).decode('utf-8')[:-2]

    def short_to_long(self,short):
        long = self.redis.hget(self.email,short)
        if long:
            cpt, url = long.decode('utf-8').split()
            self.redis.hset(self.email, short, f"{int(cpt)+1} {url}")
            return url
        return None

    def long_to_short(self,long):
        short = self.get_hash(long)
        self.redis.hsetnx(self.email, short, f"{1} {long}")
        return short

    def get_stats(self):
        stats = self.redis.hgetall(self.email)
        output = ""
        output+= f"email: {self.email}\n"
        output+= f"number of logins: {len(stats)-1}\n"
        list_tuples = []
        for short, long in stats.items():
            short = short.decode('utf-8')
            if short =="__logins__": 
                output+= f"number of URLs: {long.decode('utf-8')}\n"
            else:
                cpt, url = long.decode('utf-8').split()
                list_tuples.append((url,short,cpt))
        
        output+= tabulate(list_tuples, headers= ["Long URL","Short URL","Requests"],tablefmt='fancy_grid')
        return output

    def dump_stats(self):
        stats = self.get_stats()
        print(stats)
        logs = open(STATS_FILE,"w+")
        logs.write(stats)
        logs.close()

    def set_text(self,text,type="error"):
        if type=="error":
            self.text_error.set(text)
        elif type=="user":
            self.text_user.set(text)

    def is_email(self,email):
        return re.fullmatch(EMAIL_REGEX, email)
    
    def login(self):
        email = self.input_email.get()
        if not email or not self.is_email(email.strip()):
            self.set_text("Please enter a valid email")
        else:
            email = email.strip().lower()
            if self.redis.hlen(email):
                self.email = email
                cpt = int(self.redis.hget(email,"__logins__").decode('utf-8'))
                self.redis.hset(email,"__logins__",cpt+1)
                self.set_text(f"Connected ({self.email})",type="user")
            else:
                self.redis.hsetnx(email,"__logins__",1)
                self.email = email
                self.set_text(f"New user registered ({self.email})",type="user")
            self.set_text("")
            self.input_email.destroy()
            self.button_login.destroy()
            self.label_email.destroy()

            self.button_logout = ttk.Button(self.app, text ="Logout", command = self.logout)
            self.button_logout.pack()

            self.add_url_section()

    def convert_to_short(self):
        long = self.input_long.get()
        if long:
            short = self.long_to_short(long.strip())
            self.input_short.delete(0,END)
            self.input_short.insert(0,short)
            self.set_text("") 

    def convert_to_long(self):
        short = self.input_short.get()
        if short:
            long = self.short_to_long(short.strip())
            self.input_long.delete(0,END)
            if long:
                self.input_long.insert(0,long)
                self.set_text("") 
            else:
                self.set_text("URL not found")   

    def add_url_section(self):

        self.label_long = ttk.Label(text="Long : ")
        self.label_long.pack(padx=(50,50), pady=(70,0),fill='both')

        self.input_long = ttk.Entry(self.app)
        self.input_long.pack(padx=(50,50), pady=(0,0), fill='both')


        y= 200
        x= 165
        w= 90
        self.button_short = ttk.Button(self.app, text ="⬇️", command = self.convert_to_short)
        self.button_short.place(x=x, y=y)
        self.button_long = ttk.Button(self.app, text ="⬆️", command = self.convert_to_long)
        self.button_long.place(x=x+w, y=y)

       


        self.label_short = ttk.Label(text="Short : ")
        self.label_short.pack(padx=(50,50), pady=(50,0),fill='both')

        self.input_short = ttk.Entry(self.app)
        self.input_short.pack(padx=(50,50), pady=(0,0), fill='both')

        self.button_stats = ttk.Button(self.app, text ="Dump user stats", command = self.dump_stats)
        self.button_stats.pack(pady=(100,0))


        return

    def logout(self):
        self.email = None
        self.set_text("",type="user")

        self.button_logout.destroy()
        self.label_long.destroy()
        self.input_long.destroy()
        self.button_short.destroy()
        self.button_long.destroy()
        self.label_short.destroy()
        self.input_short.destroy()
        self.button_stats.destroy()

        self.add_email_section()

    def add_email_section(self):
        self.label_email = ttk.Label(text="Email : ")
        
        self.label_email.pack(padx=(0,0), pady=(100,0))

        self.input_email = ttk.Entry(self.app)
        self.input_email.pack(padx=(50,50), pady=(0,0), fill='both')

        self.button_login = ttk.Button(self.app, text ="Login", command = self.login)
        self.button_login.pack(pady=(100,0))

    def run(self):
       

        self.app = Tk()

        style = ThemedStyle(self.app)
        style.set_theme(STYLE)


        self.app.geometry("500x500")
        self.app.title("TinyURL")
        center(self.app)

        self.text_user = StringVar()
        label_user = ttk.Label(self.app, textvariable=self.text_user)
        label_user.pack(pady=(10,0))
        self.text_error = StringVar()
        label_error = ttk.Label(self.app, textvariable=self.text_error)
        label_error.pack()

        self.add_email_section()
        

        mainloop()
# ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')