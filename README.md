# P.U.L.S.E.

### Performance & Unified Learning Support Engine

> An intelligent CLI-based student monitoring and early-warning system designed to help schools identify students who may need academic or attendance-related support.

**1st Prize — Interschool Competition**

---

## About

**P.U.L.S.E. (Performance & Unified Learning Support Engine)** is a student-management and early-warning system that brings attendance, academic performance, and missed work into one place.

The project was designed as a fully offline Python CLI application. This means there are no external modules, colours, classes, etc. 

---

## Features

### Student Management

* Add new students
* Store class information
* List all registered students
* Persistent student data storage

### Attendance Tracking

* Mark daily attendance
* View individual attendance history
* Automatically calculate overall attendance percentage
* Identify attendance below important thresholds

### Academic Monitoring

* Record test scores
* View marks history
* Track changes in academic performance
* Detect declining marks

### Missed Work Tracking

* Log missed assignments or work
* Keep a running count for each student
* Include repeated missed work in risk assessment

### Early Warning System


This is the flagship feature of PULSE. Instead of just admitting, viewing the students' data, it also uses analytics to identify concerns, for the teacher to focus on

| Indicator              | Effect           |
| ---------------------- | ---------------- |
| Attendance below 75%   | High concern     |
| Attendance below 85%   | Attention needed |
| Sharp decline in marks | High concern     |
| Declining marks        | Attention needed |
| Repeated missed work   | High concern     |
| One missed-work record | Attention needed |

The resulting score is converted into:

* **LOW** — No immediate concern
* **MEDIUM** — Monitor the student
* **HIGH** — Requires intervention

The system also provides the reasons behind the risk level rather than simply displaying a score.

---



## Risk Assessment

P.U.L.S.E. uses a simple weighted scoring system.

### Attendance

* `< 75%` → +2
* `75%–84.99%` → +1

### Academic Trend

* Sharp decline → +2
* Decline → +1

### Missed Work

* `2+` missed-work records → +2
* `1` missed-work record → +1

### Final Risk Level

```text
Score ≥ 4  → HIGH
Score ≥ 2  → MEDIUM
Score < 2  → LOW
```

The system also records the specific factors contributing to the score, making the warning explainable rather than a black-box prediction.

---

## Main Menu

```text
--- P.U.L.S.E Main Menu ---
1. Dashboard
2. Students
3. Attendance
4. Academics
5. Early Warning
0. Exit
```

## Data Storage

For data storage, I used a JSON file. It proved to be more efficient, as everything is stored locally, without the need of the internet.

## Technology

* **Python 3**
* `json`
* `os`
* `datetime`
* ANSI terminal colors

I intentionally chose not to use external modules to ensure it would work for everybody

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/JohnM2809/PULSE.git
cd PULSE
```

### 2. Run the program

```bash
python pulse.py
```

---

## Project Structure

```text
PULSE/
│
├── pulse.py
├── pulse_data.json
└── README.md
```

> `pulse_data.json` is created automatically if it doesn't already exist.

---

## Competition

P.U.L.S.E. was developed and presented as an interschool competition project and won **1st Prize**.

The project combines software development, data management, educational technology, and explainable risk assessment into a practical application.

---


## Author

**John Mathew**
**@JohnM2809**

Built with Python for an interschool competition.

**1st Prize Winner**

---

## License

This project is available for educational and personal use. Add a license to this repository if you plan to distribute or modify it publicly.
