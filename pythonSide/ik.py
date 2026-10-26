import math
import re
from tkinter import *

BGcolor = "darkred"

_send = None
_is_simulation = lambda: False
_result_label = None
_window = None


def question_library(is_correct, angles=None, correct_msg="Nice, Correct!", wrong_msg="Try again!"):
    if not is_correct:
        _result_label.config(text=wrong_msg)
        return

    if _is_simulation():
        _result_label.config(text=f"{correct_msg} (simulation mode)")
    elif _send and angles:
        _result_label.config(text=f"{correct_msg} Driving servos...")
        _result_label.update()
        response = _send(angles)
        _result_label.config(text=f"{correct_msg} ESP32: {response}" if response else f"{correct_msg} No response from arm")
    else:
        _result_label.config(text=correct_msg)


def solve_ik(x, y, l1, l2):
    d2 = x * x + y * y
    c = (d2 - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c) > 1:
        return None
    elbow = math.acos(c)
    shoulder = math.atan2(y, x) - math.atan2(l2 * math.sin(elbow), l1 + l2 * math.cos(elbow))
    return math.degrees(shoulder), math.degrees(elbow)


def forward(shoulder, elbow, l1, l2):
    s = math.radians(shoulder)
    e = math.radians(shoulder + elbow)
    return l1 * math.cos(s) + l2 * math.cos(e), l1 * math.sin(s) + l2 * math.sin(e)


def arm_pose(base=90, shoulder=90, elbow=90, wrist=90, gripper=90):
    return [round(gripper), round(wrist), round(shoulder), round(elbow), round(base)]


