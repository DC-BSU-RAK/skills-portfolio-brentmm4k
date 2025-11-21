import tkinter as tk
import random
from pathlib import Path
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
# "PIL_AVAILABLE" indicates whether Pillow is installed. When False,
# image-related features (animated background) are skipped so the app
# still runs without the dependency.

"""
Math Quiz App
An interactive Tkinter-based quiz app that tests math skills across
three difficulty levels (Easy, Moderate, Advanced). Generates random addition
and subtraction problems, tracks scores, and provides performance feedback.
Features an animated background image and displays grade/performance messages
at the end of each quiz session.

Submitted by: Brent Muli
"""

class MathQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Quiz")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Load background image from A1 - Resources
        # Build a path relative to this script so resources are found even
        # when the user's working directory is different.
        self.resource_dir = Path(__file__).resolve().parent / "A1 - Resources"
        self.bg_image_path = self.resource_dir / "bg.gif"

        # GIF animation variables (frames are stored as PhotoImage objects)
        # `bg_label` will hold the widget that displays the animated GIF.
        self.bg_frames = []
        self.bg_frame_index = 0
        self.bg_label = None

        # Attempt to load an animated background; if Pillow is missing or
        # the file is not found, the loader will fallback to a solid color.
        self._load_animated_background()
        
        self.score = 0 # Empty score variable
        self.current_question = 0 # Empty current question variable
        self.total_questions = 10 # Total number of questions per quiz
        self.current_difficulty = "" # Empty current difficulty variable
        
        """Difficulty questions:
            Each entry in `self.questions` is a list of tuples (question_text, answer).
            We precompute the numeric answer with `eval()` so checking is a simple
            integer comparison later. The comprehensions below generate 10
            sample questions per difficulty using different numeric ranges.
        """
        self.questions = {
            "Easy": [(f"{a} {op} {b}", eval(f"{a}{op}{b}")) for _ in range(10) 
                for a in [random.randint(1, 9)] 
                for b in [random.randint(1, 9)]
                for op in [random.choice(['+', '-'])]],
            "Moderate": [(f"{a} {op} {b}", eval(f"{a}{op}{b}")) for _ in range(10) 
                for a in [random.randint(10, 99)] 
                for b in [random.randint(10, 99)]
                for op in [random.choice(['+', '-'])]],
            "Advanced": [(f"{a} {op} {b}", eval(f"{a}{op}{b}")) for _ in range(10) 
                for a in [random.randint(1000, 9999)] 
                for b in [random.randint(1000, 9999)]
                for op in [random.choice(['+', '-'])]]
        }
        self.show_main_menu()
    
    def _load_animated_background(self):
        """Load and animate the background GIF using the Stack Overflow method"""
        if not PIL_AVAILABLE:
            return  # Skip if PIL is not available
        
        try:
            # Check if the background image file exists
            if self.bg_image_path.exists():
                # Open the GIF and get all frames
                gif_image = Image.open(self.bg_image_path)
                self.bg_frames = []
                
                # Extract all frames from the GIF
                try:
                    frame_count = 0
                    while True:
                        # Convert frame to PhotoImage and keep reference
                        frame = gif_image.copy().resize((500, 400), Image.Resampling.LANCZOS)
                        photo_frame = ImageTk.PhotoImage(frame)
                        self.bg_frames.append(photo_frame)
                        frame_count += 1
                        gif_image.seek(frame_count)
                except EOFError:
                    # Reached end of GIF frames
                    pass
                
                # Create background label and place it behind other widgets.
                # Keep a reference to PhotoImage frames on the instance (and
                # on the label) so Python doesn't garbage-collect them which
                # would make the image disappear from the GUI.
                self.bg_label = tk.Label(self.root, image=self.bg_frames[0], bg='black')
                self.bg_label.place(x=0, y=0, width=500, height=400)
                # `lower()` sends the background label behind all other widgets
                # so interactive controls remain visible on top of it.
                self.bg_label.lower()
                
                # Start animation
                self._animate_background(0)
                
            else:
                # File not found: print a diagnostic and fall back to a solid
                # background color so the app remains usable.
                print(f"Background GIF not found: {self.bg_image_path}")
        except Exception as e:
            print(f"Error loading animated background: {e}")
            # Fallback to solid color background
            self.root.configure(bg='#3278b4')
    
    def _animate_background(self, frame_index):
        """Update the background animation frame"""
        if hasattr(self, 'bg_label') and self.bg_frames:
            # Update frame
            self.bg_label.configure(image=self.bg_frames[frame_index])
            
            # Calculate next frame index
            next_frame = (frame_index + 1) % len(self.bg_frames)
            
            # Schedule next frame update (typical GIF delay is 100ms)
            self.root.after(100, lambda: self._animate_background(next_frame))
        
    def show_main_menu(self):
        self.clear_root() # Clears any existing widgets and ensure background is set
        
        # Displays the text on the middle top of the main menu screen
        title_label = tk.Label(self.root, text="DIFFICULTY LEVEL", 
                            font=('Comic Sans MS', 20, 'bold'), bg='#3278b4', fg='white', padx=3, pady=2)
        title_label.pack(pady=30)
        
        # Difficulty buttons, changes the color of the button depending on the difficulty selected
        easy_dif = tk.Button(self.root, text="1. Easy 👍", 
                            font=('Arial', 16), bg='#79ADD9', fg='white',
                            width=15, height=2, command=lambda: self.start_quiz("Easy"))
        easy_dif.pack(pady=10)
        
        moderate_dif = tk.Button(self.root, text="2. Moderate 📝", 
                            font=('Arial', 16), bg='#266096', fg='white',
                            width=15, height=2, command=lambda: self.start_quiz("Moderate"))
        moderate_dif.pack(pady=10)
        
        advanced_dif = tk.Button(self.root, text="3. Advanced 🔥", 
                            font=('Arial', 16), bg='#034380', fg='white',
                            width=15, height=2, command=lambda: self.start_quiz("Advanced"))
        advanced_dif.pack(pady=10)
        
    def clear_root(self):  # Remove all widgets from the root and reset background for new screen
        for widget in self.root.winfo_children():
            # Don't destroy the background label if it exists
            if widget != self.bg_label:
                widget.destroy()
        
        # Ensure background is at the bottom
        if self.bg_label:
            self.bg_label.lower()
        
    def start_quiz(self, difficulty): # Starts the quiz based on selected difficulty
        self.current_difficulty = difficulty # Set current difficulty
        self.score = 0 # Resets the score before starting a new quiz
        self.current_question = 0 # Sets the current question to the first question
        
        self.clear_root() # Reset UI
        
        # Quiz widgets
        self.difficulty_label = tk.Label(self.root, text=f"Difficulty: {difficulty}", # Displays current difficulty on the top middle of the screen
                                        font=('Comic Sans MS', 20, 'bold'), bg='#3278b4', fg='white', padx=2, pady=1)
        self.difficulty_label.pack(pady=5)
        
        self.question_label = tk.Label(self.root, text="", font=('Comic Sans MS', 20, 'bold', 'underline'), # Displays the text for the questions
                                    bg='#3278b4', fg='white', wraplength=450, padx=3, pady=2)
        self.question_label.pack(pady=20)
        
        self.answer_entry = tk.Entry(self.root, font=('Arial', 14), justify='center', width=20) # Entry box for users to input their answers
        self.answer_entry.pack(pady=10)
        self.answer_entry.bind('<Return>', lambda event: self.check_answer()) # Allows users to press Enter to submit their answer as an alternative to clicking the button
        
        self.feedback_label = tk.Label(self.root, text="", font=('Comic Sans MS', 12), bg='#3278b4', fg='white', padx=2, pady=1) # Displays feedback for correct and incorrect answers
        self.feedback_label.pack(pady=10)
        
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}/{self.total_questions}", # Displays the current score to the current question
                                font=('Comic Sans MS', 12), bg='#3278b4', fg='white', padx=2, pady=1)
        self.score_label.pack(pady=10)
        
        button_frame = tk.Frame(self.root, bg='') # Frame for the submit button
        button_frame.pack(pady=10)
        
        self.submit_button = tk.Button(button_frame, text="Submit Answer", # Text for the submit button
                                    command=self.check_answer, # Calls the check_answer method when clicked to check the user's answer
                                    font=('Comic Sans MS', 12), bg='#2196F3', fg='white', padx=20)
        self.submit_button.pack(pady=5)
        
        self.display_question() # Displays the first question and set up for the quiz screen
        
    def display_question(self): # Displays the current question based on the current question index from the selected difficulty
        if self.current_question < self.total_questions: # Checks if there are remaining questions
            question_text, self.correct_answer = self.questions[self.current_difficulty][self.current_question] # Retrieves the question text as well as the correct answer
            self.question_label.config(text=question_text) # Updates the current question label with the new question text
            self.answer_entry.delete(0, tk.END) # Clears the answer entry box for new input
            self.feedback_label.config(text="") # Clears previous feedback text
            # Move keyboard focus to the answer entry so users can type immediately
            # and press Enter to submit without clicking the entry first.
            self.answer_entry.focus()
        else:
            self.show_results() # If there are no remaining questions, shows the results screen
            
    def check_answer(self): # Checks the user's answer from the entry box against the correct answer
        user_answer = self.answer_entry.get() 
        
        try:
            if int(user_answer) == self.correct_answer: # Compares the user's answer to the correct answer
                self.score += 1 # If correct, increments the score by 1
                self.feedback_label.config(text="✓ Correct!", fg="#B7FF30") # Displays the correct feedback
            else:
                self.feedback_label.config(text=f"✗ Wrong! The answer is {self.correct_answer}", fg="red") # Displays the incorrect feedback
        except ValueError:
            self.feedback_label.config(text="Please enter a valid number.", fg="red") # Prompts user to enter a valid number if input is invalid(i.e., non-numeric)
            return # Exit the method if input is invalid
            
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}") # Updates the score label after each question
        self.current_question += 1 # Increase the current question index
        
        # Short delay before showing the next question so the feedback is
        # visible briefly. `after` queues the callback on the Tk main loop
        # and does not block the UI thread.
        self.root.after(200, self.display_question)
            
    def show_results(self):
        self.clear_root() # Clear UI and prepare results when quiz is completed

        percentage = (self.score / self.total_questions) * 100 # Calculate the percentage score for the results screen

        result_label = tk.Label(self.root, text="Quiz Completed!", # Displays "Quiz Completed!" at the middle-top of the results screen
                            font=('Comic Sans MS', 20, 'bold'), bg='#3278b4', fg='white', padx=3, pady=2)
        result_label.pack(pady=20)
        
        score_label = tk.Label(self.root, text=f"Final Score: {self.score}/{self.total_questions}", # Displays the final score at the results screen
                            font=('Comic Sans MS', 16), bg='#3278b4', fg='white', padx=2, pady=1)
        score_label.pack(pady=10)
        
    # Displays a message based on the user's performance of the quiz at the "Results Screen"
        if percentage == 100:
            performance = "Perfect! Woohoo 🎉"
            color = "#4CAF50"
        elif percentage >= 80:
            performance = "Almost there!"
            color = "#4CAF50"
        elif percentage >= 60:
            performance = "Try again! You can do better!"
            color = "#FF9800"
        else:
            performance = "Nice try! Keep practicing!"
            color = "#f44336"
        
        performance_label = tk.Label(self.root, text=performance, # Displays performance message displayed above
                                font=('Comic Sans MS', 18, 'bold'), bg='#3278b4', fg=color, padx=3, pady=2)
        performance_label.pack(pady=10)
        
        # Buttons format
        button_frame = tk.Frame(self.root, bg='') 
        button_frame.pack(pady=20)
        
        play_again_button = tk.Button(button_frame, text="Play Again?", # Gives option to play the quiz again
                                command=lambda: self.start_quiz(self.current_difficulty),
                                font=('Arial', 12), bg='#2196F3', fg='white', padx=20)
        play_again_button.pack(side=tk.LEFT, padx=10)
        
        menu_button = tk.Button(button_frame, text="Main Menu", # Gives option to return to the main menu to change difficulty
                            command=self.show_main_menu,
                            font=('Arial', 12), bg='#757575', fg='white', padx=20)
        menu_button.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    quiz = MathQuiz(root)
    root.mainloop()