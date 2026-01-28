import json
import os
import sys
import datetime
MEALS = ["breakfast", "lunch", "dinner"]
BURNT_KEY = "burnt"
PROTEIN_KEY = "protein"
WEIGHT_KEY = "weight"
DAY_KEYS = MEALS + [BURNT_KEY, PROTEIN_KEY, WEIGHT_KEY]
APP_RUNNING = True

def app_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
    
BASE_DIR = app_path()
DATA_FILE = os.path.join(BASE_DIR, "kcalendar.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "user_settings.json")

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        kcalendar = json.load(f)
else:
    kcalendar = {}


def app_print(text):
    print(text)


def app_input(prompt):
    return input(prompt)


def handle_command(cmd: str):
    pass



def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as u:
            settings = json.load(u)
            if not isinstance(settings, dict):
                settings = {}
    else:
        settings = {}

    settings.setdefault("calorie_goal", None)
    settings.setdefault("protein_goal", None)
    settings.setdefault("weight_goal", None)

    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as u:
        json.dump(settings, u, indent=2)

user_settings = load_settings()

def ensure_day(date_str):
    if date_str not in kcalendar or kcalendar[date_str] is None:
        kcalendar[date_str] = {}
    day = kcalendar[date_str]
    for key in DAY_KEYS:
        if key not in day:
            day[key] = None
    return day

def setting_menu(user_settings):
    app_print("__________________________________________")
    app_print("entering settings (type 'back' to return)")
    app_print("what do you want to change? (calorie goal, protein goal, weight goal)")
    while True:
        option = app_input("input: ").strip().lower().replace(" ", "-")

        if option in ["back", "quit", "stop"]:
            app_print("leaving settings.")
            return user_settings

        if option == "calorie-goal":
            user_settings = set_goal(user_settings)
            seperator()
        elif option == "protein-goal":
            user_settings = set_protein_goal(user_settings)
            seperator()
        elif option == "weight-goal":
            user_settings = set_weight_goal(user_settings)
            seperator()
        else:
            app_print("valid options: calorie goal, protein goal, weight goal, back")

def set_goal(user_settings):
    cgoal = check_na("what is your current calorie goal? ")

    if cgoal == "QUIT":
        app_print("goal unchanged.")
        return user_settings

    user_settings["calorie_goal"] = cgoal
    save_settings(user_settings)

    if cgoal is None:
        app_print("calorie goal (no goal).")
    else:
        app_print(f"awesome! your calorie goal is now set: {cgoal}")

    return user_settings

def set_protein_goal(user_settings):
    prgoal = check_na("what is your current protein goal? ")

    if prgoal == "QUIT":
        app_print("goal unchanged")
        seperator()
        return user_settings

    user_settings["protein_goal"] = prgoal
    save_settings(user_settings)

    if prgoal is None:
        seperator()
        app_print("protein goal removed (no goal).")
    else:
        seperator()
        app_print(f"awesome! your protein goal is now set: {prgoal}")

def set_weight_goal(user_settings):
    wgoal = weight_na("what is your current weight goal? ")

    if wgoal == "QUIT":
        app_print("goal unchanged")
        seperator()
        return user_settings

    user_settings["weight_goal"] = wgoal
    save_settings(user_settings)

    if wgoal is None:
        seperator()
        app_print("weight goal removed (no goal).")
    else:
        seperator()
        app_print(f"awesome! your weight goal is now set: {wgoal}")

def seperator():
    app_print("__________________________________________")
    app_print("anything else you would like to do?")

def total_cal(day):
    tcal = sum(day[meal] for meal in MEALS if day[meal] is not None)
    return tcal

def compare_to_goal(value, user_settings):
    
    goal = user_settings.get("calorie_goal")
    if goal is None:
        return

    diff = value - goal 
    if diff > 0:
        app_print(f"{diff:.0f} over goal ({goal}) — try to stay conscious of what/how much you eat.")
    elif diff < 0:
        app_print(f"{abs(diff):.0f} under goal ({goal}) — nice job staying on track.")
    else:
        app_print(f"exactly on goal ({goal}).")

def compare_weight_goal(value, user_settings):
    goal = user_settings.get("weight_goal")
    if goal is None:
        return

    diff = value - goal 
    if diff > 0:
        app_print(f"{diff:.1f}kg over your goal of {goal}kg")
    elif diff < 0:
        app_print(f"{abs(diff):.1f}kg under your goal of {goal}kg")
    else:
        app_print(f"exactly on goal ({goal}).")

def check_na(prompt):
    while True:
        raw = app_input(prompt)
        raw_nom = raw.lower().strip()
        try:
        
            if raw_nom == "" or raw_nom == "na":
                val = None 
                return val
            elif raw_nom == "quit" or raw_nom == "stop":
                val = "QUIT"
                return val
            else:
                val = int(raw_nom)
                return val
        except ValueError:
            app_print("only enter a number value or na")
            continue

def weight_na(prompt):
    while True:
        raw = app_input(prompt)
        raw_nom = raw.lower().strip()
        try:
        
            if raw_nom == "" or raw_nom == "na":
                val = None 
                return val
            elif raw_nom == "quit" or raw_nom == "stop":
                val = "QUIT"
                return val
            craw_nom = float(raw_nom)
            if craw_nom == 0 or craw_nom < 0:
                app_print("value must be above 0")
                continue
            else:
                return craw_nom
        except ValueError:
            app_print("only enter a number value or na")
            continue

def goal_hit(protein, protein_goal):

    if protein_goal is None:
        return
    if protein is None:
        hit = None
    elif protein >= protein_goal:
        hit = True
    else:
        hit = False

    return hit
      

def log_update():
    date = app_input("what day are we logging? YYYY-MM-DD: ").strip().replace(" ", "-")
    if date in kcalendar:
            while True:
                app_print("************************************************************************")
                answer = app_input("you already have a log for this day, do you want to overwrite it? y/n ").lower().strip()
                app_print("************************************************************************")
                if answer == "y" or answer == "yes":
                    break
                elif answer =="n" or answer == "no":
                    return 
                else:
                    app_print("please enter: yes/no ")
                    continue
                
    brk_val = check_na("calories for breakfast: ")
    if brk_val == "QUIT":
        return
    lun_val = check_na("calories for lunch: ")
    if lun_val == "QUIT":
        return
    din_val = check_na("calories for dinner: ")
    if din_val == "QUIT":
        return
    pro_val = check_na("total protein for this day: ")
    if pro_val == "QUIT":
        return
    burn_val = check_na("calories burnt: ")
    if burn_val == "QUIT":
        return
    weight_val = weight_na("weight this day: ")
    if weight_val == "QUIT":
        return

    day_data = {"breakfast":brk_val,
                 "lunch":lun_val,
                   "dinner":din_val,
                    "protein":pro_val,
                     "burnt":burn_val,
                     "weight":weight_val}
    kcalendar[date] = day_data
    print(kcalendar)
    with open(DATA_FILE, "w") as f:
        json.dump(kcalendar, f, indent=2, sort_keys=True)

def update_today():
    today = datetime.date.today().isoformat()
    day = ensure_day(today)

    app_print("__________________________________________________________________________")
    app_print(f"Updating today: {today}")
    app_print("Only asking for missing entries. press enter to skip, 'quit' to exit.")
    

    prompts = {
        "breakfast": "calories for breakfast: ",
        "lunch": "calories for lunch: ",
        "dinner": "calories for dinner: ",
        "protein": "total protein for today: ",
        "burnt": "calories burnt: ",
         }
    weight_prompt = "current weight: "
    for key in ["breakfast", "lunch", "dinner", "protein", "burnt",]:
        if day.get(key) is None:
            val = check_na(prompts[key])
            if val == "QUIT":
                return

            if val is not None:
                day[key] = val
    if day.get("weight") is None:
        wval = weight_na(weight_prompt)
        if wval == "QUIT":
            return
        if wval is not None:
            day["weight"] = wval


    with open(DATA_FILE, "w") as f:
        json.dump(kcalendar, f, indent=2, sort_keys=True)

    tcal = total_cal(day)
    app_print("____________________________")
    app_print("Saved.")
    app_print(today)
    app_print(f"total calories: {tcal}")
    if day.get(PROTEIN_KEY) is not None:
        app_print(f"total protein: {day.get(PROTEIN_KEY)}")
    if day.get(BURNT_KEY) is not None:
        app_print(f"burnt calories: {day.get(BURNT_KEY)}")
    if day.get(WEIGHT_KEY) is not None:
        app_print(f"current weight: {day.get(WEIGHT_KEY)}kg")

def view_day():
    app_print("________________________________________")
    app_print("entering viewing mode, to exit type quit")
    app_print("________________________________________")
    app_print("what day would you like to view?")
    
    while True: 
        date = app_input("date: ").strip().replace(" ", "-")
        
        if date in ["quit", "stop", "back"]:
            app_print("exiting")
            break
        
        if date not in kcalendar:
            app_print("__________________________________")
            app_print("there is no log for this day")
            continue
        

        elif date in kcalendar:
            day = ensure_day(date)
            protein_goal = user_settings.get("protein_goal")
            protein = day.get("protein")
            tcal = total_cal(day)
            weight_goal = user_settings.get("weight_goal")
            weight = day.get("weight")
            app_print("__________________________________")
            app_print(date)
            app_print (f"total calories: {tcal}")
            compare_to_goal(tcal, user_settings)
            
            hit = goal_hit(protein, protein_goal)
            if protein_goal is None:
                app_print("enter a protein goal to see if you are getting enough protein")
            if protein_goal is not None:
                if hit == True:
                    app_print(f"you hit your protein goal of {protein_goal}g: {protein}g")
                    app_print(f"that's", protein-protein_goal,"grams over goal")
                elif hit is None:
                    app_print("no protein was logged for this day")
                else:
                    app_print(f"you did not hit your protein goal of {protein_goal}g: {protein}g")
                    app_print(f"that's", protein-protein_goal,"under goal")
                        
            burnt = day.get(BURNT_KEY)
            if burnt is not None:
                app_print(f"burnt calories: {burnt}")

            if weight is not None:
                app_print(f"weight for this day: {weight}kg")
                if weight_goal is not None:
                    weight_dif = weight - weight_goal
                    if weight_dif > 0:
                        app_print(f"you have {weight_dif:.1f}kg to lose")
                    elif weight_dif < 0:
                        app_print(f"you have {abs(weight_dif):.1f}kg to gain")
                    else:
                        app_print("you are perfectly on your weight goal!")

            else:
                app_print("no weight logged this day")
            
            app_print("__________________________________________________________")
            app_print("would you like to view another day? type quit to leave")
            
            
            continue

def view_week():
    app_print("__________________________________________")
    app_print("entering viewing mode, to exit type quit")
    app_print("what day do you want to start at?")
    protein_goal = user_settings.get("protein_goal")
    weight_goal = user_settings.get("weight_goal")
    
    while True:
        
        date_start = app_input("date: ").strip().replace(" ", "-")
        if date_start in ["quit", "stop", "back"]:
            app_print("exiting")
            break

        if date_start not in kcalendar:
            app_print("there is no log for this day")
            continue

        elif date_start in kcalendar:
            start_weight = None
            finish_weight = None
            protein_logged = 0
            protein_hit = 0
            start_cal = datetime.date.fromisoformat(date_start)
            tcal_list = []
            protein_list = []
            
            for i in range(7):
                current_date = start_cal + datetime.timedelta(days=i)
                date_str = current_date.isoformat()
                day = kcalendar.get(date_str)
                
                if day is None:
                    app_print("__________________________________")
                    app_print(f"no log for {date_str}")
                    continue
                else:
                    day = ensure_day(date_str)
                
                protein = day.get("protein")
                if protein_goal is not None and protein is not None:
                    protein_logged += 1
                    protein_list.append(protein)
                    if protein >= protein_goal:
                        protein_hit += 1
                
                weight = day.get("weight")

                if start_weight is None and weight is not None:
                    start_weight = weight
                if weight is not None:
                    finish_weight = weight
                

                tcal = total_cal(day)
                tcal_list.append(tcal)
                app_print("__________________________________")
                app_print(date_str)
                app_print(f"total calories: {tcal}")
                if protein is not None:
                    app_print(f"protein: {protein}g")
                burnt = day.get(BURNT_KEY)
                if burnt is not None:
                    app_print(f"burnt calories: {burnt}")
                if weight is not None:
                    app_print(f"weight: {weight}kg")
                if weight is not None and weight_goal is not None:
                    compare_weight_goal(weight, user_settings)
                    
            calorie_avg = sum(tcal_list)/len(tcal_list)
            app_print("_______________________________________________")
            app_print(f"average calories for days logged: {calorie_avg:.1f}")
            compare_to_goal(calorie_avg, user_settings)
            if protein_goal is not None and len(protein_list) > 0:
                protein_avg = sum(protein_list)/len(protein_list)
                app_print(f"you hit your protein goal for {protein_hit}/{protein_logged} logged days")
                app_print(f"average protein logged was {protein_avg:.1f}g")
            elif protein_goal is not None and len(protein_list) == 0:
                app_print("you didn't log any protein this week")
            else:
                app_print("set a protein goal to see if you are eating enough protein")
            if start_weight is not None and finish_weight is not None:
                dif_weight = start_weight-finish_weight
                app_print(f"started at {start_weight}kg, finished at {finish_weight}kg")
                if dif_weight >0:
                    app_print(f"you lost {abs(dif_weight):.1f}kg")
                elif dif_weight <0:
                    app_print(f"you gained {abs(dif_weight):.1f}kg")
                else:
                    app_print("your weight did not change this week")
            app_print("_______________________________________________")
            app_print("want to check another week? type quit to leave")
            continue

def view_month():
    month_key = app_input("what month would you like to view (YYYY MM): ").strip().replace(" ", "-")

    weekly_totals = {1: [], 2: [], 3: [], 4: [], 5: []}
    week_start_weight = {1: None, 2: None, 3: None, 4: None, 5: None}
    week_finish_weight = {1: None, 2: None, 3: None, 4: None, 5: None}

    month_total = []

    protein_goal = user_settings.get("protein_goal")
    protein_list = []
    protein_logged = 0
    protein_hit = 0

    weight_goal = user_settings.get("weight_goal")


    month_start_weight = None
    month_finish_weight = None

    app_print("____________________________________")


    for date_str in sorted(kcalendar):
        if not date_str.startswith(month_key):
            continue

        dt = datetime.date.fromisoformat(date_str)
        day_num = dt.day
        week_num = (day_num - 1) // 7 + 1

        daydict = ensure_day(date_str)


        tcal = total_cal(daydict)
        weekly_totals[week_num].append(tcal)
        month_total.append(tcal)


        protein = daydict.get("protein")
        if protein_goal is not None and protein is not None:
            protein_logged += 1
            protein_list.append(protein)
            if protein >= protein_goal:
                protein_hit += 1


        weight = daydict.get("weight")
        if weight is not None:

            if month_start_weight is None:
                month_start_weight = weight
            month_finish_weight = weight


            if week_start_weight[week_num] is None:
                week_start_weight[week_num] = weight
            week_finish_weight[week_num] = weight


    for week in range(1, 6):
        totals = weekly_totals[week]

        app_print("___________________________________________")
        app_print(f"week {week}")

        if not totals:
            app_print("no data received for this week")
            app_print("___________________________________________")
            continue

        week_avg = sum(totals) / len(totals)


        app_print(f"days logged: {len(totals)}")


        app_print(f"week {week} average calories: {week_avg:.1f}")


        compare_to_goal(week_avg, user_settings)


        sw = week_start_weight[week]
        fw = week_finish_weight[week]
        if sw is None or fw is None:
            app_print("weight change: not enough weight logs this week")
        else:
            change = fw - sw  
            if change > 0:
                app_print(f"weight change: gained {abs(change):.1f}kg (start {sw}kg → end {fw}kg)")
            elif change < 0:
                app_print(f"weight change: lost {abs(change):.1f}kg (start {sw}kg → end {fw}kg)")
            else:
                app_print(f"weight change: no change (start {sw}kg → end {fw}kg)")


            if weight_goal is None:
                app_print("set a weight goal to see goal progress")
            else:
                compare_weight_goal(fw, user_settings)

        app_print("___________________________________________")

    
    app_print("===========================================")
    app_print(f"month summary: {month_key}")

    if not month_total:
        app_print("no data received for this month")
        app_print("===========================================")
        return

    month_avg = sum(month_total) / len(month_total)
    app_print(f"average calories for this month: {month_avg:.1f}")
    compare_to_goal(month_avg, user_settings)

    
    if month_start_weight is not None and month_finish_weight is not None:
        change = month_finish_weight - month_start_weight
        if change > 0:
            app_print(f"month weight change: gained {abs(change):.1f}kg (start {month_start_weight}kg → end {month_finish_weight}kg)")
        elif change < 0:
            app_print(f"month weight change: lost {abs(change):.1f}kg (start {month_start_weight}kg → end {month_finish_weight}kg)")
        else:
            app_print(f"month weight change: no change (start {month_start_weight}kg → end {month_finish_weight}kg)")
        if weight_goal is not None:
            compare_weight_goal(month_finish_weight, user_settings)
        else:
            app_print("set a weight goal to see goal progress")
    else:
        app_print("month weight change: no weight logged this month")


    if protein_goal is not None and protein_logged > 0:
        protein_avg = sum(protein_list) / len(protein_list)
        app_print(f"protein goal hit: {protein_hit}/{protein_logged} logged days")
        app_print(f"average protein logged: {protein_avg:.1f}g")
    elif protein_goal is not None and protein_logged == 0:
        app_print("you didn't log any protein this month")
    else:
        app_print("set a protein goal to see if you are eating enough protein")

    app_print("===========================================")



def main_loop():
    global APP_RUNNING
    app_print("what would you like to do?")
    global user_settings
    while APP_RUNNING:
        app_print("__________________________________________")
        response = app_input("options: (log, update, view, settings, quit): ").strip().lower()
        
        if response == "log":
            log_update()
            seperator()

        elif response == "update":
            update_today()
            seperator()
        
        elif response == "settings":
            user_settings = setting_menu(user_settings)
        
        elif response == "view":
            length = app_input("what would you like to view? (day/week/month): ").strip().lower()
            if length == "day":
                view_day()
                seperator()

            if length == "week":
                view_week()
                seperator()

            if length == "month":
                view_month()
                seperator()

        elif response == "quit":
            APP_RUNNING = False
            break


if __name__ == "__main__":
    main_loop()