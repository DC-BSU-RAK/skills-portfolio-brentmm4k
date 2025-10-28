import tkinter as tk
import random

class MathQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Quiz")
        self.root.geometry("500x400")
        self.root.configure(bg='#f0f0f0')
        
        self.score = 0 # Empty score variable
        self.current_question = 0 # Empty current question variable
        self.total_questions = 10 # Total number of questions per quiz
        self.current_difficulty = "" # Empty current difficulty variable
        
        """Difficulty questions, using for loops and random numbers to generate questions
            The eval() function is used to compute the answer for each question so that it can be checked later
            The a and b variables generate random numbers within specified ranges for each difficulty level
            The op variable randomly selects either the addition or subtraction operation for each question
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
        
    def show_main_menu(self):
        self.clear_root() # Clears any existing widgets and ensure background is set
        
        # Displays the text on the middle top of the main menu screen
        title_label = tk.Label(self.root, text="DIFFICULTY LEVEL", 
                            font=('Arial', 20, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=30)
        
        # Difficulty buttons, changes the color of the button depending on the difficulty selected
        easy_dif = tk.Button(self.root, text="1. Easy 👍", 
                            font=('Arial', 16), bg='#4CAF50', fg='white',
                            width=15, height=2, command=lambda: self.start_quiz("Easy"))
        easy_dif.pack(pady=10)
        
        moderate_dif = tk.Button(self.root, text="2. Moderate 📝", 
                            font=('Arial', 16), bg='#FF9800', fg='white',
                            width=15, height=2, command=lambda: self.start_quiz("Moderate"))
        moderate_dif.pack(pady=10)
        
        advanced_dif = tk.Button(self.root, text="3. Advanced 🔥", 
                            font=('Arial', 16), bg='#f44336', fg='white',
                            width=15, height=2, command=lambda: self.start_quiz("Advanced"))
        advanced_dif.pack(pady=10)
        
    def clear_root(self):  # Remove all widgets from the root and reset background for new screen
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg='#f0f0f0')

        
    def start_quiz(self, difficulty): # Starts the quiz based on selected difficulty
        self.current_difficulty = difficulty # Set current difficulty
        self.score = 0 # Resets the score before starting a new quiz
        self.current_question = 0 # Sets the current question to the first question
        
        self.clear_root() # Reset UI
        
        # Quiz widgets
        self.difficulty_label = tk.Label(self.root, text=f"Difficulty: {difficulty}", # Displays current difficulty on the top middle of the screen
                                        font=('Arial', 14, 'bold'), bg='#f0f0f0')
        self.difficulty_label.pack(pady=5)
        
        self.question_label = tk.Label(self.root, text="", font=('Arial', 16), # Displays the text for the questions
                                    bg='#f0f0f0', wraplength=450)
        self.question_label.pack(pady=20)
        
        self.answer_entry = tk.Entry(self.root, font=('Arial', 14), justify='center', width=20) # Entry box for users to input their answers
        self.answer_entry.pack(pady=10)
        self.answer_entry.bind('<Return>', lambda event: self.check_answer()) # Allows users to press Enter to submit their answer as an alternative to clicking the button
        
        self.feedback_label = tk.Label(self.root, text="", font=('Arial', 12), bg='#f0f0f0') # Displays feedback for correct and incorrect answers
        self.feedback_label.pack(pady=10)
        
        self.score_label = tk.Label(self.root, text=f"Score: {self.score}/{self.total_questions}", # Displays the current score to the current question
                                font=('Arial', 12), bg='#f0f0f0')
        self.score_label.pack(pady=10)
        
        button_frame = tk.Frame(self.root, bg='#f0f0f0') # Frame for the submit button
        button_frame.pack(pady=10)
        
        self.submit_button = tk.Button(button_frame, text="Submit Answer", # Text for the submit button
                                    command=self.check_answer, # Calls the check_answer method when clicked to check the user's answer
                                    font=('Arial', 12), bg='#2196F3', fg='white', padx=20)
        self.submit_button.pack(pady=5)
        
        self.display_question() # Displays the first question and set up for the quiz screen
        
    def display_question(self): # Displays the current question based on the current question index from the selected difficulty
        if self.current_question < self.total_questions: # Checks if there are remaining questions
            question_text, self.correct_answer = self.questions[self.current_difficulty][self.current_question] # Retrieves the question text as well as the correct answer
            self.question_label.config(text=question_text) # Updates the current question label with the new question text
            self.answer_entry.delete(0, tk.END) # Clears the answer entry box for new input
            self.feedback_label.config(text="") # Clears previous feedback text
            self.answer_entry.focus() # Sets focus to the answer entry box
        else:
            self.show_results() # If there are no remaining questions, shows the results screen
            
    def check_answer(self): # Checks the user's answer from the entry box against the correct answer
        user_answer = self.answer_entry.get() 
        
        try:
            if int(user_answer) == self.correct_answer: # Compares the user's answer to the correct answer
                self.score += 1 # If correct, increments the score by 1
                self.feedback_label.config(text="✓ Correct!", fg="green") # Displays the correct feedback
            else:
                self.feedback_label.config(text=f"✗ Wrong! The answer is {self.correct_answer}", fg="red") # Displays the incorrect feedback
        except ValueError:
            self.feedback_label.config(text="Please enter a valid number.", fg="red") # Prompts user to enter a valid number if input is invalid(i.e., non-numeric)
            return # Exit the method if input is invalid
            
        self.score_label.config(text=f"Score: {self.score}/{self.total_questions}") # Updates the score label after each question
        self.current_question += 1 # Increase the current question index
        
        self.root.after(200, self.display_question) # Adds a slight delay before displaying the next question to allow users to see feedback
            
    def show_results(self):
        self.clear_root() # Clear UI and prepare results when quiz is completed

        percentage = (self.score / self.total_questions) * 100 # Calculate the percentage score for the results screen

        result_label = tk.Label(self.root, text="Quiz Completed!", # Displays "Quiz Completed!" at the middle-top of the results screen
                            font=('Arial', 20, 'bold'), bg='#f0f0f0')
        result_label.pack(pady=20)
        
        score_label = tk.Label(self.root, text=f"Final Score: {self.score}/{self.total_questions}", # Displays the final score at the results screen
                            font=('Arial', 16), bg='#f0f0f0')
        score_label.pack(pady=10)
        
    # Displays a message based on the user's performance of the quiz at the "Results Screen"
        if percentage == 100:
            performance = "Perfect! 🎉"
            color = "#4CAF50"
        elif percentage >= 80:
            performance = "Almost there!"
            color = "#4CAF50"
        elif percentage >= 60:
            performance = "Try again!"
            color = "#FF9800"
        else:
            performance = "Keep practicing!"
            color = "#f44336"
        
        performance_label = tk.Label(self.root, text=performance, # Displays performance message displayed above
                                font=('Arial', 18, 'bold'), bg='#f0f0f0', fg=color)
        performance_label.pack(pady=10)
        
        # Buttons format
        button_frame = tk.Frame(self.root, bg='#f0f0f0') 
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