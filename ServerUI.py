import threading
from functools import partial
from tkinter import *
from tkinter import simpledialog
from tkinter.ttk import Separator, Style

import Server
import database


def add_task(root):
    name = simpledialog.askstring("Input", "Новая задача с именем", parent=root)
    if name is None or name == "" or name == " " or name == "  ":
        return
    task = Server.Task()
    task.name = name
    task.users_have_solve = []
    task.users_have_question = []
    task.users_have_no_solve = []
    Server.add_task(task)
    users = database.UsersTable()
    u = users.getLinesFromTable()
    t = len(Server.tasks)

    for i in range(len(u) + 1):
        Separator(root, orient="vertical").grid(row=2 * i, column=2 * t + 1, sticky="ns")
        Separator(root, orient="horizontal").grid(row=2 * i + 1, column=2 * t, sticky="we")

    update(root, Server.tasks, users, content=False)


def add_menu(root):
    mainmenu = Menu(root)
    root.config(menu=mainmenu)
    file_menu1 = Menu(mainmenu, tearoff=0)
    file_menu1.add_command(label="Добавить задачу", command=partial(add_task, root))
    mainmenu.add_cascade(label="Edit", menu=file_menu1)


def draw_grid(root, tasks, users):
    u = users.getLinesFromTable()
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            Separator(root, orient="vertical").grid(row=2 * r, column=2 * c + 1, sticky="ns")
            Separator(root, orient="horizontal").grid(row=2 * r + 1, column=2 * c, sticky="we")


def update(root, tasks, users, content=True):
    u = users.getLinesFromTable()
    for i in root.winfo_children():
        if ".!button" in str(i):
            i.destroy()
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            if r == 0 and c == 0:
                continue
            elif r == 0:
                l = Label(root, text=f"{tasks[c - 1].name}")
                l.grid(row=2 * r, column=c * 2, padx=7)
            elif c == 0:
                l = Label(root, text=f"{u[r - 1][2]} {u[r - 1][1]}")
                l.grid(row=2 * r, column=c * 2, sticky='w')
            else:
                if not content:
                    break
                user_id = u[r - 1][0]
                task = tasks[c - 1]
                col = None
                if user_id in task.users_have_solve:
                    col = "green"
                elif user_id in task.users_have_no_solve:
                    col = "red"
                elif user_id in task.users_have_question:
                    col = "yellow"
                if col is None:
                    continue
                l = Label(root, text="     ", bg=col)
                l.grid(row=2 * r, column=2 * c, pady=1)

    add = Button(root, text="+", command=partial(add_task, root))
    add.grid(row=0, column=len(tasks) * 2 + 3)


if __name__ == "__main__":
    root = Tk()
    root.geometry("1080x720")
    root.title("239Online")
    a_thread = threading.Thread(target=Server.start_bot, args=(root,))
    a_thread.start()
    add_menu(root)
    draw_grid(root, [], database.UsersTable())
    update(root, [], database.UsersTable())
    root.mainloop()

