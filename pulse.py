import json
import os
from datetime import date

FILE = "pulse_data.json"

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def paint(text, color, width=0):
    text = f"{text:<{width}}"
    return f"{color}{text}{C.RESET}"

def today():
    return date.today().isoformat()

def screen(title=None):
    print()
    print(paint("P.U.L.S.E", C.BOLD + C.CYAN))
    print(paint("Performance & Unified Learning Support Engine", C.CYAN))

    if title:
        print(f"\n{paint(title, C.BOLD + C.BLUE)}")

    print()

def load():
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        data = {"students": {}}
        save(data)
        return data

    with open(FILE) as f:
        return json.load(f)

def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def pick(data):
    name = input("Student name: ").strip()

    if name not in data["students"]:
        print(paint("Student not found.", C.RED))
        return None

    return name

def add_student(data):
    name = input("Student name: ").strip()

    if name in data["students"]:
        print(paint("Student already exists.", C.RED))
        return

    data["students"][name] = {
        "class": input("Class: ").strip(),
        "attendance": [],
        "marks": [],
        "mistakes": []
    }

    save(data)
    print(paint(f"Added {name}.", C.GREEN))

def list_students(data):
    screen("Students")

    print(paint("Name", C.BOLD, 20) + paint("Class", C.BOLD))
    for name, rec in data["students"].items():
        print(f"{name:<20}{rec['class']}")

def attendance_pct(rec):
    records = rec.get("attendance", [])

    if not records:
        return None

    return sum(r["present"] for r in records) / len(records) * 100

def mark_attendance(data):
    selected = input(f"Date [{today()}]: ").strip() or today()

    for name, rec in data["students"].items():
        answer = input(f"{name:<20} Present? (y/n): ").strip().lower()
        present = answer == "y"

        record = next(
            (r for r in rec["attendance"] if r["date"] == selected),
            None
        )

        if record:
            record["present"] = present
        else:
            rec["attendance"].append({
                "date": selected,
                "present": present
            })

    save(data)
    print(paint(f"Attendance saved for {selected}.", C.GREEN))

def attendance_history(data):
    name = pick(data)

    if not name:
        return

    rec = data["students"][name]
    screen(f"Attendance: {name}")

    if not rec.get("attendance"):
        print("No attendance recorded.")
        return

    print(paint("Date", C.BOLD, 15) + paint("Status", C.BOLD))

    for r in rec["attendance"]:
        status = "Present" if r["present"] else "Absent"
        colour = C.GREEN if r["present"] else C.RED
        print(f"{r['date']:<15}{paint(status, colour)}")

    pct = attendance_pct(rec)
    print(f"\nOverall: {pct:.1f}%")

def add_marks(data):
    name = pick(data)

    if not name:
        return

    subject = input("Subject: ").strip()

    try:
        score = float(input("Score: "))
        out_of = float(input("Out of: "))

        if out_of <= 0 or not 0 <= score <= out_of:
            raise ValueError

    except ValueError:
        print(paint("Invalid marks.", C.RED))
        return

    data["students"][name]["marks"].append({
        "date": today(),
        "subject": subject,
        "score": score,
        "out_of": out_of
    })

    save(data)

    pct = score / out_of * 100
    print(paint(
        f"Recorded: {subject} {score:g}/{out_of:g} ({pct:.1f}%)",
        C.GREEN
    ))

def log_mistake(data):
    name = pick(data)

    if not name:
        return

    subject = input("Subject: ").strip()
    mistake = input("Mistake: ").strip()

    if not mistake:
        print(paint("Mistake cannot be empty.", C.RED))
        return

    data["students"][name].setdefault("mistakes", []).append({
        "date": today(),
        "subject": subject,
        "mistake": mistake
    })

    save(data)
    print(paint("Mistake logged.", C.YELLOW))

def marks_trend(rec):
    marks = rec.get("marks", [])
    scores = [m["score"] / m["out_of"] * 100 for m in marks]

    if len(scores) < 2:
        return None

    drop = sum(scores[:-1]) / len(scores[:-1]) - scores[-1]

    if drop >= 15:
        return "Sharp mark decline"
    if drop >= 7:
        return "Marks declining"

    return None

def academics_report(data):
    name = pick(data)

    if not name:
        return

    rec = data["students"][name]
    screen(f"Academics: {name}")

    print(paint("Marks", C.BOLD + C.BLUE))
    print(
        paint("Date", C.BOLD, 15) +
        paint("Subject", C.BOLD, 22) +
        paint("Score", C.BOLD, 12) +
        paint("Percent", C.BOLD)
    )

    for m in rec.get("marks", []):
        pct = m["score"] / m["out_of"] * 100
        score = f"{m['score']:g}/{m['out_of']:g}"

        print(
            f"{m['date']:<15}"
            f"{m['subject']:<22}"
            f"{score:<12}"
            f"{pct:.1f}%"
        )

    mistakes = rec.get("mistakes", [])
    print(f"\nMistakes: {len(mistakes)}")

    for m in mistakes:
        print(f"  {m['date']}  {m['subject']:<18} {m['mistake']}")

    trend = marks_trend(rec)

    if trend:
        print(f"\nTrend: {paint(trend, C.RED)}")

