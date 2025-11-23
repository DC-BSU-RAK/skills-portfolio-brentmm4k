import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
from pathlib import Path

"""
Student Marks Manager GUI
Provides a simple Tkinter interface to load student marks from a
text file, display records, and compute basic statistics (percentage
and grade). The loader attempts sensible paths relative to this
script and falls back to a recursive search for filenames matching
"*student*mark*.txt".

Submitted By: Brent Muli
"""
class StudentManager:
    # Main application class for the student marks GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Student Marks Manager")
        self.root.geometry("800x550")
        self.root.resizable(False, False)  # Prevent window resizing for consistent layout
        # Store the data file path for saving
        self.data_file = None
        # In-memory list of student records (populated by load_data)
        self.students = []
        self.load_data()
        self.create_widgets()
    
    def load_data(self):
        """Load student data from file"""
        # Determine expected locations relative to this script.
        # We try a few likely candidate paths to be resilient to working
        # directory changes and capitalization differences on Windows.
        script_dir = Path(__file__).resolve().parent
        candidates = [
            script_dir / "A1 - Resources" / "studentMarks.txt",
            script_dir / "A1 - Resources" / "studentmarks.txt",
            script_dir / "studentMarks.txt",
            script_dir.parent / "A1 - Resources" / "studentMarks.txt",
        ]

        found = None
        for p in candidates:
            if p.exists():
                found = p
                break

        # Fallback: search for any file matching *student*mark*.txt under script dir
        if found is None:
            for p in script_dir.rglob("*student*mark*.txt"):
                found = p
                break

        if found is None:
            # If no file found, ask user to select one
            found = filedialog.askopenfilename(
                initialdir=script_dir,
                title="Select student marks file",
                filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
            )
            if not found:
                messagebox.showerror("Error", "No student marks file selected.")
                return
            found = Path(found)

        self.data_file = found
        
        try:
            with open(found, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # Skip first line if it contains a numeric count; otherwise start at first record
                start_index = 1 if len(lines) > 0 and lines[0].strip().isdigit() else 0
                for line in lines[start_index:]:
                    data = line.strip().split(',')
                    # Expecting 6 fields per line: code,name,course1,course2,course3,exam
                    if len(data) == 6:
                        try:
                            code = int(data[0])
                            name = data[1]
                            course_marks = [int(data[2]), int(data[3]), int(data[4])]
                            exam_mark = int(data[5])
                        except ValueError:
                            # Skip malformed lines rather than crashing the app
                            continue
                        self.students.append({
                            'code': code,
                            'name': name,
                            'course_marks': course_marks,
                            'exam_mark': exam_mark
                        })
        except Exception as e:
            # Show a friendly error message if reading fails for any reason
            messagebox.showerror("Error", f"Failed reading {found}: {e}")
    
    def save_data(self):
        """Save student data back to the original file"""
        if not self.data_file:
            messagebox.showerror("Error", "No data file path known for saving.")
            return False
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                # Write the count as first line (for file format compatibility)
                file.write(f"{len(self.students)}\n")
                # Write each student as comma-separated values on a new line
                for student in self.students:
                    file.write(f"{student['code']},{student['name']},{student['course_marks'][0]},{student['course_marks'][1]},{student['course_marks'][2]},{student['exam_mark']}\n")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
            return False
    
    def calculate_percentage(self, student):
        """Calculate overall percentage"""
        # Coursework is out of 60 (3 items) and exam out of 100 -> total 160
        total_coursework = sum(student['course_marks'])
        total_marks = total_coursework + student['exam_mark']
        return (total_marks / 160) * 100
    
    def get_grade(self, percentage):
        """Determine grade based on percentage"""
        # Grade boundaries (inclusive lower bounds)
        if percentage >= 70:
            return 'A'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'
    
    def create_widgets(self):
        """Create the GUI interface with output at top and buttons below"""
        # Main frame with padding for consistent spacing around the window
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label at the top
        title_label = ttk.Label(main_frame, text="Student Marks Manager", 
                            font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Output area at the TOP (shows results and summaries)
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text widget with scrollbar for viewing results
        self.output_text = tk.Text(output_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        # Link scrollbar to the text widget so it updates as user scrolls
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame at the BOTTOM (user actions)
        button_frame = ttk.LabelFrame(main_frame, text="Menu Options", padding="10")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Center the button layout by creating a centered container frame
        center_frame = ttk.Frame(button_frame)
        center_frame.pack(expand=True)
        
        # LEFT SIDE: Buttons 1-4 (core functions)
        left_buttons_frame = ttk.Frame(center_frame)
        left_buttons_frame.pack(side=tk.LEFT, padx=10)
        
        # MIDDLE: Student Code Input
        middle_frame = ttk.Frame(center_frame)
        middle_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(middle_frame, text="Student Code:", font=("Arial", 10, "bold")).pack(pady=5)
        self.student_code_entry = ttk.Entry(middle_frame, width=10, font=("Arial", 12))
        self.student_code_entry.pack(pady=5)
        
        # RIGHT SIDE: Buttons 5-8 (extension tasks)
        right_buttons_frame = ttk.Frame(center_frame)
        right_buttons_frame.pack(side=tk.LEFT, padx=10)
        
        # LEFT SIDE: Buttons 1-4
        ttk.Button(left_buttons_frame, text="1. View All Students", 
                command=self.view_all, width=20).pack(padx=5, pady=5)
        
        ttk.Button(left_buttons_frame, text="2. View Individual Student", 
                command=self.view_individual, width=20).pack(padx=5, pady=5)
        
        ttk.Button(left_buttons_frame, text="3. Highest Score", 
                command=self.show_highest, width=20).pack(padx=5, pady=5)
        
        ttk.Button(left_buttons_frame, text="4. Lowest Score", 
                command=self.show_lowest, width=20).pack(padx=5, pady=5)
        
        # RIGHT SIDE: Buttons 5-8 (Extension tasks)
        ttk.Button(right_buttons_frame, text="5. Sort Students", 
                command=self.sort_students, width=20).pack(padx=5, pady=5)
        
        ttk.Button(right_buttons_frame, text="6. Add Student", 
                command=self.add_student, width=20).pack(padx=5, pady=5)
        
        ttk.Button(right_buttons_frame, text="7. Delete Student", 
                command=self.delete_student, width=20).pack(padx=5, pady=5)
        
        ttk.Button(right_buttons_frame, text="8. Update Student", 
                command=self.update_student, width=20).pack(padx=5, pady=5)
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
    
    def display_student_info(self, student):
        """Display information for a single student"""
        total_coursework = sum(student['course_marks'])
        percentage = self.calculate_percentage(student)
        grade = self.get_grade(percentage)
        
        # Format student details as readable text and append to output
        info = (f"Name: {student['name']}\n"
                f"Student Code: {student['code']}\n"
                f"Total Coursework: {total_coursework}/60\n"
                f"Exam Mark: {student['exam_mark']}/100\n"
                f"Overall Percentage: {percentage:.1f}%\n"
                f"Grade: {grade}\n"
                f"{'-'*40}\n")
        
        self.output_text.insert(tk.END, info)
    
    def view_all(self):
        """View all student records"""
        self.clear_output()
        
        if not self.students:
            self.output_text.insert(tk.END, "No student records found.\n")
            return
        
        self.output_text.insert(tk.END, "ALL STUDENT RECORDS\n")
        self.output_text.insert(tk.END, "="*50 + "\n\n")
        
        # Display each student
        for student in self.students:
            self.display_student_info(student)
        
        # Calculate and display summary (average percentage across loaded students)
        total_percentage = sum(self.calculate_percentage(student) for student in self.students)
        average_percentage = total_percentage / len(self.students)
        
        self.output_text.insert(tk.END, f"\nSUMMARY:\n")
        self.output_text.insert(tk.END, f"Number of students: {len(self.students)}\n")
        self.output_text.insert(tk.END, f"Average percentage: {average_percentage:.2f}%\n")
    
    def view_individual(self):
        """View individual student record"""
        if not self.students:
            messagebox.showinfo("Info", "No student records available.")
            return
        
        # Get student code from the entry widget
        try:
            code = int(self.student_code_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid student code (number).")
            return
        
        # Find the student
        found_student = None
        for student in self.students:
            if student['code'] == code:
                found_student = student
                break
        
        if found_student:
            self.clear_output()
            self.output_text.insert(tk.END, "INDIVIDUAL STUDENT RECORD\n")
            self.output_text.insert(tk.END, "="*50 + "\n\n")
            self.display_student_info(found_student)
        else:
            messagebox.showinfo("Not Found", f"No student found with code {code}")
    
    def show_highest(self):
        """Show student with highest overall mark"""
        if not self.students:
            messagebox.showinfo("Info", "No student records available.")
            return
        
        # Find student with highest total marks (coursework + exam)
        highest_student = max(self.students, 
                            key=lambda s: sum(s['course_marks']) + s['exam_mark'])
        
        self.clear_output()
        self.output_text.insert(tk.END, "STUDENT WITH HIGHEST SCORE\n")
        self.output_text.insert(tk.END, "="*50 + "\n\n")
        self.display_student_info(highest_student)
    
    def show_lowest(self):
        """Show student with lowest overall mark"""
        if not self.students:
            messagebox.showinfo("Info", "No student records available.")
            return
        
        # Find student with lowest total marks (coursework + exam)
        lowest_student = min(self.students, 
                        key=lambda s: sum(s['course_marks']) + s['exam_mark'])
        
        self.clear_output()
        self.output_text.insert(tk.END, "STUDENT WITH LOWEST SCORE\n")
        self.output_text.insert(tk.END, "="*50 + "\n\n")
        self.display_student_info(lowest_student)
    
    # EXTENSION TASK METHODS
    
    def sort_students(self):
        """Sort student records by overall percentage"""
        if not self.students:
            messagebox.showinfo("Info", "No student records available.")
            return
        
        # Ask user for sort order
        order = simpledialog.askstring("Sort Order", 
                                    "Enter sort order:\n1 - Ascending\n2 - Descending", 
                                    initialvalue="2")
        
        if order == "1":
            self.students.sort(key=lambda s: self.calculate_percentage(s))
            order_text = "ascending"
        else:
            self.students.sort(key=lambda s: self.calculate_percentage(s), reverse=True)
            order_text = "descending"
        
        # Save the sorted data back to the original file
        if self.save_data():
            # Display sorted results
            self.view_all()
            self.output_text.insert(tk.END, f"\n(Students sorted in {order_text} order by overall percentage)\n")
    
    def add_student(self):
        """Add a new student record directly to the original file"""
        # Create a new top-level (modal) window for the add form
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Student")
        add_window.geometry("400x350")
        add_window.transient(self.root)  # Window stays on top of main window
        add_window.grab_set()  # Make this window modal (blocks interaction with main window)
        
        # Create form labels and entry fields in a grid layout
        ttk.Label(add_window, text="Student Code:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        code_entry = ttk.Entry(add_window)
        code_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(add_window, text="Student Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(add_window)
        name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(add_window, text="Coursework Mark 1 (0-20):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        mark1_entry = ttk.Entry(add_window)
        mark1_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(add_window, text="Coursework Mark 2 (0-20):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        mark2_entry = ttk.Entry(add_window)
        mark2_entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(add_window, text="Coursework Mark 3 (0-20):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        mark3_entry = ttk.Entry(add_window)
        mark3_entry.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(add_window, text="Exam Mark (0-100):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        exam_entry = ttk.Entry(add_window)
        exam_entry.grid(row=5, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def save_student():
            try:
                # Validate inputs - strip whitespace and convert to appropriate types
                code = int(code_entry.get().strip())
                name = name_entry.get().strip()
                mark1 = int(mark1_entry.get())
                mark2 = int(mark2_entry.get())
                mark3 = int(mark3_entry.get())
                exam = int(exam_entry.get())
                
                # Validation checks (range and required field validation)
                if not name:
                    messagebox.showerror("Error", "Student name is required.")
                    return
                
                if mark1 < 0 or mark1 > 20 or mark2 < 0 or mark2 > 20 or mark3 < 0 or mark3 > 20:
                    messagebox.showerror("Error", "Coursework marks must be between 0 and 20.")
                    return
                
                if exam < 0 or exam > 100:
                    messagebox.showerror("Error", "Exam mark must be between 0 and 100.")
                    return
                
                # Check if code already exists (prevent duplicate IDs)
                if any(s['code'] == code for s in self.students):
                    messagebox.showerror("Error", "Student code already exists.")
                    return
                
                # Add new student record to the list
                new_student = {
                    'code': code,
                    'name': name,
                    'course_marks': [mark1, mark2, mark3],
                    'exam_mark': exam
                }
                
                self.students.append(new_student)
                # Save to original file and refresh display if successful
                if self.save_data():
                    add_window.destroy()
                    messagebox.showinfo("Success", "Student added successfully to the original file.")
                    self.view_all()  # Refresh display
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values.")
        
        ttk.Button(add_window, text="Save", command=save_student).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        add_window.columnconfigure(1, weight=1)
    
    def delete_student(self):
        """Delete a student record directly from the original file"""
        if not self.students:
            messagebox.showinfo("Info", "No student records available.")
            return
        
        # Get student code from the entry widget
        try:
            code = int(self.student_code_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid student code (number).")
            return
        
        # Find the student by code
        found_index = -1
        for i, student in enumerate(self.students):
            if student['code'] == code:
                found_index = i
                break
        
        if found_index != -1:
            student_name = self.students[found_index]['name']
            # Ask for confirmation before deleting
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {student_name} (Code: {code})?"):
                deleted_student = self.students.pop(found_index)
                # Save changes directly to original file and refresh display
                if self.save_data():
                    messagebox.showinfo("Success", f"Student {deleted_student['name']} deleted successfully.")
                    self.view_all()  # Refresh display
        else:
            messagebox.showinfo("Not Found", f"No student found with code {code}")
    
    def update_student(self):
        """Update a student record directly in the original file"""
        if not self.students:
            messagebox.showinfo("Info", "No student records available.")
            return
        
        # Get student code from the entry widget
        try:
            code = int(self.student_code_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid student code (number).")
            return
        
        # Find the student by code
        found_index = -1
        for i, student in enumerate(self.students):
            if student['code'] == code:
                found_index = i
                break
        
        if found_index == -1:
            messagebox.showinfo("Not Found", f"No student found with code {code}")
            return
        
        student = self.students[found_index]
        
        # Create a modal update form window with current student data pre-filled
        update_window = tk.Toplevel(self.root)
        update_window.title(f"Update Student: {student['name']}")
        update_window.geometry("400x350")
        update_window.transient(self.root)
        update_window.grab_set()
        
        # Create form with current values pre-populated in entry fields
        ttk.Label(update_window, text="Student Code:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        code_entry = ttk.Entry(update_window)
        code_entry.insert(0, str(student['code']))  # Pre-fill with current code
        code_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(update_window, text="Student Name:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        name_entry = ttk.Entry(update_window)
        name_entry.insert(0, student['name'])
        name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(update_window, text="Coursework Mark 1 (0-20):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        mark1_entry = ttk.Entry(update_window)
        mark1_entry.insert(0, str(student['course_marks'][0]))
        mark1_entry.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(update_window, text="Coursework Mark 2 (0-20):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        mark2_entry = ttk.Entry(update_window)
        mark2_entry.insert(0, str(student['course_marks'][1]))
        mark2_entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(update_window, text="Coursework Mark 3 (0-20):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        mark3_entry = ttk.Entry(update_window)
        mark3_entry.insert(0, str(student['course_marks'][2]))
        mark3_entry.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(update_window, text="Exam Mark (0-100):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        exam_entry = ttk.Entry(update_window)
        exam_entry.insert(0, str(student['exam_mark']))
        exam_entry.grid(row=5, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        def save_changes():
            try:
                # Validate inputs - extract and validate form data
                new_code = int(code_entry.get().strip())
                name = name_entry.get().strip()
                mark1 = int(mark1_entry.get())
                mark2 = int(mark2_entry.get())
                mark3 = int(mark3_entry.get())
                exam = int(exam_entry.get())
                
                # Validation checks (same as add_student)
                if not name:
                    messagebox.showerror("Error", "Student name is required.")
                    return
                
                if mark1 < 0 or mark1 > 20 or mark2 < 0 or mark2 > 20 or mark3 < 0 or mark3 > 20:
                    messagebox.showerror("Error", "Coursework marks must be between 0 and 20.")
                    return
                
                if exam < 0 or exam > 100:
                    messagebox.showerror("Error", "Exam mark must be between 0 and 100.")
                    return
                
                # Check if new code already exists (excluding current student)
                # This allows students to keep their code but prevents duplicates
                if any(s['code'] == new_code and i != found_index for i, s in enumerate(self.students)):
                    messagebox.showerror("Error", "Student code already exists.")
                    return
                
                # Update the student record with new values
                self.students[found_index] = {
                    'code': new_code,
                    'name': name,
                    'course_marks': [mark1, mark2, mark3],
                    'exam_mark': exam
                }
                
                # Save changes directly to text file and refresh display if successful
                if self.save_data():
                    update_window.destroy()
                    messagebox.showinfo("Success", "File has been updated successfully.")
                    self.view_all()  # Refresh display
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid student code.")
        
        ttk.Button(update_window, text="Save Changes", command=save_changes).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        update_window.columnconfigure(1, weight=1)

def main():
    # Standard Tkinter app runner: create the root window and start the event loop
    root = tk.Tk()
    app = StudentManager(root)
    root.mainloop()

if __name__ == "__main__":
    # Only run the app if this file is executed directly (not imported)
    main()