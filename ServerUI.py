import threading
from tkinter import *
import database
import Server

if __name__ == "__main__":
    root = Tk()

    a_thread = threading.Thread(target=Server.start_bot, args=(root, ))
    a_thread.start()
    root.mainloop()


def update(root, tasks, users):
    for child in root.winfo_children():
        child.destroy()
    u = users.getLinesFromTable()
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            if r == 0 and c == 0:
                continue
            elif r == 0:
                l = Label(root, text=tasks[c - 1].name)
                l.grid(row=r, column=c)
            elif c == 0:
                l = Label(root, text=f"{u[r - 1][2]} {u[r - 1][1]}")
                l.grid(row=r, column=c)
            else:
                user_id = u[r - 1][0]
                task = tasks[c - 1]
                l = Label(root, text="   ")
                print(task.users_have_solve)
                print(task.users_have_no_solve)
                print(task.users_have_question)
                if user_id in task.users_have_solve:
                    l["bg"] = "green"
                elif user_id in task.users_have_no_solve:
                    l["bg"] = "red"
                elif user_id in task.users_have_question:
                    l["bg"] = "yellow"
                l.grid(row=r, column=c)
