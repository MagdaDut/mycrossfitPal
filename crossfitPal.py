import sqlite3

class Database:
    def __init__(self, db_name):
        """
        Initialize the database connection.

        Parameters:
        db_name (str): The name of the SQLite database file.
        """
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()

    def initialize(self):
        """
        Create the necessary tables for the fitness tracker application.
        """
        self.c.execute('''CREATE TABLE IF NOT EXISTS exercise_category (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS workout (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            category_id INTEGER,
                            sets INTEGER,
                            reps INTEGER,
                            FOREIGN KEY(category_id) REFERENCES exercise_category(id))''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS fitness_goal (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            description TEXT NOT NULL)''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS goal_workout (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            goal_id INTEGER,
                            workout_id INTEGER,
                            completed INTEGER DEFAULT 0,
                            FOREIGN KEY(goal_id) REFERENCES fitness_goal(id),
                            FOREIGN KEY(workout_id) REFERENCES workout(id))''')

        self.conn.commit()
        print("Database initialized successfully!")

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

class Category:
    def __init__(self, db):
        """
        Initialize the Category class with a database connection.

        Parameters:
        db (Database): An instance of the Database class.
        """
        self.db = db

    def add(self):
        """
        Add a new exercise category to the database.
        """
        name = input("Enter the name of the exercise category: ")
        try:
            self.db.c.execute("INSERT INTO exercise_category (name) VALUES (?)", (name,))
            self.db.conn.commit()
            print("Exercise category added successfully!")
        except sqlite3.IntegrityError:
            print("Category already exists.")

    def view_all(self):
        """
        View all exercise categories and their associated workouts.
        """
        self.db.c.execute("SELECT * FROM exercise_category")
        categories = self.db.c.fetchall()
        for category in categories:
            print(f"{category[1]}")
            self.db.c.execute("SELECT * FROM workout WHERE category_id = ?", (category[0],))
            workouts = self.db.c.fetchall()
            for workout in workouts:
                print(f"  - {workout[1]}: {workout[3]} sets of {workout[4]} reps")

    def delete(self):
        """
        Delete an exercise category from the database.
        """
        self.view_all()
        name = input("Enter the name of the category to delete: ")
        self.db.c.execute("DELETE FROM exercise_category WHERE name = ?", (name,))
        self.db.conn.commit()
        print("Category deleted successfully!")

    def get_category_id(self, name):
        """
        Get the ID of a category based on its name.

        Parameters:
        name (str): The name of the category.

        Returns:
        int: The ID of the category.
        """
        self.db.c.execute("SELECT id FROM exercise_category WHERE name = ?", (name,))
        category = self.db.c.fetchone()
        return category[0] if category else None

class Workout:
    def __init__(self, db):
        """
        Initialize the Workout class with a database connection.

        Parameters:
        db (Database): An instance of the Database class.
        """
        self.db = db

    def create(self):
        """
        Create a new workout routine with multiple categories, each with a set and rep range, and add it to the database.
        """
        category = Category(self.db)
        workout_name = input("Enter the name of the workout: ")

        while True:
            category.view_all()
            category_name = input("Enter the category name (or 'done' to finish): ")
            if category_name.lower() == 'done':
                break
            category_id = category.get_category_id(category_name)
            if category_id is None:
                print("Category does not exist.")
                continue
            sets = int(input(f"Enter the number of sets for {category_name}: "))
            reps = int(input(f"Enter the number of reps for {category_name}: "))
            self.db.c.execute("INSERT INTO workout (name, category_id, sets, reps) VALUES (?, ?, ?, ?)",
                              (workout_name, category_id, sets, reps))
            self.db.conn.commit()
            print(f"Added {sets} sets of {reps} reps for category '{category_name}' to the workout '{workout_name}'.")

    def view_all(self):
        """
        View all workout routines in the database.
        """
        self.db.c.execute("SELECT * FROM workout")
        workouts = self.db.c.fetchall()
        for workout in workouts:
            print(f"{workout[0]}. {workout[1]}: {workout[3]} sets of {workout[4]} reps")

    def view_progress(self):
        """
        View the progress of all workouts.
        """
        self.db.c.execute("SELECT * FROM workout")
        workouts = self.db.c.fetchall()
        for workout in workouts:
            print(f"{workout[0]}. {workout[1]}: {workout[3]} sets of {workout[4]} reps completed")

    def get_workout_id(self, name):
        """
        Get the ID of a workout based on its name.

        Parameters:
        name (str): The name of the workout.

        Returns:
        int: The ID of the workout.
        """
        self.db.c.execute("SELECT id FROM workout WHERE name = ?", (name,))
        workout = self.db.c.fetchone()
        return workout[0] if workout else None

