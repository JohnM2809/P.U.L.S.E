# PULSE Code Notes: imports Through compute_risk()

This covers, in file order:
1. Imports
2. `DATA_FILE`
3. `class C`
4. `badge(level)`
5. `banner()`
6. `today_str()`
7. `load_data()`
8. `save_data(data)`
9. `add_student(data)`
10. `list_students(data)`
11. `pick_student(data)`
12. `mark_attendance(data)`
13. `attendance_pct(rec)`
14. `marked_today(rec)`
15. `attendance_history(data)`
16. `add_marks(data)`
17. `log_missed_work(data)`
18. `marks_trend(rec)`
19. `academics_report(data)`
20. `compute_risk(rec)`

## 1. Imports

```python
import json
import os
from datetime import date, datetime, timedelta
```
`json` is used to read and write the PULSE data file.
`os` is used to check whether the data file exists.
`date` is used to get today's date.
`datetime` and `timedelta` are imported but are not used in this section.
`import json` keeps the module under the `json` name, so its functions are called as `json.load(...)` and `json.dump(...)`.
`from datetime import date` imports the name directly, so the code can write `date.today()`.

## 2. DATA_FILE
```python
DATA_FILE = "pulse_data.json"
```
This is the filename used for persistent PULSE data.
The uppercase name follows the normal convention for a constant.
Both `load_data()` and `save_data()` use this value instead of repeating the filename.
This gives the filename one source of truth.

## 3. class C
```python
class C:
    HEAD = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    END = "\033[0m"
    BOLD = "\033[1m"
```
`C` groups ANSI terminal-formatting codes.
`HEAD`, `BLUE`, `GREEN`, `YELLOW`, and `RED` change terminal colours.
`BOLD` enables bold text.
`END` resets terminal formatting.
The class is being used as a namespace for constants; the program does not create `C` objects.
For example:

```python
C.RED
```
accesses the class attribute directly.

## 4. badge(level)
```python
def badge(level):
    if level == "HIGH":
        return "\033[41m\033[97m HIGH \033[0m"
    if level == "MEDIUM":
        return "\033[43m\033[30m MEDIUM \033[0m"
    return "\033[42m\033[30m LOW \033[0m"
```
If `level` is `"HIGH"`, the first branch returns immediately.
If it is `"MEDIUM"`, the second branch returns.
Anything else reaches the final `return` and is displayed as LOW.
The function returns text instead of printing it, so callers can use the result inside another `print()`.
There are two separate `if` statements rather than `if/elif`; this still works because each matching branch immediately returns.


## 5. banner()

```python
def banner():
    print(C.HEAD + C.BOLD + "=" * 60)
    print("   P.U.L.S.E - Performance & Unified Learning Support Engine")
    print("=" * 60 + C.END)
```
`"=" * 60` creates a 60-character separator.
The first line applies the heading colour and bold formatting.
The last line appends `C.END` so later terminal output is reset.
The function only prints, so it has no meaningful return value.

## 6. today_str()

```python
def today_str():
    return date.today().isoformat()
```
`date.today()` gets the current date.
`.isoformat()` converts it to a `YYYY-MM-DD` string.
The helper returns the string instead of printing it so the same value can be stored in records and compared later.
This gives the attendance system one consistent date format.

## 7. load_data()
```python
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
```
### `os.path.exists(DATA_FILE)`
Checks whether the file exists before opening it.
### `with open(DATA_FILE, "r") as f`
Opens the file in read mode.
`with` handles closing the file automatically.
`f` is the file object used inside the block.
### `json.load(f)`
Reads JSON from the file and converts it into Python data structures.
The result is returned directly.
### Important detail
There is no return after the `if` block.
If the file does not exist, the function reaches the end and Python returns `None`.
So the current behaviour is:
```text
file exists → loaded dictionary
file missing → None
```