def risk(rec):
    reasons = []
    score = 0
    pct = attendance_pct(rec)

    if pct is not None:
        if pct < 75:
            score += 2
            reasons.append("Low attendance")
        elif pct < 85:
            score += 1
            reasons.append("Attendance needs attention")

    trend = marks_trend(rec)

    if trend == "Sharp mark decline":
        score += 2
        reasons.append(trend)
    elif trend == "Marks declining":
        score += 1
        reasons.append(trend)

    mistakes = len(rec.get("mistakes", []))

    if mistakes >= 4:
        score += 2
        reasons.append("Repeated mistakes")
    elif mistakes >= 2:
        score += 1
        reasons.append("Multiple mistakes")
    elif mistakes == 1:
        score += 1
        reasons.append("Mistake recorded")

    level = "HIGH" if score >= 4 else "MEDIUM" if score >= 2 else "LOW"

    return level, score, reasons

def level_color(level):
    return {
        "HIGH": C.RED,
        "MEDIUM": C.YELLOW,
        "LOW": C.GREEN
    }[level]

def early_warning(data):
    screen("Early Warning")

    ranked = [
        (score, name, level, reasons)
        for name, rec in data["students"].items()
        for level, score, reasons in [risk(rec)]
    ]

    print(
        paint("Level", C.BOLD, 10) +
        paint("Student", C.BOLD, 20) +
        paint("Reasons", C.BOLD)
    )

    for score, name, level, reasons in sorted(ranked, reverse=True):
        print(
            paint(level, level_color(level), 10) +
            f"{name:<20}" +
            (", ".join(reasons) or "No concerns")
        )

def dashboard(data):
    screen("Dashboard")

    students = data["students"]
    risks = {name: risk(rec) for name, rec in students.items()}

    marked = sum(
        any(r["date"] == today() for r in rec.get("attendance", []))
        for rec in students.values()
    )

    high = sum(r[0] == "HIGH" for r in risks.values())
    medium = sum(r[0] == "MEDIUM" for r in risks.values())

    print(f"{'Students':<20}{len(students)}")
    print(f"{'Marked today':<20}{marked}")
    print(f"{'High risk':<20}{paint(high, C.RED)}")
    print(f"{'Watchlist':<20}{paint(medium, C.YELLOW)}")

    print(f"\n{paint('Needs attention', C.BOLD + C.BLUE)}\n")

    found = False

    for name, (level, score, reasons) in sorted(
        risks.items(),
        key=lambda x: x[1][1],
        reverse=True
    ):
        if reasons:
            found = True
            print(
                paint(level, level_color(level), 10) +
                f"{name:<20}" +
                ", ".join(reasons)
            )

    if not found:
        print(paint("No concerns.", C.GREEN))

MENUS = {
    "main": (
        "1. Dashboard\n"
        "2. Students\n"
        "3. Attendance\n"
        "4. Academics\n"
        "5. Early Warning\n"
        "0. Exit"
    ),
    "students": (
        "1. Add student\n"
        "2. List students\n"
        "0. Back"
    ),
    "attendance": (
        "1. Mark attendance\n"
        "2. View history\n"
        "0. Back"
    ),
    "academics": (
        "1. Record test\n"
        "2. Log mistake\n"
        "3. View report\n"
        "0. Back"
    ),
    "warning": (
        "1. View risk list\n"
        "0. Back"
    )
}

def submenu(data, menu, actions, title):
    while True:
        screen(title)
        print(menu)

        choice = input("\nChoose: ").strip()

        if choice == "0":
            return

        if choice in actions:
            actions[choice](data)
        else:
            print(paint("Invalid option.", C.RED))
            
def main():
    data = load()

    while True:
        screen()
        print(MENUS["main"])

        choice = input("\nChoose: ").strip()

        if choice == "1":
            dashboard(data)

        elif choice == "2":
            submenu(
                data,
                MENUS["students"],
                {"1": add_student, "2": list_students},
                "Students"
            )

        elif choice == "3":
            submenu(
                data,
                MENUS["attendance"],
                {"1": mark_attendance, "2": attendance_history},
                "Attendance"
            )

        elif choice == "4":
            submenu(
                data,
                MENUS["academics"],
                {
                    "1": add_marks,
                    "2": log_mistake,
                    "3": academics_report
                },
                "Academics"
            )

        elif choice == "5":
            submenu(
                data,
                MENUS["warning"],
                {"1": early_warning},
                "Early Warning"
            )

        elif choice == "0":
            print(paint(f"\nData saved to {FILE}. Goodbye!", C.BLUE))
            break

        else:
            print(paint("Invalid option.", C.RED))

if __name__ == "__main__":
    main()