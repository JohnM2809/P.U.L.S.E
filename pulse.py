import json
import os
from datetime import date, datetime, timedelta

DATA_FILE = "pulse_data.json"


class C:
    HEAD = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"


def badge(level):
    if level == "HIGH":
        return "\033[41m\033[97m HIGH \033[0m"
    if level == "MEDIUM":
        return "\033[43m\033[30m MEDIUM \033[0m"
    return "\033[42m\033[30m LOW \033[0m"


def banner():
    print(C.HEAD + C.BOLD + "=" * 60)
    print("   P.U.L.S.E - Performance & Unified Learning Support Engine")
    print("=" * 60 + C.END)


def today_str():
    return date.today().isoformat()


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    data = {"students": {}}
    save_data(data)
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_student(data):
    name = input("Student name: ").strip()
    if name in data["students"]:
        print(C.RED + "Student already exists." + C.END)
        return
    cls = input("Class (e.g., XI-A): ").strip()
    data["students"][name] = {
        "class": cls,
        "attendance": [],
        "marks": [],
        "missed_work": 0
    }
    save_data(data)
    print(C.GREEN + f"Added {name}." + C.END)


def list_students(data):
    print(f"\n{'Name':<18}{'Class':<10}")
    print("-" * 30)
    for name, rec in data["students"].items():
        print(f"{name:<18}{rec['class']:<10}")


def pick_student(data):
    name = input("Student name: ").strip()
    if name not in data["students"]:
        print(C.RED + "Student not found." + C.END)
        return None
    return name


def mark_attendance(data):
    print(f"Marking attendance for {today_str()}")
    for name, rec in data["students"].items():
        ans = input(f"  Is {name} present today? (y/n): ").strip().lower()
        rec["attendance"].append({
            "date": today_str(),
            "present": ans == "y"
        })
    save_data(data)
    print(C.GREEN + "Attendance saved." + C.END)


def attendance_pct(rec):
    records = rec["attendance"]
    if not records:
        return None
    present = sum(1 for r in records if r["present"])
    return present / len(records) * 100


def marked_today(rec):
    return any(r["date"] == today_str() for r in rec["attendance"])


def attendance_history(data):
    name = pick_student(data)
    if not name:
        return
    rec = data["students"][name]
    pct = attendance_pct(rec)
    print(f"\nAttendance history for {name}:")
    for r in rec["attendance"]:
        status = "Present" if r["present"] else "Absent"
        print(f"  {r['date']}  {status}")
    print(
        f"\nOverall: {pct:.1f}%"
        if pct is not None
        else "\nNo attendance recorded yet."
    )


def add_marks(data):
    name = pick_student(data)
    if not name:
        return
    subject = input("Subject: ").strip()
    try:
        score = float(input("Score (0-100): ").strip())
    except ValueError:
        print(C.RED + "Invalid score." + C.END)
        return
    data["students"][name]["marks"].append({
        "date": today_str(),
        "subject": subject,
        "score": score
    })
    save_data(data)
    print(C.GREEN + f"Recorded {subject}: {score} for {name}." + C.END)


def log_missed_work(data):
    name = pick_student(data)
    if not name:
        return
    data["students"][name]["missed_work"] += 1
    save_data(data)
    print(
        C.YELLOW
        + f"Missed work logged for {name} "
          f"(total: {data['students'][name]['missed_work']})."
        + C.END
    )


def marks_trend(rec):
    scores = [m["score"] for m in rec["marks"]]
    if len(scores) < 2:
        return None, None

    last = scores[-1]
    prev_avg = sum(scores[:-1]) / len(scores[:-1])
    diff = prev_avg - last

    if diff >= 15:
        return "sharp_decline", "Sharp mark decline"
    if diff >= 7:
        return "decline", "Marks declining"
    return "stable", None


def academics_report(data):
    name = pick_student(data)
    if not name:
        return
    rec = data["students"][name]
    print(f"\nMarks history for {name}:")
    for m in rec["marks"]:
        print(f"  {m['date']}  {m['subject']:<12} {m['score']}")
    trend, reason = marks_trend(rec)
    print(f"Missed work logged: {rec['missed_work']}")
    print(f"Trend: {reason or 'Stable / not enough data'}")


def compute_risk(rec):
    reasons = []
    score = 0

    pct = attendance_pct(rec)
    if pct is not None:
        if pct < 75:
            reasons.append("Low attendance")
            score += 2
        elif pct < 85:
            reasons.append("Attendance needs attention")
            score += 1

    trend, reason = marks_trend(rec)
    if trend == "sharp_decline":
        reasons.append(reason)
        score += 2
    elif trend == "decline":
        reasons.append(reason)
        score += 1

    missed = rec.get("missed_work", 0)
    if missed >= 2:
        reasons.append("Repeated missed work")
        score += 2
    elif missed == 1:
        reasons.append("Missed work")
        score += 1

    if score >= 4:
        level = "HIGH"
    elif score >= 2:
        level = "MEDIUM"
    else:
        level = "LOW"

    return level, score, reasons


