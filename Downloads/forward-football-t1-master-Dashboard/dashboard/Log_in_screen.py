from tkinter import *

def login_user():
    #screen1 = Toplevel(screen)
    #screen1.title("Login")
    username_info = username.get()
    password_info = password.get()

    #username_entry.delete(0, END)
    #password_entry.delete(0, END)

    Label(text = "login success")

def main_screen():

    global screen
    global screen
    global username
    global password
    global username_entry
    global password_entry

    screen = Tk()
    screen.geometry("300x250")
    screen.title("Log In screen")

    username = StringVar()
    password = StringVar()

    Label(text = "Username *").pack()
    username_entry = Entry(textvariable = username).pack()

    Label(text = "Password *").pack()
    password_entry = Entry(textvariable = password).pack()

    Button(text = "Login", height = "2", width = "20", command = login_user).pack()

    screen.mainloop()

main_screen()