class FitnessGoal:
    def __init__(self, db):
        """
        Initialize the FitnessGoal class with a database connection.

        Parameters:
        db (Database): An instance of the Database class.
        """
        self.db = db

    def set(self):
        """
        Set a new fitness goal and add it to the database.
        """
        description = input("Enter the fitness goal: ")
        self.db.c.execute("INSERT INTO fitness_goal (description) VALUES (?)", (description,))
        self.db.conn.commit()
        print("Fitness goal set successfully!")

    def add_workouts(self):
        """
        Add workouts to a fitness goal.
        """
        self.view_goals()
        goal_id = int(input("Enter the ID of the goal you want to add workouts to: "))
        workout = Workout(self.db)
        while True:
            workout.view_all()
            workout_name = input("Enter the workout name to add to this goal (or 'done' to finish): ")
            if workout_name.lower() == 'done':
                break
            workout_id = workout.get_workout_id(workout_name)
            if workout_id is None:
                print("Workout does not exist.")
                continue
            self.db.c.execute("INSERT INTO goal_workout (goal_id, workout_id) VALUES (?, ?)",
                              (goal_id, workout_id))
            self.db.conn.commit()
            print(f"Added workout '{workout_name}' to goal ID {goal_id}.")

    def view_goals(self):
        """
        View all fitness goals.
        """
        self.db.c.execute("SELECT * FROM fitness_goal")
        goals = self.db.c.fetchall()
        for goal in goals:
            print(f"{goal[0]}. {goal[1]}")
            self.db.c.execute("SELECT w.name, gw.completed FROM workout w JOIN goal_workout gw ON w.id = gw.workout_id WHERE gw.goal_id = ?", (goal[0],))
            workouts = self.db.c.fetchall()
            for workout in workouts:
                status = "Completed" if workout[1] else "Not completed"
                print(f"  - {workout[0]}: {status}")

    def mark_workout_completed(self):
        """
        Mark a workout in a fitness goal as completed.
        """
        self.view_goals()
        goal_id = int(input("Enter the ID of the goal: "))
        workout_name = input("Enter the name of the workout to mark as completed: ")
        workout = Workout(self.db)
        workout_id = workout.get_workout_id(workout_name)
        if workout_id is None:
            print("Workout does not exist.")
            return
        self.db.c.execute("UPDATE goal_workout SET completed = 1 WHERE goal_id = ? AND workout_id = ?",
                          (goal_id, workout_id))
        self.db.conn.commit()
        print(f"Marked workout '{workout_name}' as completed for goal ID {goal_id}.")

    def view_progress(self):
        """
        View the progress towards all fitness goals.
        """
        self.view_goals()

class Menu:
    def __init__(self, tracker):
        """
        Initialize the Menu class with a FitnessTracker instance.

        Parameters:
        tracker (FitnessTracker): An instance of the FitnessTracker class.
        """
        self.tracker = tracker

    def display(self):
        """
        Display the menu and handle user input to perform the selected action.
        """
        while True:
            print("""
            1. Add exercise category
            2. View exercise by category
            3. Delete exercise by category
            4. Create Workout Routine
            5. View Workout Routine
            6. View Exercise Progress
            7. Set Fitness Goals
            8. Add Workouts to Fitness Goals
            9. Mark Workout Completed in Goal
            10. View Progress towards Fitness Goals
            11. Quit
            """)
            choice = input("Enter your choice: ")
            if choice == '1':
                self.tracker.category.add()
            elif choice == '2':
                self.tracker.category.view_all()
            elif choice == '3':
                self.tracker.category.delete()
            elif choice == '4':
                self.tracker.workout.create()
            elif choice == '5':
                self.tracker.workout.view_all()
            elif choice == '6':
                self.tracker.workout.view_progress()
            elif choice == '7':
                self.tracker.goal.set()
            elif choice == '8':
                self.tracker.goal.add_workouts()
            elif choice == '9':
                self.tracker.goal.mark_workout_completed()
            elif choice == '10':
                self.tracker.goal.view_progress()
            elif choice == '11':
                break
            else:
                print("Invalid choice. Please try again.")

class FitnessTracker:
    def __init__(self, db):
        """
        Initialize the FitnessTracker class with a database connection.

        Parameters:
        db (Database): An instance of the Database class.
        """
        self.db = db
        self.category = Category(db)
        self.workout = Workout(db)
        self.goal = FitnessGoal(db)

if __name__ == "__main__":
    db = Database('crossfit.db')

    # Prompt the user to initialize the database
    initialize = input("Do you want to initialize the database? (yes/no): ").lower()
    if initialize == 'yes':
        db.initialize()

    tracker = FitnessTracker(db)
    menu = Menu(tracker)
    menu.display()

    db.close()