## 8. save_data(data)
```python
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
```
`"w"` opens the file in write mode.
`json.dump()` serializes the Python object directly into the file.
`indent=2` makes the JSON formatted and readable.
The two persistence operations are therefore:
```text
JSON file → Python object : json.load()
Python object → JSON file : json.dump()
```

## 9. add_student(data)
```python
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
```
`input()` returns text; `.strip()` removes surrounding whitespace.

```python
if name in data["students"]:
```
checks whether the name already exists as a dictionary key.
If it does, the function prints an error and `return` exits immediately.
This is a guard clause.
A new student gets four fields:
```text
class        → class string
attendance   → empty list
marks        → empty list
missed_work  → zero
```
The assignment:

```python
data["students"][name] = {...}
```
mutates the shared `data` dictionary.
`save_data(data)` then persists the change.
The final f-string inserts the actual student name into the confirmation.

## 10. list_students(data)
```python
def list_students(data):
    print(f"\n{'Name':<18}{'Class':<10}")
    print("-" * 30)
    for name, rec in data["students"].items():
        print(f"{name:<18}{rec['class']:<10}")
```
`:<18` and `:<10` left-align the fields inside fixed-width columns.
`.items()` gives both the dictionary key and value.
Here:

```python
name
```
is the student name and:

```python
rec
```
is the student record.
This function only reads the data.

## 11. pick_student(data)
```python
def pick_student(data):
    name = input("Student name: ").strip()
    if name not in data["students"]:
        print(C.RED + "Student not found." + C.END)
        return None
    return name
```
If the name does not exist, the function prints an error and returns `None`.
If the name exists, it returns the name.
This lets other functions share the same validation logic instead of rewriting it.
The common caller pattern is:

```python
name = pick_student(data)
if not name:
    return
```

## 12. mark_attendance(data)
```python
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
```
The loop visits every student.
`.strip().lower()` normalizes the input.
The expression:

```python
ans == "y"
```
produces a Boolean, so `"present"` stores `True` or `False`.
The new attendance dictionary is appended to the student's attendance list.
After all students are processed, `save_data(data)` persists the updated data.
This function does not call `marked_today()`, so it does not itself prevent duplicate entries for the same date.

## 13. attendance_pct(rec)
```python
def attendance_pct(rec):
    records = rec["attendance"]
    if not records:
        return None
    present = sum(1 for r in records if r["present"])
    return present / len(records) * 100
```
`records` refers to the attendance list.

```python
if not records:
```
checks for an empty list.
When there are no attendance records, the function returns `None`.
That distinguishes "no attendance data" from a real numeric percentage.
The line:

```python
sum(1 for r in records if r["present"])
```
counts the records whose `"present"` field is true.
The final expression calculates:
```text
present records / total records × 100
```

## 14. marked_today(rec)
```python
def marked_today(rec):
    return any(r["date"] == today_str() for r in rec["attendance"])
```
For every attendance record, the generator tests:

```python
r["date"] == today_str()
```
`any()` returns `True` if at least one test is true.
If no record matches, it returns `False`.
This is a read-only helper.

## 15. attendance_history(data)
```python
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
```
`pick_student()` handles validation.
The `if not name: return` line is a guard clause.
Each attendance record is displayed by the loop.
The expression:

```python
"Present" if r["present"] else "Absent"
```
selects the displayed status.
The final conditional expression chooses between the formatted percentage and the no-data message.
`:.1f` formats the percentage to one decimal place.

## 16. add_marks(data)
```python
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
```
The student is selected first.
The subject is read as text.
The score is converted with `float()`.
That conversion can raise `ValueError`, so it is inside a `try` block.
The `except` prevents bad numeric input from crashing the program.
The prompt says `0-100`, but the current code does not actually check that range. It only checks whether the input is convertible to a float.
The mark record contains:
```text
date
subject
score
```
It is appended to the student's marks list and then saved.

## 17. log_missed_work(data)
```python
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
```
The key operation is:

```python
+= 1
```
which increments the stored integer.
The function saves immediately after the change.
The final f-string reports the new counter value.
The two adjacent f-strings form one string expression.

## 18. marks_trend(rec)
```python
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
```
The list comprehension:

```python
[m["score"] for m in rec["marks"]]
```
extracts the scores.
With fewer than two scores, no comparison is possible, so the function returns:

```python
(None, None)
```
`scores[-1]` gets the latest score.
`scores[:-1]` gets every earlier score.
`prev_avg` is the average of those earlier scores.
`diff` measures:
```text
previous average - latest score
```
The thresholds are checked from the largest decline downward.
`diff >= 15` returns the `"sharp_decline"` code and its reason.
`diff >= 7` returns `"decline"` and its reason.
Everything below `7` returns `"stable", None`.
The first returned value is for program logic; the second is a readable reason.

## 19. academics_report(data)
```python
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
```
The function uses the same student-selection guard clause as the attendance functions.
Each mark is printed with aligned subject text.
`marks_trend(rec)` returns two values, unpacked into `trend` and `reason`.
Only `reason` is needed for this display.
The expression:

```python
reason or 'Stable / not enough data'
```
uses the readable reason when present and the fallback text when `reason` is `None`.

## 20. compute_risk(rec)
```python
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
```
The function starts with:

```python
reasons = []
score = 0
```
Every warning condition can add both a reason and points.
### Attendance

```python
pct = attendance_pct(rec)
```
gets the percentage.
The outer test uses:

```python
pct is not None
```
so missing attendance data is not treated as zero attendance.
Below `75` adds two points.
Below `85` but not below `75` adds one point.
### Marks
`marks_trend(rec)` supplies the trend code and reason.
`"sharp_decline"` adds two points.
`"decline"` adds one point.
Other results add nothing.
### Missed work

```python
missed = rec.get("missed_work", 0)
```
reads the counter and supplies `0` if the key is absent.
Two or more adds two points.
Exactly one adds one point.
### Final level

```python
if score >= 4:
    level = "HIGH"
elif score >= 2:
    level = "MEDIUM"
else:
    level = "LOW"
```
So the thresholds are:
```text
4+  → HIGH
2–3 → MEDIUM
0–1 → LOW
```
Finally:

```python
return level, score, reasons
```
returns the risk category, numeric score, and explanations together.
This function is the single place where the program combines its three risk signals.

---

# PULSE Code Notes: early_warning_list Through main()
## 1. early_warning_list(data)

```python
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
```

**Role:** runs when the user picks "Early Warning" then "1. View full risk list." Prints every student, ranked from highest risk to lowest.

**Walkthrough:**

