import tkinter as tk
from tkinter import scrolledtext
import calendar
import main as backend


def main():
    # =========================
    # 1) Create the root window
    # =========================
    root = tk.Tk()
    root.title("kcalendar")
    root.geometry("1100x750")

    def on_close():
        backend.APP_RUNNING = False
        try:
            root.destroy()
        except:
            pass
        import sys
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)

    # =========================
    # 2) Layout (frames / boxes)
    # =========================
    content = tk.Frame(root)
    content.pack(fill="both", expand=True)

    left = tk.Frame(content)
    left.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

    right = tk.Frame(content, width=360)
    right.pack(side="right", fill="y", padx=(4, 8), pady=8)
    right.pack_propagate(False)

    # Terminal output + input (left)
    output = scrolledtext.ScrolledText(left, wrap="word", state="disabled", font=("Consolas", 10))
    output.pack(fill="both", expand=True, pady=(0, 6))

    entry = tk.Entry(left, font=("Consolas", 10))
    entry.pack(fill="x")
    entry.focus()

    # Helper: create a titled box on the right, returns (frame, header, canvas)
    def make_box(parent, title: str, height=220):
        frame = tk.Frame(parent, relief="solid", bd=1)
        frame.pack(fill="x", expand=True, pady=6)

        header = tk.Frame(frame)
        header.pack(fill="x", padx=6, pady=(6, 0))

        title_lbl = tk.Label(header, text=title, font=("Consolas", 10, "bold"))
        title_lbl.pack(side="left")

        # store label on frame so we can update it later (calendar month title)
        frame.title_lbl = title_lbl

        canvas = tk.Canvas(frame, height=height, highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=6, pady=6)

        return frame, header, canvas

    cal_frame, cal_header, cal_canvas = make_box(right, "Calendar", height=220)
    bar_frame, bar_header, bar_canvas = make_box(right, "Weekly Calories", height=220)
    pie_frame, pie_header, pie_canvas = make_box(right, "Meal Breakdown", height=220)
    btn_bar_next = tk.Button(bar_header, text=">>", width=4)
    btn_bar_next.pack(side="right", padx=(4, 0))

    btn_bar_prev = tk.Button(bar_header, text="<<", width=4)
    btn_bar_prev.pack(side="right")


    # =========================
    # 3) GUI terminal bridge (app_print / app_input)
    # =========================
    waiting_for_input = False
    input_value = None

    def write_line(text: str):
        output.configure(state="normal")
        output.insert("end", text + "\n")
        output.see("end")
        output.configure(state="disabled")

    def on_enter(event=None):
        nonlocal waiting_for_input, input_value
        text = entry.get()
        entry.delete(0, "end")

        if waiting_for_input:
            input_value = text
            waiting_for_input = False
            return

        if text.strip():
            write_line("> " + text.strip())

    entry.bind("<Return>", on_enter)

    def gui_print(*args):
        # behaves like print(): supports multiple args
        write_line(" ".join(str(a) for a in args))

    def gui_input(prompt=""):
        nonlocal waiting_for_input, input_value
        write_line(str(prompt))
        entry.focus()
        waiting_for_input = True
        input_value = None
        while waiting_for_input and backend.APP_RUNNING:
            root.update()
        return input_value

    backend.app_print = gui_print
    backend.app_input = gui_input

    # =========================
    # 4) App state (shared GUI state)
    # =========================
    today = backend.datetime.date.today()

    # Calendar state
    cal_year = today.year
    cal_month = today.month
    selected_date = today.isoformat()
    

    # Pie state
    pie_mode = "day"  # "day" | "week" | "month"

    def week_start_for(date_obj):
        # Monday-start week
        return date_obj - backend.datetime.timedelta(days=date_obj.weekday())
    bar_week_start = week_start_for(today)
    pie_week_start = week_start_for(today)

    meal_colors = {
        "breakfast": "#ff9999",
        "lunch": "#99ccff",
        "dinner": "#99ff99",
    }

    # =========================
    # 5) Calendar drawing + interaction
    # =========================
    def days_in_month(year, month):
        return calendar.monthrange(year, month)[1]

    def first_weekday(year, month):
        # 0=Monday ... 6=Sunday
        return calendar.monthrange(year, month)[0]

    def is_logged(date_str: str) -> bool:
        return date_str in backend.kcalendar

    def draw_calendar():
        nonlocal cal_year, cal_month, selected_date

        c = cal_canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            root.after(50, draw_calendar)
            return

        # update title label in header
        cal_frame.title_lbl.config(text=f"{calendar.month_name[cal_month]} {cal_year}")

        pad = 10
        header_h = 0  # title is in header now
        dow_h = 20

        grid_top = header_h + dow_h
        grid_left = pad
        grid_right = w - pad
        grid_bottom = h - pad

        cols = 7
        rows = 6
        cell_w = (grid_right - grid_left) / cols
        cell_h = (grid_bottom - grid_top) / rows

        # day-of-week labels
        dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, name in enumerate(dows):
            x = grid_left + i * cell_w + 4
            y = header_h
            c.create_text(x, y, anchor="nw", text=name, font=("Consolas", 9))

        first = first_weekday(cal_year, cal_month)
        total_days = days_in_month(cal_year, cal_month)

        c.day_cells = []
        day_num = 1

        for r in range(rows):
            for col in range(cols):
                index = r * cols + col
                x1 = grid_left + col * cell_w
                y1 = grid_top + r * cell_h
                x2 = x1 + cell_w
                y2 = y1 + cell_h

                c.create_rectangle(x1, y1, x2, y2)

                if index >= first and day_num <= total_days:
                    date_str = f"{cal_year:04d}-{cal_month:02d}-{day_num:02d}"

                    # selection highlight
                    if date_str == selected_date:
                        c.create_rectangle(x1 + 1, y1 + 1, x2 - 1, y2 - 1, width=2)

                    # day number
                    c.create_text(x1 + 4, y1 + 2, anchor="nw", text=str(day_num), font=("Consolas", 10))

                    # tick if logged
                    if is_logged(date_str):
                        c.create_text(x2 - 10, y1 + 2, anchor="ne", text="✓", font=("Consolas", 12, "bold"))

                    c.day_cells.append({"date": date_str, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
                    day_num += 1

    def on_calendar_click(event):
        nonlocal selected_date, pie_mode, pie_week_start

        c = cal_canvas
        if not hasattr(c, "day_cells"):
            return

        x, y = event.x, event.y
        for cell in c.day_cells:
            if cell["x1"] <= x <= cell["x2"] and cell["y1"] <= y <= cell["y2"]:
                selected_date = cell["date"]

                # rule: calendar click forces pie to Day
                pie_mode = "day"

                # also update the pie's week-start so week-mode follows the selected date
                d = backend.datetime.date.fromisoformat(selected_date)
                pie_week_start = week_start_for(d)

                backend.app_print("Selected date:", selected_date)
                draw_calendar()
                draw_pie()
                return

    cal_canvas.bind("<Button-1>", on_calendar_click)

    # Month navigation arrows
    def change_month(delta):
        nonlocal cal_year, cal_month
        cal_month += delta
        if cal_month < 1:
            cal_month = 12
            cal_year -= 1
        elif cal_month > 12:
            cal_month = 1
            cal_year += 1
        draw_calendar()

    btn_next = tk.Button(cal_header, text=">>", width=4, command=lambda: change_month(1))
    btn_next.pack(side="right", padx=(4, 0))

    btn_prev = tk.Button(cal_header, text="<<", width=4, command=lambda: change_month(-1))
    btn_prev.pack(side="right")

    # bar graph data + drawing

    def get_week_calories(week_start_date):
        # returns (labels, values)
        # labels: ["Mon 01", "Tue 02", ...]
        # values: [int or None]  (None = no log)
        labels = []
        values = []

        for i in range(7):
            d = week_start_date + backend.datetime.timedelta(days=i)
            date_str = d.isoformat()

            labels.append(d.strftime("%a %d"))  # Mon 01, Tue 02

            day = backend.kcalendar.get(date_str)
            if not day:
                values.append(None)
                continue

            # sum calories (breakfast/lunch/dinner) ignoring None
            total = 0
            for meal in ["breakfast", "lunch", "dinner"]:
                v = day.get(meal)
                if v is not None:
                    total += v

            values.append(total)

        return labels, values

    def draw_bar_week():
        nonlocal bar_week_start

        c = bar_canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w <= 1 or h <= 1:
            root.after(50, draw_bar_week)
            return

        labels, values = get_week_calories(bar_week_start)
        goal = backend.user_settings.get("calorie_goal")

        # Title
        c.create_text(3, 0, anchor="nw",
                    text=f"Week of {bar_week_start.isoformat()}",
                    font=("Consolas", 10, "bold"))

        # Chart area
        pad_left = 30
        pad_right = 10
        pad_top = 50
        pad_bottom = 28

        x0 = pad_left
        y0 = pad_top
        x1 = w - pad_right
        y1 = h - pad_bottom

        # Find max (avoid divide by zero)
        nums = [v for v in values if v is not None]
        if not nums:
            c.create_text(w // 2, h // 2, text="No week data", font=("Consolas", 10))
            return

        max_day = max(nums)
        max_val = max_day

        # If a goal exists, scale to show it too
        if goal is not None and goal > max_val:
            max_val = goal

        if max_val <= 0:
            max_val = 1

        # Bar sizing
        n = 7
        gap = 8
        bar_w = (x1 - x0 - gap * (n - 1)) / n

        # Axes line
        c.create_line(x0, y1, x1, y1)  # baseline

        

        for i in range(n):
            v = values[i]
            bx1 = x0 + i * (bar_w + gap)
            bx2 = bx1 + bar_w

            # x label
            c.create_text((bx1 + bx2) / 2, y1 + 6, anchor="n", text=labels[i], font=("Consolas", 8))

            # gap if no data
            if v is None:
                c.create_text((bx1 + bx2) / 2, (y0 + y1) / 2, text="—", font=("Consolas", 14))
                continue

            bar_h = (v / max_val) * (y1 - y0)
            top = y1 - bar_h

            c.create_rectangle(bx1, top, bx2, y1, outline="", fill="#7aa2ff")
            label_y = max(top -4, y0 + 2)
            c.create_text((bx1 + bx2) / 2, label_y, anchor="s", text=str(v), font=("Consolas", 8))
        
        
        if goal is not None and goal > 0:
            goal_y = y1 - (goal / max_val) * (y1 - y0)
            c.create_line(x0, goal_y, x1, goal_y, dash=(4, 2))
            c.create_text(x0 - 4, goal_y, anchor="e", text=f"{goal:.0f}", font=("Consolas", 8, "bold"))

    def change_bar_week(delta_weeks):
        nonlocal bar_week_start
        bar_week_start = bar_week_start + backend.datetime.timedelta(days=7 * delta_weeks)
        draw_bar_week()

    btn_bar_prev.config(command=lambda: change_bar_week(-1))
    btn_bar_next.config(command=lambda: change_bar_week(1))
   
   
    def on_bar_click(event=None):
        nonlocal bar_week_start, selected_date
        d = backend.datetime.date.fromisoformat(selected_date)
        bar_week_start = week_start_for(d)
        draw_bar_week()
        backend.app_print("Bar graph set to week of:", bar_week_start.isoformat())
    bar_canvas.bind("<Button-1>", on_bar_click)

    # =========================
    # 6) Pie chart data + drawing + mode buttons
    # =========================
    def get_day_meals(date_str):
        day = backend.kcalendar.get(date_str)
        if not day:
            return [], []
        labels, values = [], []
        for meal in ["breakfast", "lunch", "dinner"]:
            v = day.get(meal)
            if v is not None and v > 0:
                labels.append(meal)
                values.append(v)
        return labels, values

    def get_week_meals_avg(week_start_date):
        totals = {"breakfast": 0, "lunch": 0, "dinner": 0}
        counts = {"breakfast": 0, "lunch": 0, "dinner": 0}

        for i in range(7):
            d = week_start_date + backend.datetime.timedelta(days=i)
            date_str = d.isoformat()
            day = backend.kcalendar.get(date_str)
            if not day:
                continue

            for meal in ["breakfast", "lunch", "dinner"]:
                v = day.get(meal)
                if v is not None and v > 0:
                    totals[meal] += v
                    counts[meal] += 1

        labels, values = [], []
        for meal in ["breakfast", "lunch", "dinner"]:
            if counts[meal] > 0:
                labels.append(meal)
                values.append(totals[meal] / counts[meal])
        return labels, values

    def get_month_meals_avg(year, month):
        totals = {"breakfast": 0, "lunch": 0, "dinner": 0}
        counts = {"breakfast": 0, "lunch": 0, "dinner": 0}

        month_key = f"{year:04d}-{month:02d}"
        for date_str, day in backend.kcalendar.items():
            if not date_str.startswith(month_key) or not day:
                continue
            for meal in ["breakfast", "lunch", "dinner"]:
                v = day.get(meal)
                if v is not None and v > 0:
                    totals[meal] += v
                    counts[meal] += 1

        labels, values = [], []
        for meal in ["breakfast", "lunch", "dinner"]:
            if counts[meal] > 0:
                labels.append(meal)
                values.append(totals[meal] / counts[meal])
        return labels, values

    def draw_pie_generic(labels, values, title=""):
        w = pie_canvas.winfo_width()
        h = pie_canvas.winfo_height()
        if w <= 1 or h <= 1:
            root.after(50, lambda: draw_pie_generic(labels, values, title))
            return

        c = pie_canvas
        c.delete("all")

        if title:
            c.create_text(10, 8, anchor="nw", text=title, font=("Consolas", 10, "bold"))

        if not values:
            c.create_text(w // 2, h // 2, text="No meal data", font=("Consolas", 10))
            return

        total = sum(values)
        cx = w // 2 + 80
        cy = h // 2 - 10
        r = min(w, h) // 2 - 18
        if r <= 5:
            return

        start = 0
        for label, value in zip(labels, values):
            extent = value / total * 360
            if len(values) == 1:
                extent = 359.9

            c.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=start,
                extent=extent,
                fill=meal_colors.get(label, "#cccccc"),
                outline="white"
            )
            start += extent

        # legend
        y = 28
        for label, value in zip(labels, values):
            col = meal_colors.get(label, "#cccccc")
            c.create_rectangle(10, y + 3, 22, y + 15, fill=col, outline="")
            c.create_text(28, y, anchor="nw", text=f"{label}: {value:.0f}")
            y += 18
        # total calories (below legend)
        total_cals = sum(values)
        y += 6
        c.create_line(10, y, 150, y, fill="#888888")
        y += 6
        c.create_text(
            10,
            y,
            anchor="nw",
            text=f"Total: {total_cals:.0f} kcal",
            font=("Consolas", 10, "bold")
        )

    def draw_pie():
        nonlocal pie_mode, pie_week_start, selected_date, cal_year, cal_month

        if pie_mode == "day":
            labels, values = get_day_meals(selected_date)
            draw_pie_generic(labels, values, title=selected_date)
            return

        if pie_mode == "week":
            labels, values = get_week_meals_avg(pie_week_start)
            draw_pie_generic(labels, values, title=f"Week of {pie_week_start.isoformat()}")
            return

        if pie_mode == "month":
            labels, values = get_month_meals_avg(cal_year, cal_month)
            draw_pie_generic(labels, values, title=f"{cal_year:04d}-{cal_month:02d}")
            return

    def set_pie_mode(mode):
        nonlocal pie_mode, pie_week_start, selected_date
        pie_mode = mode

        if mode == "week":
            d = backend.datetime.date.fromisoformat(selected_date)
            pie_week_start = week_start_for(d)

        draw_pie()

    btn_pie_month = tk.Button(pie_header, text="Month", width=6, command=lambda: set_pie_mode("month"))
    btn_pie_week = tk.Button(pie_header, text="Week", width=6, command=lambda: set_pie_mode("week"))
    btn_pie_day = tk.Button(pie_header, text="Day", width=6, command=lambda: set_pie_mode("day"))

    btn_pie_month.pack(side="right", padx=(4, 0))
    btn_pie_week.pack(side="right")
    btn_pie_day.pack(side="right")

    # =========================
    # 7) Startup actions (draw + backend start)
    # =========================
    root.after(100, draw_calendar)
    root.after(150, draw_pie)
    root.after(150, draw_bar_week)

    root.after(0, backend.main_loop)

    write_line("kcalendar GUI — terminal mode")
    root.mainloop()


if __name__ == "__main__":
    main()
