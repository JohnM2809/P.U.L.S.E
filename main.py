import hashlib
import json
from datetime import date, datetime
from pathlib import Path

import customtkinter as ctk


DATA_FILE = Path(__file__).with_name("miguel_data.json")
BLACK = "#000000"
PANEL = "#0B0D10"
FIELD = "#11151B"
LINE = "#252B35"
TEXT = "#F5F7FA"
MUTED = "#8F9AAA"
BLUE = "#4D8DFF"
MINT = "#35D0A1"
AMBER = "#F5B942"
RED = "#F05D6F"


def digest(password):
    return hashlib.sha256(password.encode()).hexdigest()


class SchoolData:
    def __init__(self):
        self.data = self.load()

    def empty(self):
        return {"users": [], "attendance": [], "marks": [], "timetable": [], "circulars": []}

    def load(self):
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf8"))
            if not isinstance(data, dict):
                return self.empty()
            for key, value in self.empty().items():
                if not isinstance(data.get(key), list):
                    data[key] = value
            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return self.empty()

    def save(self):
        DATA_FILE.write_text(json.dumps(self.data, indent=2), encoding="utf8")

    def items(self, name):
        return self.data[name]

    def next_id(self, name):
        return max((item.get("id", 0) for item in self.items(name)), default=0) + 1

    def teacher_exists(self):
        return any(user["role"] == "teacher" for user in self.items("users"))

    def create_teacher(self, username, password):
        self.add_user(username, password, "teacher")

    def add_user(self, username, password, role, **details):
        username = username.strip()
        if not username or not password:
            raise ValueError("Username and password are required")
        if any(user["username"].casefold() == username.casefold() for user in self.items("users")):
            raise ValueError("That username is already in use")
        user = {"id": self.next_id("users"), "username": username, "password": digest(password), "role": role, **details}
        self.items("users").append(user)
        self.save()
        return user

    def login(self, username, password):
        secret = digest(password)
        return next((user for user in self.items("users") if user["username"].casefold() == username.strip().casefold() and user["password"] == secret), None)

    def students(self, search=""):
        term = search.casefold().strip()
        users = [user for user in self.items("users") if user["role"] == "student"]
        if term:
            users = [user for user in users if term in " ".join(str(user.get(key, "")) for key in ("name", "roll", "username")).casefold()]
        return sorted(users, key=lambda user: (int(user["roll"]) if user["roll"].isdigit() else 9999, user["name"]))

    def user(self, user_id):
        return next((user for user in self.items("users") if user["id"] == user_id), None)

    def add_student(self, name, roll, username, password, email):
        required = [name, roll, username, password]
        if not all(value.strip() for value in required):
            raise ValueError("Complete all required fields")
        return self.add_user(username, password, "student", name=name.strip(), roll=roll.strip(), email=email.strip())

    def update_student(self, user_id, name, roll, username, password, email):
        user = self.user(user_id)
        if not user:
            raise ValueError("Student not found")
        username = username.strip()
        if not all([name.strip(), roll.strip(), username]):
            raise ValueError("Complete all required fields")
        if any(item["id"] != user_id and item["username"].casefold() == username.casefold() for item in self.items("users")):
            raise ValueError("That username is already in use")
        user.update(name=name.strip(), roll=roll.strip(), username=username, email=email.strip())
        if password:
            user["password"] = digest(password)
        self.save()

    def remove_student(self, user_id):
        self.data["users"] = [user for user in self.items("users") if user["id"] != user_id]
        self.data["attendance"] = [item for item in self.items("attendance") if item["student_id"] != user_id]
        self.data["marks"] = [item for item in self.items("marks") if item["student_id"] != user_id]
        self.save()

    def record_attendance(self, student_id, day, present):
        item = next((item for item in self.items("attendance") if item["student_id"] == student_id and item["day"] == day), None)
        if item:
            item["present"] = present
        else:
            self.items("attendance").append({"id": self.next_id("attendance"), "student_id": student_id, "day": day, "present": present})
        self.save()

    def attendance(self, student_id):
        return sorted((item for item in self.items("attendance") if item["student_id"] == student_id), key=lambda item: item["day"], reverse=True)

    def attendance_rate(self, student_id):
        records = self.attendance(student_id)
        present = sum(item["present"] for item in records)
        return present, len(records), round(present / len(records) * 100, 1) if records else 0

    def add_mark(self, student_id, subject, assessment, score, total):
        score, total = float(score), float(total)
        if not subject.strip() or not assessment.strip() or total <= 0:
            raise ValueError("Enter a subject, assessment, and valid total")
        self.items("marks").append({"id": self.next_id("marks"), "student_id": student_id, "subject": subject.strip(), "assessment": assessment.strip(), "score": score, "total": total})
        self.save()

    def marks(self, student_id):
        return list(reversed([item for item in self.items("marks") if item["student_id"] == student_id]))

    def add_lesson(self, day, period, subject, teacher, room):
        values = [day, period.strip(), subject.strip(), teacher.strip(), room.strip()]
        if not all(values):
            raise ValueError("Complete every lesson field")
        if any(item["day"] == day and item["period"] == period.strip() and item["room"].casefold() == room.strip().casefold() for item in self.items("timetable")):
            raise ValueError("That room already has a lesson in this period")
        self.items("timetable").append({"id": self.next_id("timetable"), "day": day, "period": period.strip(), "subject": subject.strip(), "teacher": teacher.strip(), "room": room.strip()})
        self.save()

    def lessons(self):
        order = {day: index for index, day in enumerate(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"])}
        return sorted(self.items("timetable"), key=lambda item: (order.get(item["day"], 9), item["period"]))

    def add_circular(self, title, message):
        if not title.strip() or not message.strip():
            raise ValueError("Add both a title and message")
        self.items("circulars").append({"id": self.next_id("circulars"), "title": title.strip(), "message": message.strip(), "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")})
        self.save()

    def circulars(self):
        return list(reversed(self.items("circulars")))

    def stats(self):
        students = self.students()
        attendance = self.items("attendance")
        rate = round(sum(item["present"] for item in attendance) / len(attendance) * 100, 1) if attendance else 0
        return len(students), rate, len(self.items("circulars"))


class Form(ctk.CTkToplevel):
    def __init__(self, app, title, fields, save, values=None):
        super().__init__(app)
        self.app, self.save_action, self.inputs = app, save, {}
        two_columns = len(fields) > 4 and all(kind != "text" for _, kind in fields)
        self.title(title)
        self.configure(fg_color=PANEL)
        self.geometry("650x430" if two_columns else "500x470")
        self.resizable(False, False)
        self.transient(app)
        self.grab_set()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text=title, font=("Segoe UI Semibold", 22), text_color=TEXT).grid(row=0, column=0, sticky="w", padx=28, pady=(25, 10))
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=28)
        if two_columns:
            body.grid_columnconfigure((0, 1), weight=1)
        for index, (label, kind) in enumerate(fields):
            cell = ctk.CTkFrame(body, fg_color="transparent")
            if two_columns:
                cell.grid(row=index // 2, column=index % 2, sticky="ew", padx=(0, 12) if index % 2 == 0 else (12, 0), pady=4)
            else:
                cell.grid(row=index, column=0, sticky="ew", pady=4)
                body.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(cell, text=label, text_color=MUTED, font=("Segoe UI", 12)).pack(anchor="w", pady=(2, 4))
            if kind == "text":
                input_box = ctk.CTkTextbox(cell, height=86, fg_color=FIELD, border_width=1, border_color=LINE, text_color=TEXT)
            elif isinstance(kind, list):
                input_box = ctk.CTkOptionMenu(cell, values=kind, fg_color=FIELD, button_color=LINE, button_hover_color=LINE, dropdown_hover_color=FIELD, text_color=TEXT)
            else:
                input_box = ctk.CTkEntry(cell, height=34, fg_color=FIELD, border_color=LINE, text_color=TEXT, show="•" if kind == "password" else "")
            input_box.pack(fill="x")
            if values and label in values:
                if kind == "text": input_box.insert("1.0", str(values[label]))
                elif isinstance(kind, list): input_box.set(str(values[label]))
                else: input_box.insert(0, str(values[label]))
            self.inputs[label] = (input_box, kind)
        ctk.CTkButton(self, text="Save", height=40, fg_color=BLUE, hover=False, command=self.submit).grid(row=2, column=0, sticky="ew", padx=28, pady=(16, 24))

    def submit(self):
        values = {}
        for label, (input_box, kind) in self.inputs.items():
            values[label] = input_box.get("1.0", "end-1c").strip() if kind == "text" else input_box.get().strip()
        try:
            self.save_action(values)
            self.destroy()
        except Exception as error:
            self.app.notice(str(error), True)


class DarkTable(ctk.CTkFrame):
    def __init__(self, parent, columns, rows, select=True, on_choose=None):
        super().__init__(parent, fg_color=FIELD, corner_radius=10)
        self.columns, self.rows, self.select = columns, list(rows), select
        self.on_choose = on_choose
        self.selected = None
        self.draw()

    def picked(self):
        return self.selected

    def choose(self, row):
        if self.select:
            self.selected = row["id"]
            self.draw()
            if self.on_choose:
                self.on_choose(self.selected)

    def draw(self):
        for child in self.winfo_children(): child.destroy()
        if not self.rows:
            ctk.CTkLabel(self, text="Nothing to show yet.", text_color=MUTED, height=70).pack(fill="x")
            return
        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        header.pack(fill="x")
        for index, (key, title, width) in enumerate(self.columns):
            header.grid_columnconfigure(index, weight=width, minsize=width * 80)
            ctk.CTkLabel(header, text=title, height=32, text_color=MUTED).grid(row=0, column=index, sticky="ew")
        for row in self.rows[:8]:
            strip = ctk.CTkFrame(self, fg_color="#17345D" if row["id"] == self.selected else FIELD, corner_radius=0, height=34)
            strip.pack(fill="x")
            for index, (key, _, width) in enumerate(self.columns):
                strip.grid_columnconfigure(index, weight=width, minsize=width * 80)
                cell = ctk.CTkLabel(strip, text=str(row.get(key, "")), text_color=TEXT, anchor="center")
                cell.grid(row=0, column=index, sticky="ew", padx=12, pady=7)
                cell.bind("<Button-1>", lambda event, item=row: self.choose(item))


class Miguel(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.store = SchoolData()
        self.user = None
        self.title("M.I.G.U.E.L. | Smart School Command Center")
        self.geometry("1180x720")
        self.minsize(980, 620)
        self.configure(fg_color=BLACK)
        self.login_screen()

    def button(self, parent, **options):
        options.setdefault("hover", False)
        return ctk.CTkButton(parent, **options)

    def clear(self):
        for child in self.winfo_children(): child.destroy()

    def notice(self, text, error=False):
        label = ctk.CTkLabel(self, text=text, fg_color=RED if error else MINT, text_color=BLACK, corner_radius=8, padx=14, pady=8)
        label.place(relx=.98, rely=.04, anchor="ne")
        self.after(2500, label.destroy)

    def entry(self, parent, label, password=False):
        ctk.CTkLabel(parent, text=label, text_color=MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=36, pady=(10, 4))
        field = ctk.CTkEntry(parent, height=38, fg_color=FIELD, border_color=LINE, text_color=TEXT, show="•" if password else "")
        field.pack(fill="x", padx=36)
        return field

    def login_screen(self):
        self.clear()
        shell = ctk.CTkFrame(self, fg_color=BLACK)
        shell.place(relx=.5, rely=.5, anchor="center", relwidth=.9, relheight=.8)
        welcome = ctk.CTkFrame(shell, fg_color=PANEL, corner_radius=16)
        welcome.pack(side="left", fill="both", expand=True, padx=(0, 16))
        ctk.CTkLabel(welcome, text="M.I.G.U.E.L.", font=("Segoe UI Semibold", 34), text_color=TEXT).place(x=42, y=42)
        ctk.CTkLabel(welcome, text="Smart School\nCommand Center", font=("Segoe UI", 24), text_color=MUTED, justify="left").place(x=42, y=100)
        ctk.CTkLabel(welcome, text="A focused workspace for teachers\nand students.", font=("Segoe UI", 14), text_color=MUTED, justify="left").place(x=42, rely=.78)
        card = ctk.CTkFrame(shell, width=380, fg_color=PANEL, corner_radius=16)
        card.pack(side="right", fill="y")
        ctk.CTkLabel(card, text="Welcome back", font=("Segoe UI Semibold", 25), text_color=TEXT).pack(anchor="w", padx=36, pady=(56, 6))
        ctk.CTkLabel(card, text="Sign in to continue", text_color=MUTED).pack(anchor="w", padx=36, pady=(0, 25))
        self.username = self.entry(card, "Username")
        self.password = self.entry(card, "Password", True)
        self.button(card, text="Sign in", height=42, fg_color=BLUE, command=self.login).pack(fill="x", padx=36, pady=(24, 12))
        if not self.store.teacher_exists():
            self.button(card, text="First time teacher setup", height=38, fg_color="transparent", border_width=1, border_color=LINE, command=self.setup_teacher).pack(fill="x", padx=36)

    def setup_teacher(self):
        def save(data):
            if len(data["Password"]) < 4: raise ValueError("Use at least 4 characters for the password")
            self.store.create_teacher(data["Username"], data["Password"])
            self.notice("Teacher account created")
        Form(self, "Create teacher account", [("Username", "entry"), ("Password", "password")], save)

    def login(self):
        self.user = self.store.login(self.username.get(), self.password.get())
        if not self.user:
            self.notice("Check your username and password", True)
            return
        self.app_shell()
        self.show_page("Home")

    def app_shell(self):
        self.clear()
        self.sidebar = ctk.CTkFrame(self, width=222, fg_color=PANEL, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        ctk.CTkLabel(self.sidebar, text="M.I.G.U.E.L.", font=("Segoe UI Semibold", 21), text_color=TEXT).pack(anchor="w", padx=24, pady=(28, 5))
        ctk.CTkLabel(self.sidebar, text="SMART SCHOOL CENTER", font=("Segoe UI", 9), text_color=BLUE).pack(anchor="w", padx=25, pady=(0, 25))
        pages = ["Home", "Students", "Attendance", "Academics", "Timetable", "Circulars"] if self.user["role"] == "teacher" else ["Home", "Profile", "Attendance", "Academics", "Timetable", "Circulars"]
        self.nav = {}
        for page in pages:
            item = self.button(self.sidebar, text=page, anchor="w", height=38, corner_radius=7, fg_color="transparent", text_color=MUTED, command=lambda name=page: self.show_page(name))
            item.pack(fill="x", padx=14, pady=2)
            self.nav[page] = item
        ctk.CTkFrame(self.sidebar, height=1, fg_color=LINE).pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(self.sidebar, text=self.user["username"], font=("Segoe UI Semibold", 12), text_color=TEXT).pack(anchor="w", padx=24)
        ctk.CTkLabel(self.sidebar, text=self.user["role"].upper(), font=("Segoe UI", 10), text_color=MUTED).pack(anchor="w", padx=24)
        self.button(self.sidebar, text="Sign out", anchor="w", height=34, fg_color="transparent", text_color=RED, command=self.login_screen).pack(side="bottom", fill="x", padx=14, pady=20)
        self.main = ctk.CTkFrame(self, fg_color=BLACK, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)

    def show_page(self, name):
        for item, button in self.nav.items():
            button.configure(fg_color="#16345D" if item == name else "transparent", text_color=TEXT if item == name else MUTED)
        for child in self.main.winfo_children(): child.destroy()
        header = ctk.CTkFrame(self.main, fg_color=BLACK, height=88)
        header.pack(fill="x", padx=34, pady=(20, 0))
        header.pack_propagate(False)
        subtitles = {"Home": "Your school, at a glance", "Students": "Create and manage student accounts", "Profile": "Your account details", "Attendance": "Keep attendance records up to date", "Academics": "Track assessment performance", "Timetable": "A clear view of every lesson", "Circulars": "Important school updates"}
        ctk.CTkLabel(header, text=name, font=("Segoe UI Semibold", 27), text_color=TEXT).pack(anchor="w", pady=(14, 0))
        ctk.CTkLabel(header, text=subtitles[name], text_color=MUTED).pack(anchor="w")
        body = ctk.CTkFrame(self.main, fg_color=BLACK)
        body.pack(fill="both", expand=True, padx=34, pady=(0, 26))
        getattr(self, "page_" + name.lower())(body)

    def section(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Segoe UI Semibold", 17), text_color=TEXT).pack(anchor="w", pady=(12, 9))

    def cards(self, parent, values):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(8, 18))
        for title, value, color in values:
            card = ctk.CTkFrame(row, fg_color=PANEL, corner_radius=12)
            card.pack(side="left", fill="x", expand=True, padx=(0, 12))
            ctk.CTkLabel(card, text=title.upper(), text_color=MUTED, font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=18, pady=(16, 5))
            ctk.CTkLabel(card, text=value, text_color=color, font=("Segoe UI Semibold", 25)).pack(anchor="w", padx=18, pady=(0, 15))

    def table(self, parent, columns, rows, select=True, on_choose=None):
        table = DarkTable(parent, columns, rows, select, on_choose)
        table.pack(fill="x", pady=(0, 12))
        return table

    def page_home(self, body):
        if self.user["role"] == "teacher":
            students, attendance, circulars = self.store.stats()
            self.cards(body, [("Students", str(students), BLUE), ("Attendance average", f"{attendance}%", MINT), ("Circulars", str(circulars), AMBER)])
            self.section(body, "Today’s schedule")
            self.lesson_table(body, [item for item in self.store.lessons() if item["day"] == datetime.now().strftime("%A")])
        else:
            present, total, rate = self.store.attendance_rate(self.user["id"])
            self.cards(body, [("Attendance", f"{rate}%", MINT), ("Present", str(present), BLUE), ("Classes held", str(total), AMBER)])
            self.section(body, "Today’s schedule")
            self.lesson_table(body, [item for item in self.store.lessons() if item["day"] == datetime.now().strftime("%A")])

    def page_students(self, body):
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(8, 16))
        search = ctk.CTkEntry(top, placeholder_text="Search by name, roll or username", height=38, fg_color=FIELD, border_color=LINE, text_color=TEXT)
        search.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.button(top, text="Add student", height=38, fg_color=BLUE, command=self.add_student).pack(side="right")
        holder = ctk.CTkFrame(body, fg_color="transparent")
        holder.pack(fill="x")
        def render(event=None):
            for child in holder.winfo_children(): child.destroy()
            self.current_student = None
            users = self.store.students(search.get())
            if not users:
                ctk.CTkLabel(holder, text="No students found.", text_color=MUTED, height=70).pack(fill="x")
            self.student_table = self.table(holder, [("name", "NAME", 3), ("roll", "ROLL", 1), ("username", "USERNAME", 2), ("email", "EMAIL", 3)], users, on_choose=self.choose_student)
            actions = ctk.CTkFrame(holder, fg_color="transparent")
            actions.pack(fill="x")
            self.button(actions, text="Edit selected", fg_color=FIELD, border_width=1, border_color=LINE, command=self.edit_student).pack(side="left", padx=(0, 8))
            self.button(actions, text="Delete selected", fg_color="transparent", text_color=RED, command=self.delete_student).pack(side="left")
        search.bind("<KeyRelease>", render)
        render()

    def choose_student(self, user_id):
        self.current_student = user_id

    def add_student(self):
        fields = [("Name", "entry"), ("Roll number", "entry"), ("Username", "entry"), ("Password", "password"), ("Email", "entry")]
        def save(data):
            self.store.add_student(data["Name"], data["Roll number"], data["Username"], data["Password"], data["Email"])
            self.show_page("Students")
            self.notice("Student account created")
        Form(self, "Add student", fields, save)

    def selected_student(self):
        user_id = getattr(self, "current_student", None)
        user = self.store.user(user_id) if user_id else None
        if not user:
            raise ValueError("Select a student first")
        return user

    def edit_student(self):
        try:
            user = self.selected_student()
            fields = [("Name", "entry"), ("Roll number", "entry"), ("Username", "entry"), ("New password", "password"), ("Email", "entry")]
            values = {"Name": user["name"], "Roll number": user["roll"], "Username": user["username"], "Email": user.get("email", "")}
            def save(data):
                self.store.update_student(user["id"], data["Name"], data["Roll number"], data["Username"], data["New password"], data["Email"])
                self.show_page("Students")
                self.notice("Student updated")
            Form(self, "Edit student", fields, save, values)
        except Exception as error:
            self.notice(str(error), True)

    def delete_student(self):
        try:
            self.store.remove_student(self.selected_student()["id"])
            self.show_page("Students")
            self.notice("Student removed")
        except Exception as error:
            self.notice(str(error), True)

    def picker(self, parent):
        users = self.store.students()
        choices = {f"{user['name']}  |  Roll {user['roll']}": user["id"] for user in users}
        box = ctk.CTkOptionMenu(parent, values=list(choices) or ["No students available"], fg_color=FIELD, button_color=LINE, button_hover_color=LINE, dropdown_hover_color=FIELD, text_color=TEXT)
        box.pack(side="left", fill="x", expand=True, padx=(0, 10))
        return lambda: self.store.user(choices.get(box.get()))

    def page_attendance(self, body):
        if self.user["role"] == "student":
            present, total, rate = self.store.attendance_rate(self.user["id"])
            self.cards(body, [("Attendance", f"{rate}%", MINT), ("Present", str(present), BLUE), ("Total days", str(total), AMBER)])
            rows = [{"id": item["id"], "day": item["day"], "status": "Present" if item["present"] else "Absent"} for item in self.store.attendance(self.user["id"])]
            self.table(body, [("day", "DATE", 2), ("status", "STATUS", 2)], rows, False)
            return
        top = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=12)
        top.pack(fill="x", pady=(8, 16))
        ctk.CTkLabel(top, text="Mark attendance", font=("Segoe UI Semibold", 15), text_color=TEXT).pack(side="left", padx=(18, 14))
        student = self.picker(top)
        day = ctk.CTkEntry(top, width=130, height=38, fg_color=FIELD, border_color=LINE, text_color=TEXT)
        day.insert(0, date.today().isoformat())
        day.pack(side="left", padx=(0, 10), pady=14)
        status = ctk.CTkOptionMenu(top, values=["Present", "Absent"], width=100, fg_color=FIELD, button_color=LINE, button_hover_color=LINE, dropdown_hover_color=FIELD)
        status.pack(side="left", padx=(0, 10), pady=14)
        def save():
            user = student()
            if not user: raise ValueError("Add a student first")
            datetime.strptime(day.get(), "%Y-%m-%d")
            self.store.record_attendance(user["id"], day.get(), status.get() == "Present")
            self.show_page("Attendance")
            self.notice("Attendance saved")
        self.button(top, text="Save", fg_color=BLUE, command=lambda: self.run(save)).pack(side="left")
        self.section(body, "Recent attendance")
        rows = []
        for user in self.store.students():
            rows.extend({"id": item["id"], "day": item["day"], "student": user["name"], "status": "Present" if item["present"] else "Absent"} for item in self.store.attendance(user["id"]))
        self.table(body, [("day", "DATE", 2), ("student", "STUDENT", 3), ("status", "STATUS", 2)], rows, False)

    def page_academics(self, body):
        if self.user["role"] == "teacher":
            top = ctk.CTkFrame(body, fg_color="transparent")
            top.pack(fill="x", pady=(8, 16))
            student = self.picker(top)
            def form():
                user = student()
                if not user: raise ValueError("Select a student")
                def save(data):
                    self.store.add_mark(user["id"], data["Subject"], data["Assessment"], data["Score"], data["Out of"])
                    self.show_page("Academics")
                    self.notice("Assessment recorded")
                Form(self, "Record assessment", [("Subject", "entry"), ("Assessment", "entry"), ("Score", "entry"), ("Out of", "entry")], save)
            self.button(top, text="Record assessment", fg_color=BLUE, command=lambda: self.run(form)).pack(side="right")
            rows = []
            for user in self.store.students():
                rows.extend({"id": item["id"], "student": user["name"], "subject": item["subject"], "assessment": item["assessment"], "score": f"{item['score']:g}/{item['total']:g}", "result": f"{item['score'] / item['total'] * 100:.0f}%"} for item in self.store.marks(user["id"]))
            self.table(body, [("student", "STUDENT", 3), ("subject", "SUBJECT", 2), ("assessment", "ASSESSMENT", 2), ("score", "SCORE", 1), ("result", "RESULT", 1)], rows, False)
        else:
            rows = [{"id": item["id"], "subject": item["subject"], "assessment": item["assessment"], "score": f"{item['score']:g}/{item['total']:g}", "result": f"{item['score'] / item['total'] * 100:.0f}%"} for item in self.store.marks(self.user["id"])]
            self.table(body, [("subject", "SUBJECT", 2), ("assessment", "ASSESSMENT", 2), ("score", "SCORE", 1), ("result", "RESULT", 1)], rows, False)

    def lesson_table(self, body, lessons):
        self.table(body, [("day", "DAY", 2), ("period", "PERIOD", 1), ("subject", "SUBJECT", 3), ("teacher", "TEACHER", 2), ("room", "ROOM", 1)], lessons, False)

    def page_timetable(self, body):
        if self.user["role"] == "teacher":
            self.button(body, text="Add lesson", fg_color=BLUE, command=self.add_lesson).pack(anchor="e", pady=(8, 14))
        self.lesson_table(body, self.store.lessons())

    def add_lesson(self):
        fields = [("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]), ("Period", "entry"), ("Subject", "entry"), ("Teacher", "entry"), ("Room", "entry")]
        def save(data):
            self.store.add_lesson(data["Day"], data["Period"], data["Subject"], data["Teacher"], data["Room"])
            self.show_page("Timetable")
            self.notice("Lesson added")
        Form(self, "Add lesson", fields, save)

    def page_circulars(self, body):
        if self.user["role"] == "teacher":
            self.button(body, text="Publish circular", fg_color=BLUE, command=self.add_circular).pack(anchor="e", pady=(8, 14))
        rows = [{"id": item["id"], "title": item["title"], "message": item["message"], "created": item["created_at"]} for item in self.store.circulars()]
        self.table(body, [("title", "TITLE", 2), ("message", "MESSAGE", 5), ("created", "PUBLISHED", 2)], rows, False)

    def add_circular(self):
        def save(data):
            self.store.add_circular(data["Title"], data["Message"])
            self.show_page("Circulars")
            self.notice("Circular published")
        Form(self, "Publish circular", [("Title", "entry"), ("Message", "text")], save)

    def page_profile(self, body):
        card = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=14)
        card.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(card, text=self.user["name"], font=("Segoe UI Semibold", 25), text_color=TEXT).pack(anchor="w", padx=24, pady=(24, 4))
        ctk.CTkLabel(card, text=f"Roll no. {self.user['roll']}", text_color=BLUE).pack(anchor="w", padx=24)
        for label, value in [("Username", self.user["username"]), ("Email", self.user.get("email") or "Not provided")]:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=(18 if label == "Username" else 8, 0))
            ctk.CTkLabel(row, text=label, width=110, anchor="w", text_color=MUTED).pack(side="left")
            ctk.CTkLabel(row, text=value, text_color=TEXT).pack(side="left")
        ctk.CTkLabel(card, text="Contact your teacher if any detail needs updating.", text_color=MUTED).pack(anchor="w", padx=24, pady=24)

    def run(self, action):
        try:
            action()
        except Exception as error:
            self.notice(str(error), True)


if __name__ == "__main__":
    Miguel().mainloop()