def parse_numbers(text):
    return [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", text)]


def numbers_match(answer, expected, tol=1.5):
    nums = parse_numbers(answer)
    return len(nums) == len(expected) and all(abs(a - e) <= tol for a, e in zip(nums, expected))


def question_1(answer):
    try:
        is_correct = abs(float(answer) - 18) < 0.01
    except ValueError:
        is_correct = False
    question_library(is_correct, angles=[90, 90, 90, 90, 90])


def question_2(answer):
    question_library(answer.strip().lower() == "elbow", angles=[90, 45, 90, 120, 90])


def question_3(answer):
    question_library(numbers_match(answer, [2], 0.01), angles=arm_pose(90, 90, 180))


def question_4(answer):
    question_library(answer.strip().lower() in ("no", "n"))


def question_5(answer):
    x, y = forward(30, 60, 10, 10)
    question_library(numbers_match(answer, [x, y], 0.1), angles=arm_pose(90, 30, 60))


def question_6(answer):
    shoulder, elbow = solve_ik(10, 10, 10, 10)
    question_library(numbers_match(answer, [shoulder, elbow]), angles=arm_pose(90, shoulder, elbow))


def question_7(answer):
    shoulder, elbow = solve_ik(10, 12, 12, 9)
    question_library(numbers_match(answer, [shoulder, elbow]), angles=arm_pose(90, shoulder, elbow))


def question_8(answer):
    base = math.degrees(math.atan2(4, -4))
    question_library(numbers_match(answer, [base]), angles=arm_pose(base, 90, 90))


def question_9(answer):
    shoulder = math.degrees(math.atan2(8, 6))
    question_library(numbers_match(answer, [shoulder]), angles=arm_pose(90, shoulder, 0))


def question_10(answer):
    base = 45
    shoulder = math.degrees(math.atan2(6, math.hypot(6, 6)))
    question_library(numbers_match(answer, [base, shoulder]), angles=arm_pose(base, shoulder, 0))


def question_11(answer):
    base = 45
    shoulder, elbow = solve_ik(math.hypot(6, 6), 12, 10, 10)
    question_library(numbers_match(answer, [base, shoulder, elbow]), angles=arm_pose(base, shoulder, elbow))


def question_12(answer):
    base = 135
    shoulder, elbow = solve_ik(math.hypot(-6, 6), 14, 10, 10)
    question_library(numbers_match(answer, [base, shoulder, elbow]), angles=arm_pose(base, shoulder, elbow))


QUESTIONS = [
    {
        "title": "Q1: Reach of a 2-link arm",
        "prompt": "Q1: Reach of a fully extended 2-link arm with L1=10 and L2=8?",
        "check": question_1,
    },
    {
        "title": "Q2: Wrist-shoulder distance",
        "prompt": "Q2: Which joint changes the distance between the wrist and shoulder?",
        "check": question_2,
    },
    {
        "title": "Q3: Minimum reach",
        "prompt": "Q3: What is the minimum reach (arm folded fully back on itself) of a 2-link arm with L1=10 and L2=8?",
        "check": question_3,
    },
    {
        "title": "Q4: Reachable or not?",
        "prompt": "Q4: An object is 19 units from the shoulder. Can an arm with L1=10 and L2=8 reach it? (yes / no)",
        "check": question_4,
    },
    {
        "title": "Q5: Forward kinematics",
        "prompt": "Q5: L1=10, L2=10. The shoulder is at 30\u00b0 above horizontal and the elbow bends 60\u00b0 relative to the upper arm. "
                  "Where is the wrist? Enter x, y (2 decimals is fine, e.g. 1.00, 2.00).",
        "check": question_5,
    },
    {
        "title": "Q6: Pick up (easy)",
        "prompt": "Q6: PICK. L1=10, L2=10, shoulder at the origin. The object is at x=10, y=10 (y is height). "
                  "Angles are measured from horizontal for the shoulder and relative to the upper arm for the elbow, "
                  "with the elbow bending down. Enter shoulder, elbow in degrees.",
        "check": question_6,
    },
    {
        "title": "Q7: Pick up (uneven links)",
        "prompt": "Q7: PICK. L1=12, L2=9, shoulder at the origin. The object is at x=10, y=12 (y is height). "
                  "Same angle convention as Q6. Enter shoulder, elbow in degrees (nearest degree is fine).",
        "check": question_7,
    },
    {
        "title": "Q8: Base rotation",
        "prompt": "Q8: Top-down view: base 0\u00b0 points along +X and 90\u00b0 points along +Y. "
                  "An object sits at X=-4, Y=4. What base angle points the arm at it?",
        "check": question_8,
    },
    {
        "title": "Q9: Pointing (side view)",
        "prompt": "Q9: POINT. The arm is fully extended (elbow = 0\u00b0) and must point at a spot 6 units forward and 8 units up "
                  "from the shoulder. What shoulder angle from horizontal?",
        "check": question_9,
    },
    {
        "title": "Q10: Pointing in 3D",
        "prompt": "Q10: POINT. The arm is fully extended (elbow = 0\u00b0) and must point at X=6, Y=6, Z=6 "
                  "(Z is height above the shoulder, base 0\u00b0 = +X). Enter base, shoulder in degrees.",
        "check": question_10,
    },
    {
        "title": "Q11: Pick up in 3D",
        "prompt": "Q11: PICK. L1=10, L2=10. The object is at X=6, Y=6, Z=12 (Z is height above the shoulder, base 0\u00b0 = +X). "
                  "Use the Q6 convention for shoulder and elbow. Enter base, shoulder, elbow in degrees.",
        "check": question_11,
    },
    {
        "title": "Q12: Place",
        "prompt": "Q12: PLACE. After grabbing the object, drop it at X=-6, Y=6, Z=14 (L1=10, L2=10, same conventions as Q11). "
                  "Enter base, shoulder, elbow in degrees.",
        "check": question_12,
    },
]


class ScrollFrame(Frame):

    def __init__(self, parent):
        super().__init__(parent, bg=BGcolor)
        self.canvas = Canvas(self, bg=BGcolor, highlightthickness=0)
        scrollbar = Scrollbar(self, orient=VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.inner = Frame(self.canvas, bg=BGcolor)
        self._window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfig(self._window_id, width=e.width))

    def scroll(self, units):
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(units, "units")


def open_ik_library(parent, send_angles=None, is_simulation=None):
    global _send, _is_simulation, _result_label, _window

    if _window is not None and _window.winfo_exists():
        _window.lift()
        _window.focus_force()
        return _window

    _send = send_angles
    _is_simulation = is_simulation or (lambda: False)

    win = Toplevel(parent)
    _window = win
    win.title("IK Library")
    win.geometry("700x500")
    win.configure(bg=BGcolor)

    container = Frame(win, bg=BGcolor)
    container.pack(fill=BOTH, expand=True)

    current = {"scroll": None}

    def on_wheel(event):
        if current["scroll"] is not None and current["scroll"].winfo_exists():
            current["scroll"].scroll(-1 if event.delta > 0 else 1)

    win.bind("<MouseWheel>", on_wheel)
    win.bind("<Button-4>", lambda e: current["scroll"] and current["scroll"].scroll(-1))
    win.bind("<Button-5>", lambda e: current["scroll"] and current["scroll"].scroll(1))

    def clear():
        for child in container.winfo_children():
            child.destroy()

    def show_list():
        global _result_label
        clear()
        _result_label = None

        Label(container, text="IK Library", bg=BGcolor, fg="pink",
              font=("Arial", 14, "bold")).pack(pady=10)

        scroll = ScrollFrame(container)
        scroll.pack(fill=BOTH, expand=True)
        current["scroll"] = scroll

        for q in QUESTIONS:
            Button(scroll.inner, text=q["title"], font=("Arial", 11),
                   command=lambda q=q: show_question(q)).pack(pady=6, ipadx=10, ipady=4)

    def show_question(q):
        global _result_label
        clear()

        header = Frame(container, bg=BGcolor)
        header.pack(fill=X, pady=(10, 0), padx=10)
        Button(header, text="\u25C0 Back", command=show_list).pack(side=LEFT)

        scroll = ScrollFrame(container)
        scroll.pack(fill=BOTH, expand=True)
        current["scroll"] = scroll
        page = scroll.inner

        Label(page, text=q["prompt"], bg=BGcolor, fg="pink",
              font=("Arial", 11), wraplength=600).pack(pady=(15, 0))

        entry = Entry(page)
        entry.pack(pady=5)
        entry.focus_set()
        entry.bind("<Return>", lambda e: q["check"](entry.get()))
        Button(page, text="Submit", command=lambda: q["check"](entry.get())).pack()

        _result_label = Label(page, text="", bg=BGcolor, fg="pink",
                              font=("Arial", 11, "bold"), wraplength=600)
        _result_label.pack(pady=20)

    show_list()
    return win