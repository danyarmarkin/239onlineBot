import threading
from functools import partial
from tkinter import *
from tkinter import simpledialog
from tkinter.ttk import Separator

import Server
import database


def add_task(root_element):
    name = simpledialog.askstring("Input", "Новая задача с именем", parent=root_element)
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
        Separator(root_element, orient="vertical").grid(row=2 * i, column=2 * t + 1, sticky="ns")
        Separator(root_element, orient="horizontal").grid(row=2 * i + 1, column=2 * t, sticky="we")
        label = Label(root_element, text="     ")
        if i == 0:
            label["text"] = name
        label.grid(row=2 * i, column=2 * t, pady=1)
        root_element.labels[i].append(label)

    root_element.add_button.destroy()
    add = Button(root_element, text="+", command=partial(add_task, root_element))
    add.grid(row=0, column=t * 2 + 3)
    root_element.add_button = add


def add_menu(root_element):
    mainmenu = Menu(root_element)
    root_element.config(menu=mainmenu)
    file_menu1 = Menu(mainmenu, tearoff=0)
    file_menu1.add_command(label="Добавить задачу", command=partial(add_task, root_element))
    mainmenu.add_cascade(label="Edit", menu=file_menu1)


def draw_grid(root_element, tasks, users):
    u = users.getLinesFromTable()
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            Separator(root_element, orient="vertical").grid(row=2 * r, column=2 * c + 1, sticky="ns")
            Separator(root_element, orient="horizontal").grid(row=2 * r + 1, column=2 * c, sticky="we")


def prepare_for_start(root_element, users):
    u = users.getLinesFromTable()
    for r in range(len(u) + 1):
        label = Label(root_element, text="     ")
        label.grid(row=2 * r, column=0, sticky='w')
        root_element.labels.append([label])
    add = Button(root_element, text="+", command=partial(add_task, root_element))
    add.grid(row=0, column=3)
    root_element.add_button = add


def prepare_for_new_user(root_element, tasks, users):
    u = users.getLinesFromTable()
    labels = []
    for i in range(len(tasks) + 1):
        Separator(root_element, orient="vertical").grid(row=2 * len(u), column=2 * i + 1, sticky="ns")
        Separator(root_element, orient="horizontal").grid(row=2 * len(u) + 1, column=2 * i, sticky="we")
        label = Label(root_element, text="     ")
        if i == 0:
            label.grid(row=2 * len(u), column=2 * i, sticky='w')
        else:
            label.grid(row=2 * len(u), column=2 * i, pady=1)
        labels.append(label)
    root_element.labels.append(labels)


def update(root_element, tasks, users, content=True):
    root_element.add_button.destroy()
    u = users.getLinesFromTable()
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            if r == 0 and c == 0:
                continue
            elif r == 0:
                root_element.labels[0][c]["text"] = f"{tasks[c - 1].name}"
            elif c == 0:
                root_element.labels[r][0]["text"] = f"{u[r - 1][2]} {u[r - 1][1]}"
            else:
                if not content:
                    break
                user_id = u[r - 1][0]
                task = tasks[c - 1]
                col = "white"
                if user_id in task.users_have_solve:
                    col = "green"
                elif user_id in task.users_have_no_solve:
                    col = "red"
                elif user_id in task.users_have_question:
                    col = "yellow"
                if col is None:
                    continue
                root_element.labels[r][c]["bg"] = col
    add = Button(root_element, text="+", command=partial(add_task, root_element))
    add.grid(row=0, column=len(tasks) * 2 + 3)
    root_element.add_button = add


if __name__ == "__main__":
    class ActivityRoot(Tk):
        labels = []
        add_button = None

        def __init__(self):
            super().__init__()


    root = ActivityRoot()
    root.labels = []
    root.geometry("1080x720")
    root.title("239Online")
    a_thread = threading.Thread(target=Server.start_bot, args=(root,))
    a_thread.start()
    add_menu(root)
    prepare_for_start(root, database.UsersTable())
    draw_grid(root, [], database.UsersTable())
    update(root, [], database.UsersTable())
    root.mainloop()