def early_warning_list(data):
    print(f"\n{C.BOLD}Early Warning - all students{C.END}")
    ranked = []
    for name, rec in data["students"].items():
        level, score, reasons = compute_risk(rec)
        ranked.append((score, name, level, reasons))
    ranked.sort(reverse=True)

    for score, name, level, reasons in ranked:
        reason_text = " • ".join(reasons) if reasons else "No concerns"
        print(f"  {badge(level)} {name:<15} {reason_text}")


def early_warning_detail(data):
    name = pick_student(data)
    if not name:
        return
    rec = data["students"][name]
    level, score, reasons = compute_risk(rec)
    pct = attendance_pct(rec)

    print(f"\n{C.BOLD}Risk profile: {name}{C.END}")
    print(f"  Level: {badge(level)}  (score: {score})")
    print(
        f"  Attendance: {pct:.1f}%"
        if pct is not None
        else "  Attendance: no data"
    )
    print(f"  Missed work: {rec.get('missed_work', 0)}")
    print(
        f"  Reasons: "
        f"{', '.join(reasons) if reasons else 'None'}"
    )

    if level == "HIGH":
        print(
            C.RED
            + "  Suggested action: Schedule a parent-teacher meeting."
            + C.END
        )
    elif level == "MEDIUM":
        print(
            C.YELLOW
            + "  Suggested action: Monitor closely over the next 2 weeks."
            + C.END
        )
    else:
        print(
            C.GREEN
            + "  Suggested action: No action needed."
            + C.END
        )


def dashboard(data):
    banner()
    students = data["students"]
    total = len(students)
    marked_count = sum(1 for r in students.values() if marked_today(r))

    risks = {
        name: compute_risk(rec)
        for name, rec in students.items()
    }
    high_count = sum(
        1 for level, _, _ in risks.values()
        if level == "HIGH"
    )
    watchlist_count = sum(
        1 for level, _, _ in risks.values()
        if level == "MEDIUM"
    )

    print(f"\n{C.BOLD}Dashboard{C.END}")
    print("One view for attendance, academics and student wellbeing.\n")

    print(f"  {'Students':<12} {C.BLUE}{total}{C.END}")
    print(f"  {'Marked Today':<12} {C.GREEN}{marked_count}{C.END}")
    print(f"  {'High Risk':<12} {C.RED}{high_count}{C.END}")
    print(f"  {'Watchlist':<12} {C.YELLOW}{watchlist_count}{C.END}")

    print(f"\n{C.BOLD}Students needing attention{C.END}")
    ranked = sorted(
        (
            (score, name, level, reasons)
            for name, (level, score, reasons) in risks.items()
        ),
        reverse=True,
    )

    shown = False
    for score, name, level, reasons in ranked:
        if level in ("HIGH", "MEDIUM"):
            shown = True
            reason_text = " • ".join(reasons)
            print(
                f"  {badge(level)} {name:<15} {reason_text}"
            )

    if not shown:
        print(
            C.GREEN
            + "  No students currently flagged."
            + C.END
        )
    print()


MAIN_MENU = """
--- P.U.L.S.E Main Menu ---
1. Dashboard
2. Students
3. Attendance
4. Academics
5. Early Warning
0. Exit
"""

STUDENTS_MENU = """
-- Students --
1. Add student
2. List students
0. Back
"""

ATTENDANCE_MENU = """
-- Attendance --
1. Mark attendance for today
2. View a student's attendance history
0. Back
"""

ACADEMICS_MENU = """
-- Academics --
1. Record a test score
2. Log missed work
3. View a student's academics report
0. Back
"""

EARLY_WARNING_MENU = """
-- Early Warning --
1. View full risk list
2. View a student's risk detail
0. Back
"""


def submenu(title, data, handlers):
    while True:
        print(title)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            return
        action = handlers.get(choice)
        if action:
            action(data)
        else:
            print(C.RED + "Invalid option." + C.END)


def main():
    data = load_data()
    banner()
    while True:
        print(MAIN_MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            dashboard(data)
        elif choice == "2":
            submenu(
                STUDENTS_MENU,
                data,
                {"1": add_student, "2": list_students}
            )
        elif choice == "3":
            submenu(
                ATTENDANCE_MENU,
                data,
                {"1": mark_attendance, "2": attendance_history}
            )
        elif choice == "4":
            submenu(
                ACADEMICS_MENU,
                data,
                {
                    "1": add_marks,
                    "2": log_missed_work,
                    "3": academics_report
                }
            )
        elif choice == "5":
            submenu(
                EARLY_WARNING_MENU,
                data,
                {
                    "1": early_warning_list,
                    "2": early_warning_detail
                }
            )
        elif choice == "0":
            print(
                C.BLUE
                + "Goodbye! Data saved to "
                + DATA_FILE
                + C.END
            )
            break
        else:
            print(C.RED + "Invalid option, try again." + C.END)


if __name__ == "__main__":
    main()
