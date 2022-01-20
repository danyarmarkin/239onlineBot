import threading
from functools import partial
from tkinter import *
from tkinter import simpledialog
import Server
import database


def add_task(root):
    name = simpledialog.askstring("Input", "Новая задача с именем", parent=root)
    if name is None:
        return
    task = Server.Task()
    task.name = name
    task.users_have_solve = []
    task.users_have_question = []
    task.users_have_no_solve = []
    Server.add_task(task)
    update(root, Server.tasks, database.UsersTable())


def add_menu(root):
    mainmenu = Menu(root)
    root.config(menu=mainmenu)
    file_menu1 = Menu(mainmenu, tearoff=0)
    file_menu1.add_command(label="Добавить задачу", command=partial(add_task, root))
    mainmenu.add_cascade(label="Edit", menu=file_menu1)


def update(root, tasks, users):
    for child in root.winfo_children():
        child.destroy()
    add_menu(root)
    u = users.getLinesFromTable()
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            if r == 0 and c == 0:
                continue
            elif r == 0:
                l = Label(root, text=f"  {tasks[c - 1].name}  ")
                l.grid(row=r, column=c)
            elif c == 0:
                l = Label(root, text=f"{u[r - 1][2]} {u[r - 1][1]}", height=1)
                l.grid(row=r, column=c)
            else:
                user_id = u[r - 1][0]
                task = tasks[c - 1]
                l = Label(root, text="   ")
                if user_id in task.users_have_solve:
                    l["bg"] = "green"
                elif user_id in task.users_have_no_solve:
                    l["bg"] = "red"
                elif user_id in task.users_have_question:
                    l["bg"] = "yellow"
                l.grid(row=r, column=c)


if __name__ == "__main__":
    root = Tk()
    root.geometry("1080x720")
    root.title("239Online")
    a_thread = threading.Thread(target=Server.start_bot, args=(root,))
    a_thread.start()
    add_menu(root)
    root.mainloop()
