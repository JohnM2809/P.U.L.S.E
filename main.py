import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
import json

FILE = "miguel.json"
BLUE = "#3B82F6"
BLUE2 = "#2563EB"
BG = "#0B1120"
CARD = "#111827"
NAVY = "#0F172A"
TEXT = "#F8FAFC"
MUTED = "#94A3B8"
GREEN = "#22C55E"
RED = "#EF4444"
AMBER = "#F59E0B"

DEFAULT = {
    "students": [
        ["Aarav",47,45],["Priya",47,44],["John",47,42],["Rahul",47,40],["Arjun",47,34]
    ],
    "tasks": [
        ["Physics","WEP questions",1,0],["Chemistry","Chemical Bonding revision",2,0]
    ],
    "lessons": [
        ["Monday",1,"Physics","Mr Rao","203"],
        ["Monday",2,"Mathematics","Mr Kumar","105"],
        ["Monday",3,"Chemistry","Ms Das","Lab 2"],
        ["Monday",4,"English","Ms John","108"],
        ["Tuesday",1,"Mathematics","Mr Kumar","105"],
        ["Tuesday",2,"Physics","Mr Rao","203"]
    ]
}

def save():
    with open(FILE,"w",encoding="utf8") as f:
        json.dump(data,f,indent=2)

def load():
    global data
    try:
        with open(FILE,"r",encoding="utf8") as f:
            data=json.load(f)
    except:
        data=json.loads(json.dumps(DEFAULT))
        save()

def attendance(s):
    return 100 if s[1]==0 else s[2]/s[1]*100

def priority(t):
    if t[3]: return "Done"
    d=t[2]
    return "Urgent" if d<=1 else "Soon" if d<=3 else "Normal"

def clashes(items=None):
    items=data["lessons"] if items is None else items
    teachers,rooms,out=set(),set(),[]
    for x in items:
        a=(x[0],x[1],x[3]); b=(x[0],x[1],x[4])
        if a in teachers: out.append(f"Teacher clash: {x[3]} P{x[1]} {x[0]}")
        if b in rooms: out.append(f"Room clash: {x[4]} P{x[1]} {x[0]}")
        teachers.add(a); rooms.add(b)
    return out

