import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from functools import partial

# --- Constants and Configuration ---
DATA_FILE = 'student_data.json'
GRADES = [
    (90, 'A'), (80, 'B'), (70, 'C'), (0, 'F')
] # (Minimum Average Score, Grade)

# --- Data Persistence Functions (CRUD Operations) ---

def load_data():
    """Loads student data from the JSON file, or returns an empty list if not found."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Data Error", "Could not decode student data file. Starting with empty data.")
            return []
    return []

def save_data(data):
    """Saves the current student data list to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError:
        messagebox.showerror("File Error", "Could not save data to the file.")

# --- Core Business Logic Functions ---

def calculate_grade(average):
    """Calculates the letter grade based on the average score."""
    try:
        average = float(average)
    except (TypeError, ValueError):
        return "N/A"

    for min_score, grade in GRADES:
        if average >= min_score:
            return grade
    return "F" # Fallback for averages below 0

def calculate_performance(student):
    """Calculates attendance percentage, average marks, and final grade for a student."""
    try:
        # 1. Marks Calculation
        math_m = int(student.get('math', 0))
        science_m = int(student.get('science', 0))
        english_m = int(student.get('english', 0))

        total_marks = math_m + science_m + english_m
        average_marks = total_marks / 3.0
        final_grade = calculate_grade(average_marks)

        # 2. Attendance Calculation
        present = int(student.get('present_days', 0))
        total = int(student.get('total_days', 0))
        
        if total > 0:
            attendance_perc = (present / total) * 100
        else:
            attendance_perc = 0.0

        return {
            'total_marks': total_marks,
            'average_marks': f"{average_marks:.2f}",
            'final_grade': final_grade,
            'attendance_perc': f"{attendance_perc:.1f}%"
        }

    except (ValueError, TypeError, ZeroDivisionError) as e:
        # Handles cases where marks/attendance fields are empty or invalid
        return {
            'total_marks': 'N/A',
            'average_marks': 'N/A',
            'final_grade': 'N/A',
            'attendance_perc': 'N/A'
        }


# --- Main Application Class (UI/UX) ---

class StudentManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System - Python/Tkinter UI")
        self.geometry("800x600")
        
        # Configure overall style
        style = ttk.Style(self)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Inter', 10))
        style.configure('TButton', font=('Inter', 10, 'bold'), padding=6, foreground='#333333')
        style.map('TButton', background=[('active', '#e0e0e0')])
        style.configure('Custom.TNotebook', tabposition='nw', background='#ffffff')
        
        self.student_data = load_data()
        self.current_user_id = tk.StringVar()
        
        # Setup Notebook (Tabs) for main layout
        self.notebook = ttk.Notebook(self, style='Custom.TNotebook')
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Initialize Frames for each tab
        self.frame_manage = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.frame_report = ttk.Frame(self.notebook, padding="10 10 10 10")
        
        self.notebook.add(self.frame_manage, text="Student Management (CRUD)")
        self.notebook.add(self.frame_report, text="Performance Report & Grades")
        
        # Build UI for each section
        self.create_manage_ui(self.frame_manage)
        self.create_report_ui(self.frame_report)
        
        # Load and refresh data on startup
        self.refresh_list()

    def create_manage_ui(self, parent):
        """Creates the UI for adding, selecting, and updating student data."""
        # Left Panel: Student List
        list_frame = ttk.LabelFrame(parent, text="Student List", padding="10")
        list_frame.pack(side=tk.LEFT, fill="y", padx=10, pady=10)
        
        self.student_listbox = tk.Listbox(list_frame, width=30, height=25, font=('Inter', 10), bd=2, selectmode=tk.SINGLE)
        self.student_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.student_listbox.bind('<<ListboxSelect>>', self.load_student_details)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.student_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.student_listbox.config(yscrollcommand=scrollbar.set)
        
        # Right Panel: Input Forms
        form_frame = ttk.LabelFrame(parent, text="Details & Update", padding="15")
        form_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)
        
        self.entries = {}
        fields = [
            ("ID", "student_id", True), 
            ("Name", "name", False), 
            ("Math Marks (Max 100)", "math", False), 
            ("Science Marks (Max 100)", "science", False), 
            ("English Marks (Max 100)", "english", False),
            ("Days Present", "present_days", False),
            ("Total Class Days", "total_days", False)
        ]
        
        for i, (label_text, key, is_readonly) in enumerate(fields):
            row_frame = ttk.Frame(form_frame)
            row_frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(row_frame, text=f"{label_text}:", width=20, anchor='w')
            label.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(row_frame, width=30, font=('Inter', 10))
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
            
            if is_readonly:
                entry.config(state='readonly')
            
            self.entries[key] = entry

        # Action Buttons
        button_frame = ttk.Frame(form_frame, padding="10 0 0 0")
        button_frame.pack(fill=tk.X, pady=20)

        # Use partial to pass extra arguments to the command functions
        add_btn = ttk.Button(button_frame, text="Add New Student", command=partial(self.handle_student_action, 'add'))
        add_btn.pack(side=tk.LEFT, expand=True, padx=5)
        
        update_btn = ttk.Button(button_frame, text="Update Data", command=partial(self.handle_student_action, 'update'))
        update_btn.pack(side=tk.LEFT, expand=True, padx=5)
        
        delete_btn = ttk.Button(button_frame, text="Delete Selected", command=partial(self.handle_student_action, 'delete'))
        delete_btn.pack(side=tk.LEFT, expand=True, padx=5)

    def create_report_ui(self, parent):
        """Creates the Treeview UI for displaying the full performance report."""
        # Create a Treeview widget for the report table
        self.report_tree = ttk.Treeview(parent, columns=('ID', 'Name', 'Math', 'Science', 'English', 'Total Marks', 'Average', 'Attendance %', 'Final Grade'), show='headings')
        
        # Define column headings and widths (UI/UX enhancement)
        columns_config = {
            'ID': (80, 'center'), 'Name': (150, 'w'), 'Math': (70, 'center'), 
            'Science': (70, 'center'), 'English': (70, 'center'), 'Total Marks': (90, 'center'), 
            'Average': (80, 'center'), 'Attendance %': (100, 'center'), 'Final Grade': (80, 'center')
        }
        
        for col, (width, anchor) in columns_config.items():
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=width, anchor=anchor)

        # Add scrollbar
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.report_tree.yview)
        vsb.pack(side='right', fill='y')
        self.report_tree.configure(yscrollcommand=vsb.set)
        
        self.report_tree.pack(expand=True, fill='both')
        
        # Button to refresh the report
        ttk.Button(parent, text="Refresh Report Data", command=self.populate_report_tree).pack(pady=10)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    # --- Event Handlers ---
    
    def on_tab_change(self, event):
        """Refreshes the report when the report tab is selected."""
        selected_tab = self.notebook.index(self.notebook.select())
        if selected_tab == 1: # Index of the Report tab
            self.populate_report_tree()

    def get_student_data_from_ui(self):
        """Extracts data from the entry fields and validates it."""
        data = {}
        required_fields = ['student_id', 'name']
        numeric_fields = ['math', 'science', 'english', 'present_days', 'total_days']
        
        # 1. Collect all data
        for key, entry in self.entries.items():
            # Temporarily set to normal to read, then back to readonly if needed
            if key == 'student_id' and entry.cget('state') == 'readonly':
                entry.config(state='normal')
                data[key] = entry.get().strip()
                entry.config(state='readonly')
            else:
                data[key] = entry.get().strip()

        # 2. Validation
        for field in required_fields:
            if not data[field]:
                messagebox.showwarning("Input Error", f"The '{field}' field cannot be empty.")
                return None
        
        for field in numeric_fields:
            value = data.get(field, '0')
            if not value.isdigit() or int(value) < 0:
                messagebox.showwarning("Input Error", f"'{field}' must be a non-negative number.")
                return None
            
            # Additional validation for marks/days
            num_val = int(value)
            if field in ['math', 'science', 'english'] and num_val > 100:
                messagebox.showwarning("Input Error", f"'{field}' marks cannot exceed 100.")
                return None
            if field == 'present_days' and num_val > int(data.get('total_days', 0)):
                 messagebox.showwarning("Input Error", "Days Present cannot exceed Total Class Days.")
                 return None

        # 3. Convert numbers to strings for JSON serialization and return
        return data

    def handle_student_action(self, action):
        """Handles Add, Update, and Delete actions."""
        
        if action == 'add':
            new_student = self.get_student_data_from_ui()
            if not new_student: return
            
            # Check for unique ID
            if any(s['student_id'] == new_student['student_id'] for s in self.student_data):
                messagebox.showwarning("Duplicate ID", "A student with this ID already exists.")
                return
            
            self.student_data.append(new_student)
            messagebox.showinfo("Success", f"Student '{new_student['name']}' added successfully.")
            self.clear_entries()
            
        elif action == 'update':
            # Only proceed if a student is selected (i.e., the ID is read-only)
            selected_id = self.entries['student_id'].get()
            if not selected_id:
                messagebox.showwarning("Selection Error", "Please select a student from the list to update.")
                return
            
            updated_student = self.get_student_data_from_ui()
            if not updated_student: return
            
            # Find and update the record
            for i, student in enumerate(self.student_data):
                if student['student_id'] == selected_id:
                    self.student_data[i] = updated_student
                    messagebox.showinfo("Success", f"Student '{updated_student['name']}' updated successfully.")
                    break
            self.clear_entries()
            
        elif action == 'delete':
            selected_indices = self.student_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Selection Error", "Please select a student to delete.")
                return
                
            index_to_delete = selected_indices[0]
            student_name = self.student_data[index_to_delete]['name']
            
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{student_name}'?"):
                del self.student_data[index_to_delete]
                messagebox.showinfo("Success", f"Student '{student_name}' deleted.")
                self.clear_entries()
            
        save_data(self.student_data)
        self.refresh_list()
        self.populate_report_tree() # Refresh report immediately

    def refresh_list(self):
        """Clears and re-populates the student listbox."""
        self.student_listbox.delete(0, tk.END)
        for student in self.student_data:
            self.student_listbox.insert(tk.END, f"{student['student_id']} - {student['name']}")

    def load_student_details(self, event):
        """Loads selected student data into the input forms."""
        selected_indices = self.student_listbox.curselection()
        if not selected_indices:
            self.clear_entries()
            return
            
        index = selected_indices[0]
        student = self.student_data[index]

        self.clear_entries() # Clear first to reset states
        
        # Populate entries
        for key, entry in self.entries.items():
            value = student.get(key, '') # Use .get with default empty string
            
            # Handle the ID field (set to normal, insert value, set back to readonly)
            if key == 'student_id':
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, value)
                entry.config(state='readonly')
            else:
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def clear_entries(self):
        """Clears all input fields and resets the ID field state."""
        for key, entry in self.entries.items():
            if key == 'student_id':
                # ID field needs to be editable for adding new students
                entry.config(state='normal') 
                entry.delete(0, tk.END)
            else:
                entry.delete(0, tk.END)
        
        # After clearing, the ID field is ready for a new entry (editable)
        # If the user clicks 'Update', load_student_details will set it to readonly.
        
    def populate_report_tree(self):
        """Populates the Report Treeview with calculated performance data."""
        # Clear existing data
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
            
        # Insert new data
        for student in self.student_data:
            performance = calculate_performance(student)
            
            row_data = (
                student.get('student_id', 'N/A'),
                student.get('name', 'N/A'),
                student.get('math', '0'),
                student.get('science', '0'),
                student.get('english', '0'),
                performance['total_marks'],
                performance['average_marks'],
                performance['attendance_perc'],
                performance['final_grade']
            )
            
            # Tag the row for color coding grades (UI/UX enhancement)
            tag = 'default'
            if performance['final_grade'] == 'A': tag = 'grade_a'
            elif performance['final_grade'] == 'F': tag = 'grade_f'
            
            self.report_tree.insert('', tk.END, values=row_data, tags=(tag,))

        # Configure tags for row colors (better visual distinction)
        self.report_tree.tag_configure('grade_a', background='#e6ffe6', foreground='#006600') # Light Green
        self.report_tree.tag_configure('grade_f', background='#ffe6e6', foreground='#cc0000') # Light Red
        self.report_tree.tag_configure('default', background='#ffffff')


if __name__ == "__main__":
    app = StudentManagementApp()
    app.mainloop()