1. Print a bold header. The leading `\n` gives a blank line of separation from whatever menu text was printed just before it.
2. `ranked = []` starts an empty list, one tuple will be added per student.
3. Loop over `data["students"].items()`. Each pass gives `name` (the dict key) and `rec` (that student's full record, containing `class`, `attendance`, `marks`, `missed_work`).
4. `compute_risk(rec)` is called and unpacked straight into `level, score, reasons`.
5. A tuple is appended to `ranked`, but notice the field order: `(score, name, level, reasons)`. That is not the order `compute_risk` returned them in (`level, score, reasons`). This reorder is intentional, explained next.
6. `ranked.sort(reverse=True)` sorts the list in place, highest first.

**Why the tuple is built as `(score, name, level, reasons)`:**

Python compares tuples element by element, left to right, the same way you would alphabetize a list of `(last_name, first_name)` pairs. Whatever sits first in the tuple becomes the primary sort key automatically. Putting `score` first means `.sort(reverse=True)` ranks by risk score with no `key=` argument needed at all.

If two students land on the same score, Python compares the next element, `name`, to break the tie. Since `name` is a dictionary key, it is guaranteed unique, so the comparison always resolves there. In practice, Python never needs to look at `level` or `reasons` to decide an order. Worth knowing anyway that it would still work even if it did, list comparison is also element by element, and strings sort lexicographically, so nothing would break, it just never comes up here.

7. The second loop iterates the now sorted `ranked` list, unpacking each tuple back into the same four names.
8. `reason_text = " • ".join(reasons) if reasons else "No concerns"` joins the reasons with a bullet separator, or falls back to the literal text "No concerns" for students with an empty list. This matters here specifically because this view prints every student, including LOW risk ones who can have no reasons at all.
9. The print line combines the colored badge, the name left aligned inside a 15 character field with `{name:<15}` so every row lines up in the terminal, then the reasons.

**Patterns to remember:**
- Reordering fields inside a tuple purely so the field you want to sort by lands first, avoiding a custom sort key for the simple cases.
- `list.append(...)` followed by `.sort(reverse=True)`, a two step, in place way to build then rank a collection.
- A guaranteed unique field (a dict key) doubling as a free tie breaker when sorting.



## 2. early_warning_detail(data)

```python
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
```

**Role:** runs when the user picks "Early Warning" then "2. View a student's risk detail." One student, full picture, plus a recommended next step.

**Walkthrough:**

1. `name = pick_student(data)` asks for a name and validates it. `pick_student` already prints "Student not found." and returns `None` on a bad name, so this function does not repeat that error handling.
2. `if not name: return` is a guard clause. Rather than wrapping everything else in `if name:`, the function exits immediately on the failure path, so every line after this one can safely assume `name` is valid. A pattern worth using anywhere a function starts with a "fetch or bail" step.
3. `rec = data["students"][name]` fetches the full record, safe now that the name is confirmed to exist.
4. `level, score, reasons = compute_risk(rec)` gets the shared vocabulary used everywhere in this file.
5. `pct = attendance_pct(rec)` is called again here, separately, even though `compute_risk` already called `attendance_pct` internally while building the score. It is not cached or reused, it is simply computed a second time because this function needs the raw percentage number for display, and `compute_risk` only returns the pass or fail band, not the number itself. Harmless at this data size, but worth noticing, since `dashboard` below handles the equivalent situation with a cache instead.
6. Print the header, then level plus badge plus the numeric score on one line.
7. The attendance line uses a conditional expression spread across several lines for readability, but it is still one `print(...)` call. Python evaluates the whole `f"  Attendance: {pct:.1f}%" if pct is not None else "  Attendance: no data"` expression first, then hands the single resulting string to `print`. `:.1f` formats the float to one decimal place.
8. `rec.get('missed_work', 0)` reads the counter defensively. In normal operation this default never actually gets used, `add_student` always sets `missed_work` to `0` when a student is created, but it is a cheap safety net regardless.
9. The reasons line joins with `", "` and falls back to the word `"None"` for an empty list. Compare this to `early_warning_list`, which used `" • "` as the separator and `"No concerns"` as the fallback text for the exact same situation. Both work, but if you were extending this codebase, this is exactly the kind of small inconsistency worth pulling into one shared helper, something like `format_reasons(reasons, empty_text, sep)`, so every screen describes an empty reasons list the same way.
10. The closing block is a plain `if / elif / else` on `level`, each branch printing a differently colored suggested action. Unlike the f-string interpolation used everywhere else in this function, these three lines build colored text with plain `+` concatenation, `C.RED + "text" + C.END`. Both techniques produce an identical result. An f-string like `f"{C.RED}text{C.END}"` would behave exactly the same way. Seeing both styles side by side in one file is a useful reminder that they are interchangeable, use whichever reads more clearly for the line in front of you.

**Patterns to remember:**
- A guard clause right after a "fetch and validate" call.
- `.get(key, default)` for a defensive read even when the key is very likely present.
- A multi line conditional expression is still a single expression, indentation across lines does not change that.
- String concatenation with `+` and f-string interpolation are two equivalent ways to wrap text in color codes.



## 3. dashboard(data)

```python
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
```

**Role:** menu option "1" on the main menu, called directly rather than through a submenu, since Dashboard has no sub choices of its own. Gives a one screen summary, headline numbers plus a short flagged list.

**Walkthrough:**

1. `banner()` reprints the app header every time the dashboard is opened. There is no terminal clear anywhere in this codebase, so this is the closest thing to a screen refresh, it just reprints the same header so the dashboard visually starts the same way the program did.
2. `students = data["students"]` is a reference, not a copy. `students` and `data["students"]` point at the same dictionary in memory, this line exists to save typing below, not to protect the original data.
3. `total = len(students)`.
4. `marked_count = sum(1 for r in students.values() if marked_today(r))` is the "count how many pass a test" idiom. The generator expression yields `1` once per student where `marked_today(r)` is true, `sum()` adds them up. No intermediate list gets built, and no manual counter with `+= 1` is needed.
5. `risks = {name: compute_risk(rec) for name, rec in students.items()}` is a dict comprehension that calls `compute_risk` exactly once per student and stores every result keyed by name. Compare this to `early_warning_detail` above, which called `attendance_pct` a second time redundantly. Here, the same "call it once, reuse the result" need is handled properly: `high_count`, `watchlist_count`, and the ranked list further down all read from `risks` instead of calling `compute_risk` again.
6. `high_count` and `watchlist_count` reuse the same `sum(1 for ... if ...)` idiom, this time unpacking each tuple in `risks.values()` as `level, _, _`. The underscore is the conventional name for "a value I must unpack but do not need." Since `compute_risk` returns three items, all three need a name on the left to unpack, even where only the first one is used.
7. The four stat lines each hardcode their own label and color, `'Students'`, `'Marked Today'`, `'High Risk'`, `'Watchlist'`, each padded to 12 characters with `:<12`. Fine as is for four fixed stats, if a fifth or sixth were ever added, it would be worth turning this into a loop over something like `[("Students", total, C.BLUE), ("Marked Today", marked_count, C.GREEN), ...]` instead of hand writing another near identical line.
8. The "Students needing attention" list uses `sorted(genexpr, reverse=True)` instead of `list.append` followed by `.sort()`. Both approaches land on the same ranked order. `sorted()` accepts any iterable and returns a brand new list, `.sort()` (used in `early_warning_list` above) works in place on a list that already exists. Here, a generator expression is handed directly to `sorted()`, so there is no separate "build the list, then sort it" step, it happens in one call.
9. Inside that generator expression, `for name, (level, score, reasons) in risks.items()` unpacks two layers in one line: `risks.items()` yields pairs like `("Priya", ("HIGH", 5, [...]))`, so `name` catches the first half, and `(level, score, reasons)` unpacks the nested tuple in the second half, at the same time. The expression part, `(score, name, level, reasons)`, reorders everything again so `score` sorts first, exactly like the tuple built in `early_warning_list`.
10. The loop that follows filters with `if level in ("HIGH", "MEDIUM")`, so LOW risk students never appear in this section, only in the full list produced by `early_warning_list`.
11. `shown` starts `False` and flips to `True` the first time anything prints inside the loop. After the loop, `if not shown:` prints a "No students currently flagged" fallback, but only if the loop never printed anything at all. This decides whether to show an empty state message in the same pass that does the printing, no separate length check or pre filtering needed.
12. Notice the reasons line here has no `if reasons else "No concerns"` fallback, unlike `early_warning_list`. That is safe specifically because of the invariant mentioned earlier: anything with `level` "HIGH" or "MEDIUM" is guaranteed to have at least one reason, since `compute_risk` only raises the score when it also appends a reason. `early_warning_list` needed that fallback because it also prints LOW risk students, who can have an empty `reasons` list.
13. The trailing `print()` adds one blank line of spacing after the section, a small visual polish.

**Compare to early_warning_list:** both functions rank students by score using the exact same tuple reordering trick, but `early_warning_list` builds a list first with `.append()` then sorts it in place with `.sort()`, while `dashboard` skips the intermediate list and sorts a generator expression directly with `sorted()`. Same outcome, two equally valid styles, good to be comfortable reading and writing both.

**Patterns to remember:**
- `sum(1 for x in y if cond)` to count without a manual loop counter.
- A dict comprehension used as a one shot cache inside a function, compute once, read many times.
- `sorted(generator, reverse=True)` as a one line alternative to `list.append` then `.sort()`.
- Nested unpacking directly inside a comprehension's `for` clause.
- The boolean flag pattern (`shown`) for printing a fallback only if a loop produced nothing.
- Reference versus copy: `students = data["students"]` aliases the same dictionary, it does not clone it.



## 4. The menu string constants

```python
MAIN_MENU = """
 P.U.L.S.E Main Menu
1. Dashboard
2. Students
3. Attendance
4. Academics
5. Early Warning
0. Exit
"""
```

`STUDENTS_MENU`, `ATTENDANCE_MENU`, `ACADEMICS_MENU`, and `EARLY_WARNING_MENU` all follow the exact same shape, a triple quoted multi line string, a title line, numbered options, and a "0. Back" line at the bottom (only the top level `MAIN_MENU` uses "0. Exit" instead, since there is nowhere further back to go from there).

| Constant | Numbered options | Bottom line |
||||
| `MAIN_MENU` | Dashboard, Students, Attendance, Academics, Early Warning | 0. Exit |
| `STUDENTS_MENU` | Add student, List students | 0. Back |
| `ATTENDANCE_MENU` | Mark attendance for today, View a student's attendance history | 0. Back |
| `ACADEMICS_MENU` | Record a test score, Log missed work, View a student's academics report | 0. Back |
| `EARLY_WARNING_MENU` | View full risk list, View a student's risk detail | 0. Back |

These constants are purely text. They do not connect a number to an action by themselves, that wiring happens separately in `main()` and `submenu()` below, through the `handlers` dictionaries. Keeping menu text as a plain constant, separate from the logic that dispatches on it, means you can reword any menu without touching the code that decides what each option does, and the other way around.



## 5. submenu(title, data, handlers)

```python
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
```

**Role:** this single function runs every submenu in the program. Students, Attendance, Academics, and Early Warning all call this exact same function, just with different `title` and `handlers` arguments. This is the most reusable piece of code in this section, worth understanding thoroughly.

**Walkthrough:**

1. `while True:` starts a loop with no built in exit condition. It only ends when something inside it explicitly returns.
2. `print(title)` shows whichever menu text was passed in.
3. `choice = input(...).strip()` reads raw text and strips surrounding whitespace, so `" 1 "` and `"1"` behave the same way.
4. `if choice == "0": return` exits the function entirely, not just the loop, sending control back to whoever called `submenu(...)`, which in this codebase is always `main()`.
5. `action = handlers.get(choice)`. `handlers` is a dictionary like `{"1": early_warning_list, "2": early_warning_detail}`. Note carefully, the dictionary stores the function objects themselves, `early_warning_list` with no parentheses, not the result of calling them. Python functions are first class objects, a reference to one can sit in a variable or a dictionary value without being invoked, and get called later. `.get(choice)` looks up the entered choice, and returns `None` instead of raising a `KeyError` when the key is missing, which the next line accounts for.
6. `if action:` checks whether a matching function was found. `None` is falsy, so an invalid choice like `"9"` skips straight to the `else`. Any real function object is truthy, so a valid choice proceeds.
7. `action(data)` is where the stored reference finally gets called, with `data` passed in as its one argument. This is the entire payoff of the dispatch table, `submenu` never needs to know whether `action` is `early_warning_list`, `add_student`, or `mark_attendance`, it just calls whatever it was handed, the same way, every time.
8. The `else` branch prints an error and lets the `while True` loop continue, reprinting the menu and asking again. There is no `return` here on purpose, an invalid choice should not kick the user out of the submenu.

**Why this works across four completely different menus:** every handler function referenced anywhere in this program, `add_student`, `list_students`, `mark_attendance`, `attendance_history`, `add_marks`, `log_missed_work`, `academics_report`, `early_warning_list`, `early_warning_detail`, accepts exactly one argument, `data`, and returns nothing meaningful. That shared shape, one parameter, no meaningful return value, is what lets `submenu` treat every one of them identically. If even one handler needed a second argument, or needed to return something `submenu` had to act on, this generic version would need to change, most likely by wrapping that one handler in a small `lambda data: awkward_function(data, extra_arg)` so its shape still matches the rest.

This whole pattern is usually called a dispatch table, and it is the idiomatic Python replacement for a long `if choice == "1": ... elif choice == "2": ...` chain, especially once you have more than three or four branches, or, as here, once you want the exact same branching logic reused across several different menus.

**Patterns to remember:**
- A dictionary mapping short strings to function references, looked up and called dynamically, in place of a long if/elif chain.
- `.get(key)` returning `None` for a missing key, checked with a plain `if`, instead of `try/except KeyError` or `dict[key]`.
- One generic function, parameterized by its arguments, powering four different screens instead of four near duplicate copies of the same loop.



## 6. main()

```python
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
```

**Role:** the program's entry point. Everything covered above exists to be reachable from here.

**Walkthrough:**

1. `data = load_data()` loads `pulse_data.json` once, at startup, into a single dictionary that gets threaded through every function for the rest of the program's life. That is why every handler function above takes `data` as its only argument, they are all sharing this one loaded object, by reference, not a copy.
2. `banner()` prints the header once here. `dashboard()` prints it again on every visit, so this is the only unconditional, guaranteed once per run call to it.
3. `while True:` is the top level program loop, it keeps showing the main menu until the user explicitly exits with "0".
4. `print(MAIN_MENU)` then `input(...).strip()`, the same read pattern as `submenu`.
5. Choice "1" calls `dashboard(data)` directly. This differs from choices "2" through "5", which all call `submenu(...)`. Dashboard has no sub options, it is a single screen, so it does not need a submenu loop wrapped around it.
6. Choices "2" through "5" each call `submenu(...)` with a different menu constant and a different `handlers` dictionary literal, built inline right at the call site. This is the same `submenu` function from the previous section, reused four times with different arguments.
7. Choice "0" prints a goodbye message, using the plain `+` concatenation style seen earlier in `early_warning_detail`, then `break`, which is what actually ends the `while True` loop. The message says data was saved, and it has been, but not by this line. Every mutating handler in the file, `add_student`, `mark_attendance`, `add_marks`, `log_missed_work`, already calls `save_data(data)` immediately after making its change. There is no separate "save on exit" step here, the goodbye message is just confirming work that already happened continuously through the session. Once the loop ends, `main()` has nothing left to do, so it returns and the program exits normally.
8. The final `else` catches anything that is not "0" through "5", prints an error, and lets the loop continue.

**Why main() is a plain if/elif chain and not a dispatch table like submenu:** every branch inside `submenu` does the exact same shape of thing, call `handlers[choice](data)`. Every branch inside `main()` does something structurally different, one calls a function directly, four call `submenu` with different arguments, and one calls `break` instead of calling anything at all. A dispatch dictionary needs every branch to be "call this one thing the same way," and `main()`'s branches do not fit that shape without extra wrapping, you would need something like `lambda: submenu(STUDENTS_MENU, data, {...})` for each entry, plus a sentinel value to represent "break instead of calling a function." Once uniformity breaks down like that, a plain if/elif chain is more honest about what is actually happening, which is exactly what is written here.

`if __name__ == "__main__": main()` at the very bottom is the standard Python guard that only runs `main()` when the file is executed directly, and skips it if the file is ever imported as a module from somewhere else. Since this file has no other entry point, this line is what actually starts everything when the script runs.

**Worth knowing, even though it lives just above this section's scope:** `load_data()` returns `None` if `pulse_data.json` does not exist yet, since the function only has a branch for "the file exists," and a Python function returns `None` by default if it falls off the end without hitting a `return`. On a brand new setup, before the JSON file has ever been created, `data = load_data()` sets `data` to `None`, and the very first action that touches `data["students"]`, including `dashboard()` sitting right at the top of this loop, would raise `TypeError: 'NoneType' object is not subscriptable`. The usual fix is giving `load_data()` an `else` branch that returns a fresh starting structure, `return {"students": {}}`, so the rest of the program always has a real dictionary to work with, even on the very first run.

**Patterns to remember:**
- A single loaded state object created once and passed by reference into every handler for the program's entire run.
- `break` as the loop's actual exit mechanism, everything before it is setup and looping.
- Recognizing when a dispatch table fits, uniform branches, and when a plain if/elif chain is the more honest choice, non uniform branches, rather than forcing every branching structure into the same shape.
- The `if __name__ == "__main__":` guard as the conventional single entry point for a runnable script.



## Putting it together: one full trace

Here is exactly what happens, step by step, when the program is running and the user picks Early Warning, then "View full risk list":

```
main() is running its while True loop
  MAIN_MENU is printed, user types "5"
  main() calls submenu(EARLY_WARNING_MENU, data, {"1": early_warning_list, "2": early_warning_detail})

    submenu() starts its own while True loop
    EARLY_WARNING_MENU is printed, user types "1"
    handlers.get("1") returns the early_warning_list function object
    action(data) runs, which is early_warning_list(data)

      early_warning_list() loops every student
      calls compute_risk(rec) for each one
      builds (score, name, level, reasons) tuples
      sorts them, highest score first
      prints one badge and reason line per student

    control returns to submenu()'s loop
    EARLY_WARNING_MENU is printed again, user types "0"
    submenu() returns

  control returns to main()'s loop
  MAIN_MENU is printed again
```

Two loops are active at the same time through most of this, `main()`'s loop and `submenu()`'s loop. Typing "0" only ever escapes the innermost one currently running, which is why backing out of the risk list lands back on the Early Warning menu, not all the way back at the very first screen.



## Patterns worth reusing in your own projects

- **Dispatch table:** a dict mapping short input strings to function references, called dynamically, whenever every handler shares the same signature. Falls apart the moment one handler needs a different shape, at which point a plain if/elif chain, as seen in `main()`, is the more honest choice.
- **Guard clause:** validate or fetch first, `return` immediately on failure, so the rest of the function does not need nesting inside an `if`.
- **Sortable tuples:** put whatever you want to sort by first in the tuple, then call `.sort()` or `sorted()` with `reverse=True`, instead of writing a `key=` function for simple cases. A unique field later in the tuple doubles as a free tie breaker.
- **`sum(1 for x in y if cond)`:** a compact, no intermediate list way to count how many items pass a test.
- **Comprehension as a one shot cache:** compute an expensive thing once into a dict, then have every other calculation in the function read from that dict instead of recomputing.
- **Boolean flag pattern:** a `found` or `shown` style variable, set `True` inside a loop, checked after the loop to decide whether to print a fallback message, all in one pass.
- **`.get(key, default)` versus `dict[key]`:** a safe read that returns a fallback instead of raising, useful anywhere a missing key is expected and should not crash the program.
- **Single source of truth:** keep one function as the only place that computes a derived value (`compute_risk`), and have every display function consume its output rather than reimplementing the logic themselves.

Together, `early_warning_list`, `early_warning_detail`, and `dashboard`, plus the two level menu system that reaches them, make up the entire user facing layer of this program. Everything else in the file exists to feed them data.