def generate():
    subjects=[
        ("Physics","Mr Rao","203"),("Mathematics","Mr Kumar","105"),
        ("Chemistry","Ms Das","Lab 2"),("English","Ms John","108")
    ]
    slots=[(d,p) for d in ("Monday","Tuesday","Wednesday","Thursday","Friday") for p in range(1,5)]
    need=[s for s in subjects for _ in range(2)]
    result=[]
    def ok(s,d,p):
        for x in result:
            if x[0]==d and x[1]==p and (x[3]==s[1] or x[4]==s[2]): return False
            if x[0]==d and abs(x[1]-p)==1 and x[2]==s[0]: return False
        return True
    def back(i):
        if i==len(need): return True
        s=need[i]
        for d,p in slots:
            if ok(s,d,p):
                result.append([d,p,s[0],s[1],s[2]])
                if back(i+1): return True
                result.pop()
        return False
    if back(0):
        data["lessons"]=result
        save()
        return True
    return False

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MIGUEL — Smart School Solutions")
        self.geometry("1100x700")
        self.minsize(950,600)
        self.user=""
        self.role="Student"
        load()
        self.login()

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def button(self,p,text,cmd,width=140,main=True):
        return ctk.CTkButton(
            p,text=text,command=cmd,width=width,height=36,corner_radius=10,
            fg_color=BLUE if main else CARD,hover_color=BLUE2
        )

    def card(self,p):
        return ctk.CTkFrame(p,fg_color=CARD,corner_radius=16)

    def login(self):
        self.clear()
        left=ctk.CTkFrame(self,fg_color=NAVY,corner_radius=0)
        left.pack(side="left",fill="both",expand=True)
        right=ctk.CTkFrame(self,width=380,corner_radius=0)
        right.pack(side="right",fill="y"); right.pack_propagate(False)

        b=ctk.CTkFrame(left,fg_color="transparent")
        b.place(relx=.5,rely=.5,anchor="center")
        ctk.CTkLabel(b,text="MIGUEL",font=ctk.CTkFont(size=42,weight="bold")).pack(anchor="w")
        ctk.CTkLabel(b,text="Smart School Solutions",text_color=MUTED,
                     font=ctk.CTkFont(size=15)).pack(anchor="w",pady=(2,22))
        for x in ("Smart timetable","Attendance insights","Assignments","Smart alerts","Teacher controls"):
            ctk.CTkLabel(b,text="• "+x,text_color="#CBD5E1").pack(anchor="w",pady=3)

        p=ctk.CTkFrame(right,fg_color="transparent")
        p.pack(fill="both",expand=True,padx=40)
        ctk.CTkLabel(p,text="Welcome back",font=ctk.CTkFont(size=26,weight="bold")).pack(anchor="w",pady=(125,6))
        ctk.CTkLabel(p,text="Enter your details",text_color=MUTED).pack(anchor="w",pady=(0,20))
        self.name=ctk.CTkEntry(p,placeholder_text="Username",height=42)
        self.name.pack(fill="x",pady=6); self.name.insert(0,"John")
        self.role=ctk.StringVar(value="Student")
        ctk.CTkComboBox(p,variable=self.role,values=["Student","Teacher"],state="readonly",height=42).pack(fill="x",pady=6)
        self.button(p,"Enter MIGUEL  →",self.enter,300).pack(fill="x",pady=22)
        ctk.CTkLabel(p,text="Offline • JSON datastore",text_color="#64748B").pack()

    def enter(self):
        self.user=self.name.get().strip() or "User"
        self.build()

    def build(self):
        self.clear()
        side=ctk.CTkFrame(self,width=215,fg_color=NAVY,corner_radius=0)
        side.pack(side="left",fill="y"); side.pack_propagate(False)
        ctk.CTkLabel(side,text="MIGUEL",font=ctk.CTkFont(size=22,weight="bold")).pack(anchor="w",padx=18,pady=(24,2))
        ctk.CTkLabel(side,text=f"{self.user} • {self.role.get()}",text_color=MUTED).pack(anchor="w",padx=18,pady=(0,22))
        items=[("Dashboard",self.dashboard),("Timetable",self.timetable),("Attendance",self.attendance),("Tasks",self.tasks)]
        if self.role.get()=="Teacher":
            items += [("Students",self.students),("Manage timetable",self.manage_timetable)]
        items += [("Smart alerts",self.alerts)]
        self.nav={}
        for text,cmd in items:
            b=ctk.CTkButton(side,text=text,command=cmd,anchor="w",fg_color="transparent",hover_color="#1E293B",corner_radius=10,height=38)
            b.pack(fill="x",padx=9,pady=2); self.nav[text]=b
        ctk.CTkLabel(side,text="● OFFLINE",text_color="#7DD3FC",
                     font=ctk.CTkFont(size=10,weight="bold")).pack(side="bottom",anchor="w",padx=18,pady=18)

        main=ctk.CTkFrame(self,fg_color=BG,corner_radius=0)
        main.pack(side="left",fill="both",expand=True)
        self.title=ctk.CTkLabel(main,text="",font=ctk.CTkFont(size=27,weight="bold"))
        self.title.pack(anchor="w",padx=28,pady=(25,18))
        self.content=ctk.CTkFrame(main,fg_color="transparent")
        self.content.pack(fill="both",expand=True,padx=28,pady=(0,25))
        self.dashboard()

    def page(self,title,active):
        self.title.configure(text=title)
        for w in self.content.winfo_children(): w.destroy()
        for k,b in self.nav.items(): b.configure(fg_color=BLUE if k==active else "transparent")

    def stat(self,p,name,value,color):
        c=self.card(p); c.pack(side="left",fill="both",expand=True,padx=4)
        ctk.CTkLabel(c,text=name,text_color=MUTED,font=ctk.CTkFont(size=10,weight="bold")).pack(anchor="w",padx=15,pady=(14,2))
        ctk.CTkLabel(c,text=value,text_color=color,font=ctk.CTkFont(size=25,weight="bold")).pack(anchor="w",padx=15,pady=(0,14))

    def dashboard(self):
        self.page("Dashboard","Dashboard")
        avg=sum(attendance(s) for s in data["students"])/len(data["students"]) if data["students"] else 0
        low=sum(attendance(s)<75 for s in data["students"])
        due=sum(not t[3] and priority(t) in ("Urgent","Soon") for t in data["tasks"])
        alerts=low+due+len(clashes())

        ctk.CTkLabel(self.content,text=f"Good morning, {self.user} 👋",font=ctk.CTkFont(size=17,weight="bold")).pack(anchor="w")
        ctk.CTkLabel(self.content,text="Everything important, in one place.",text_color=MUTED).pack(anchor="w",pady=(2,14))
        stats=ctk.CTkFrame(self.content,fg_color="transparent"); stats.pack(fill="x",pady=(0,15))
        self.stat(stats,"STUDENTS",len(data["students"]),TEXT)
        self.stat(stats,"ATTENDANCE",f"{avg:.1f}%",GREEN)
        self.stat(stats,"TASKS DUE",due,BLUE)
        self.stat(stats,"ALERTS",alerts,AMBER)

        body=ctk.CTkFrame(self.content,fg_color="transparent"); body.pack(fill="both",expand=True)
        left=self.card(body); left.pack(side="left",fill="both",expand=True,padx=(0,7))
        ctk.CTkLabel(left,text="Today's schedule",font=ctk.CTkFont(size=15,weight="bold")).pack(anchor="w",padx=18,pady=(17,10))
        for x in sorted([a for a in data["lessons"] if a[0]=="Monday"],key=lambda z:z[1]):
            ctk.CTkLabel(left,text=f"P{x[1]}    {x[2]}    Room {x[4]}",anchor="w").pack(fill="x",padx=18,pady=5)

        right=self.card(body); right.pack(side="left",fill="both",expand=True,padx=(7,0))
        ctk.CTkLabel(right,text="Smart alerts",font=ctk.CTkFont(size=15,weight="bold")).pack(anchor="w",padx=18,pady=(17,10))
        msgs=[]
        for s in data["students"]:
            if attendance(s)<75: msgs.append((RED,f"{s[0]} is below 75% attendance"))
        for t in data["tasks"]:
            if not t[3] and priority(t) in ("Urgent","Overdue"): msgs.append((AMBER,f"{t[1]} is {priority(t).lower()}"))
        for x in clashes(): msgs.append((RED,x))
        if not msgs: msgs=[(GREEN,"No immediate issues detected")]
        for color,text in msgs[:4]:
            r=ctk.CTkFrame(right,fg_color=NAVY,corner_radius=10); r.pack(fill="x",padx=18,pady=4)
            ctk.CTkLabel(r,text="●",text_color=color).pack(side="left",padx=10,pady=8)
            ctk.CTkLabel(r,text=text,anchor="w").pack(side="left",fill="x",expand=True)

    def timetable(self):
        self.page("Timetable","Timetable")
        frame=ctk.CTkFrame(self.content,fg_color=CARD,corner_radius=14); frame.pack(fill="both",expand=True)
        headers=["Period","Mon","Tue","Wed","Thu","Fri"]
        for j,h in enumerate(headers): ctk.CTkLabel(frame,text=h,text_color=MUTED,font=ctk.CTkFont(weight="bold")).grid(row=0,column=j,padx=12,pady=12,sticky="nsew")
        lookup={(x[0],x[1]):x[2] for x in data["lessons"]}
        days=["Monday","Tuesday","Wednesday","Thursday","Friday"]
        for i in range(1,5):
            ctk.CTkLabel(frame,text=str(i)).grid(row=i,column=0,padx=12,pady=8)
            for j,d in enumerate(days,1): ctk.CTkLabel(frame,text=lookup.get((d,i),"—")).grid(row=i,column=j,padx=12,pady=8)
        bar=ctk.CTkFrame(self.content,fg_color="transparent"); bar.pack(fill="x",pady=(10,0))
        self.button(bar,"Check conflicts",self.check_conflicts,140,False).pack(side="left")
        if self.role.get()=="Teacher":
            self.button(bar,"Manage timetable",self.manage_timetable,160).pack(side="left",padx=8)
            self.button(bar,"Generate",self.generate,120).pack(side="left")

    def check_conflicts(self):
        x=clashes()
        messagebox.showwarning("MIGUEL","\n".join(x)) if x else messagebox.showinfo("MIGUEL","No teacher or room conflicts.")

    def generate(self):
        if generate(): messagebox.showinfo("MIGUEL","New conflict-free timetable generated."); self.timetable()
        else: messagebox.showerror("MIGUEL","No valid timetable found.")

    def attendance(self):
        self.page("Attendance","Attendance")
        card=self.card(self.content); card.pack(fill="both",expand=True)
        for j,h in enumerate(("Student","Attendance","Status")): ctk.CTkLabel(card,text=h,text_color=MUTED,font=ctk.CTkFont(weight="bold")).grid(row=0,column=j,padx=20,pady=12)
        for i,s in enumerate(data["students"],1):
            p=attendance(s)
            ctk.CTkLabel(card,text=s[0]).grid(row=i,column=0,padx=20,pady=7,sticky="w")
            ctk.CTkLabel(card,text=f"{p:.1f}%",text_color=GREEN if p>=75 else RED).grid(row=i,column=1,padx=20,pady=7)
            ctk.CTkLabel(card,text="Good" if p>=75 else "Attention").grid(row=i,column=2,padx=20,pady=7)
        if self.role.get()=="Teacher": self.button(self.content,"Mark attendance",self.mark_attendance,160).pack(anchor="e",pady=10)

    def mark_attendance(self):
        w=ctk.CTkToplevel(self); w.title("Attendance"); w.geometry("360x420")
        vars_=[]
        for s in data["students"]:
            v=ctk.BooleanVar(value=True); vars_.append((s,v))
            ctk.CTkCheckBox(w,text=s[0],variable=v).pack(anchor="w",padx=25,pady=5)
        def save_att():
            for s,v in vars_: s[1]+=1; s[2]+=int(v.get())
            save(); w.destroy(); self.attendance()
        self.button(w,"Save attendance",save_att,300).pack(pady=20)

    def tasks(self):
        self.page("Tasks","Tasks")
        if self.role.get()=="Teacher": self.button(self.content,"Add task",self.add_task,120).pack(anchor="e",pady=(0,10))
        card=self.card(self.content); card.pack(fill="both",expand=True)
        for j,h in enumerate(("Subject","Task","Due","Priority","Status")): ctk.CTkLabel(card,text=h,text_color=MUTED,font=ctk.CTkFont(weight="bold")).grid(row=0,column=j,padx=10,pady=12)
        for i,t in enumerate(data["tasks"],1):
            for j,v in enumerate((t[0],t[1],t[2],priority(t),"Done" if t[3] else "Pending")): ctk.CTkLabel(card,text=str(v)).grid(row=i,column=j,padx=10,pady=7,sticky="w")

    def add_task(self):
        w=ctk.CTkToplevel(self); w.title("Add task"); w.geometry("400x330")
        fields=[]
        for ph in ("Subject","Task","Due in days"):
            e=ctk.CTkEntry(w,placeholder_text=ph); e.pack(fill="x",padx=25,pady=10); fields.append(e)
        fields[2].insert(0,"2")
        def add():
            try:
                d=int(fields[2].get())
                if d<0 or not fields[1].get().strip(): raise ValueError
                data["tasks"].append([fields[0].get().strip() or "General",fields[1].get().strip(),d,0])
                save(); w.destroy(); self.tasks()
            except: messagebox.showerror("MIGUEL","Enter valid task details.")
        self.button(w,"Save task",add,300).pack(pady=15)

    def students(self):
        self.page("Students","Students")
        self.button(self.content,"Add student",lambda:self.student_edit(),130).pack(anchor="e",pady=(0,10))
        card=self.card(self.content); card.pack(fill="both",expand=True)
        for j,h in enumerate(("Name","Attendance","Edit")): ctk.CTkLabel(card,text=h,text_color=MUTED,font=ctk.CTkFont(weight="bold")).grid(row=0,column=j,padx=20,pady=12)
        for i,s in enumerate(data["students"],1):
            ctk.CTkLabel(card,text=s[0]).grid(row=i,column=0,padx=20,pady=7,sticky="w")
            ctk.CTkLabel(card,text=f"{attendance(s):.1f}%").grid(row=i,column=1,padx=20,pady=7)
            self.button(card,"Edit",lambda s=s:self.student_edit(s),65,False).grid(row=i,column=2,padx=20,pady=4)

    def student_edit(self,student=None):
        w=ctk.CTkToplevel(self); w.title("Student"); w.geometry("380x350")
        f=[]
        for ph in ("Name","Total classes","Attended classes"):
            e=ctk.CTkEntry(w,placeholder_text=ph); e.pack(fill="x",padx=25,pady=10); f.append(e)
        if student:
            f[0].insert(0,student[0]); f[1].insert(0,student[1]); f[2].insert(0,student[2])
        def save_s():
            try:
                n,t,a=f[0].get().strip(),int(f[1].get()),int(f[2].get())
                if not n or t<0 or a<0 or a>t: raise ValueError
                if student: student[:]=[n,t,a]
                else:
                    if any(s[0]==n for s in data["students"]): raise ValueError
                    data["students"].append([n,t,a])
                save(); w.destroy(); self.students()
            except: messagebox.showerror("MIGUEL","Enter valid student data.")
        self.button(w,"Save student",save_s,300).pack(pady=15)

    def manage_timetable(self):
        self.page("Manage timetable","Manage timetable")
        self.button(self.content,"Add lesson",lambda:self.lesson_edit(),130).pack(anchor="e",pady=(0,10))
        card=self.card(self.content); card.pack(fill="both",expand=True)
        for j,h in enumerate(("Day","Period","Subject","Teacher","Room","Edit")): ctk.CTkLabel(card,text=h,text_color=MUTED,font=ctk.CTkFont(weight="bold")).grid(row=0,column=j,padx=7,pady=12)
        for i,x in enumerate(data["lessons"],1):
            for j,v in enumerate(x): ctk.CTkLabel(card,text=str(v)).grid(row=i,column=j,padx=7,pady=6)
            self.button(card,"Edit",lambda x=x:self.lesson_edit(x),60,False).grid(row=i,column=5,padx=3)

    def lesson_edit(self,lesson=None):
        w=ctk.CTkToplevel(self); w.title("Lesson"); w.geometry("400x470")
        fields=[]
        for ph in ("Day","Period","Subject","Teacher","Room"):
            e=ctk.CTkEntry(w,placeholder_text=ph); e.pack(fill="x",padx=25,pady=8); fields.append(e)
        if lesson:
            for e,v in zip(fields,lesson): e.insert(0,str(v))
        def save_l():
            try:
                x=[fields[0].get().strip(),int(fields[1].get()),fields[2].get().strip(),fields[3].get().strip(),fields[4].get().strip()]
                if not x[0] or x[1]<1 or not x[2] or not x[3] or not x[4]: raise ValueError
                new=list(data["lessons"])
                if lesson: new[new.index(lesson)]=x
                else: new.append(x)
                if clashes(new): raise RuntimeError
                data["lessons"]=new; save(); w.destroy(); self.manage_timetable()
            except RuntimeError: messagebox.showwarning("MIGUEL","That lesson creates a teacher or room conflict.")
            except: messagebox.showerror("MIGUEL","Enter valid lesson data.")
        self.button(w,"Save lesson",save_l,300).pack(pady=15)

    def alerts(self):
        self.page("Smart alerts","Smart alerts")
        items=[(RED,f"{s[0]} is below 75% attendance") for s in data["students"] if attendance(s)<75]
        items += [(AMBER,f"{t[1]} is {priority(t).lower()}") for t in data["tasks"] if not t[3] and priority(t) in ("Urgent","Overdue")]
        items += [(RED,x) for x in clashes()]
        if not items: items=[(GREEN,"No alerts")]
        for color,text in items:
            r=self.card(self.content); r.pack(fill="x",pady=5)
            ctk.CTkLabel(r,text="●",text_color=color).pack(side="left",padx=14,pady=10)
            ctk.CTkLabel(r,text=text).pack(side="left",padx=4,pady=10)
        self.button(self.content,"Save data",lambda:(save(),messagebox.showinfo("MIGUEL","Saved to miguel.json")),130,False).pack(anchor="w",pady=12)

if __name__=="__main__":
    App().mainloop()
