import threading
from functools import partial
from tkinter import *
from tkinter import simpledialog
from tkinter.ttk import Separator
from structures import *
import Server
import database
from enum import Enum
import time


class ActionType(Enum):
    UPDATE = 1
    NEW_USER = 2
    ADD_TASK = 3


class Action:
    type = None
    extra = None

    def __init__(self, action_type: ActionType, extra=None):
        self.type = action_type
        self.extra = extra


class ActivityRoot(Tk):
    labels = []
    add_button = None
    queue = None
    users = None
    tasks = None
    isExe = False

    def __init__(self):
        super().__init__()
        self.queue = Queue()
        self.users = database.UsersTable()
        self.tasks = []


def prepare_for_new_task(root_element: ActivityRoot):
    name = simpledialog.askstring("Input", "Новая задача с именем", parent=root_element)
    if name is None or name == "" or name == " " or name == "  ":
        return
    root_element.queue.push(Action(ActionType.ADD_TASK, extra=name))


def add_task(root_element: ActivityRoot, name="task"):
    task = Server.Task()
    task.name = name
    task.users_have_solve = []
    task.users_have_question = []
    task.users_have_no_solve = []
    Server.add_task(task)
    u = root_element.users.getLinesFromTable()
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
    add = Button(root_element, text="+", command=partial(prepare_for_new_task, root_element))
    add.grid(row=0, column=t * 2 + 3)
    root_element.add_button = add


def add_menu(root_element: ActivityRoot):
    mainmenu = Menu(root_element)
    root_element.config(menu=mainmenu)
    file_menu1 = Menu(mainmenu, tearoff=0)
    file_menu1.add_command(label="Добавить задачу", command=partial(prepare_for_new_task, root_element))
    mainmenu.add_cascade(label="Edit", menu=file_menu1)


def draw_grid(root_element: ActivityRoot):
    u = root_element.users.getLinesFromTable()
    tasks = root_element.tasks
    for r in range(len(u) + 1):
        for c in range(len(tasks) + 1):
            Separator(root_element, orient="vertical").grid(row=2 * r, column=2 * c + 1, sticky="ns")
            Separator(root_element, orient="horizontal").grid(row=2 * r + 1, column=2 * c, sticky="we")


def prepare_for_start(root_element: ActivityRoot):
    u = root_element.users.getLinesFromTable()
    for r in range(len(u) + 1):
        label = Label(root_element, text="     ")
        label.grid(row=2 * r, column=0, sticky='w')
        root_element.labels.append([label])
    add = Button(root_element, text="+", command=partial(prepare_for_new_task, root_element))
    add.grid(row=0, column=3)
    root_element.add_button = add


def prepare_for_new_user(root_element: ActivityRoot):
    u = root_element.users.getLinesFromTable()
    tasks = root_element.tasks
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


def update(root_element: ActivityRoot, content=True):

    u = root_element.users.getLinesFromTable()
    tasks = root_element.tasks
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
                root_element.labels[r][c]["bg"] = col
    root_element.add_button.destroy()
    add = Button(root_element, text="+", command=partial(prepare_for_new_task, root_element))
    add.grid(row=0, column=len(tasks) * 2 + 3)
    root_element.add_button = add


def queue_exe(root_element: ActivityRoot):
    queue = root_element.queue
    while True:
        if queue.size() != 0:
            action = queue.pop()
            if action.type == ActionType.UPDATE:
                update(root_element)
            elif action.type == ActionType.NEW_USER:
                prepare_for_new_user(root_element)
            elif action.type == ActionType.ADD_TASK:
                add_task(root_element, name=action.extra)
            continue
        time.sleep(0.25)


if __name__ == "__main__":
    root = ActivityRoot()
    root.labels = []
    root.geometry("1080x720")
    root.title("239Online")
    a_thread = threading.Thread(target=Server.start_bot, args=(root,))
    a_thread.start()
    add_menu(root)
    prepare_for_start(root)
    draw_grid(root)
    root.queue.push(Action(ActionType.UPDATE))

    class UL(Server.UpdateListener):
        def update(self, tasks_list, users_db):
            root.queue.push(Action(ActionType.UPDATE))
            root.tasks = tasks_list
            root.users = users_db

    class NUL(Server.NewUserListener):
        def update(self, tasks_list, users_db):
            root.queue.push(Action(ActionType.NEW_USER))
            root.tasks = tasks_list
            root.users = users_db

    Server.update_listeners.append(UL())
    Server.new_user_listeners.append(NUL())

    queue_thread = threading.Thread(target=queue_exe, args=(root,))
    queue_thread.start()

    root.mainloop()
