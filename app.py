import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime
from db import Database

class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("University Student Management System")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize database
        self.db = Database()
        
        # Session data
        self.current_user = None
        self.user_type = None  # 'student' or 'lecturer'
        
        # Setup styles
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 12), padding=6)
        self.style.configure("TEntry", font=("Arial", 12))
        
        # Create frames for different screens
        self.frames = {}
        self.create_frames()
        
        # Show welcome screen
        self.show_frame("welcome")
    
    def create_frames(self):
        """Create all frames/screens for the application"""
        # Welcome screen
        welcome_frame = ttk.Frame(self.root, padding="20")
        self.frames["welcome"] = welcome_frame
        
        ttk.Label(welcome_frame, text="Welcome to University Student Management System", 
                 font=("Arial", 16, "bold")).pack(pady=(20, 30))
        
        ttk.Button(welcome_frame, text="Student Login", 
                  command=lambda: self.show_frame("student_login")).pack(pady=10, fill=tk.X)
        ttk.Button(welcome_frame, text="Student Registration", 
                  command=lambda: self.show_frame("student_registration")).pack(pady=10, fill=tk.X)
        ttk.Button(welcome_frame, text="Lecturer Login", 
                  command=lambda: self.show_frame("lecturer_login")).pack(pady=10, fill=tk.X)
        ttk.Button(welcome_frame, text="Exit", 
                  command=self.root.quit).pack(pady=(30, 10), fill=tk.X)
        
        # Student Login
        self.create_student_login_frame()
        
        # Student Registration
        self.create_student_registration_frame()
        
        # Lecturer Login
        self.create_lecturer_login_frame()
        
        # Student Dashboard
        self.create_student_dashboard_frame()
        
        # Lecturer Dashboard
        self.create_lecturer_dashboard_frame()
        
        # Student Details (for lecturers)
        self.create_student_details_frame()
        
        # Update Student Data (for students)
        self.create_update_student_frame()
    
    def show_frame(self, frame_name):
        """Show the specified frame and hide others"""
        for frame in self.frames.values():
            frame.pack_forget()
        
        if frame_name == "student_dashboard" and self.current_user:
            self.load_student_data()
            
        if frame_name == "lecturer_dashboard":
            self.load_all_students()
        
        self.frames[frame_name].pack(fill=tk.BOTH, expand=True)
    
    def create_student_login_frame(self):
        """Create the student login frame"""
        login_frame = ttk.Frame(self.root, padding="20")
        self.frames["student_login"] = login_frame
        
        ttk.Label(login_frame, text="Student Login", 
                 font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.student_username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.student_username_var, width=30).grid(
            column=1, row=1, sticky=tk.W, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.student_password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.student_password_var, show='*', width=30).grid(
            column=1, row=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(column=0, row=3, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Login", command=self.student_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=lambda: self.show_frame("welcome")).pack(
            side=tk.LEFT, padx=5)
    
    def create_lecturer_login_frame(self):
        """Create the lecturer login frame"""
        login_frame = ttk.Frame(self.root, padding="20")
        self.frames["lecturer_login"] = login_frame
        
        ttk.Label(login_frame, text="Lecturer Login", 
                 font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 20))
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.lecturer_username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.lecturer_username_var, width=30).grid(
            column=1, row=1, sticky=tk.W, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.lecturer_password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.lecturer_password_var, show='*', width=30).grid(
            column=1, row=2, sticky=tk.W, pady=5)
        
        # Default credentials notice
        ttk.Label(login_frame, text="Default: admin / admin123", 
                 font=("Arial", 10, "italic")).grid(column=1, row=3, sticky=tk.W, pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.grid(column=0, row=4, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Login", command=self.lecturer_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=lambda: self.show_frame("welcome")).pack(
            side=tk.LEFT, padx=5)
    
    def create_student_registration_frame(self):
        """Create the student registration frame"""
        reg_frame = ttk.Frame(self.root, padding="20")
        self.frames["student_registration"] = reg_frame
        
        ttk.Label(reg_frame, text="Student Registration", 
                 font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 20))
        
        # Registration form
        fields = [
            ("Username", "username_var"),
            ("Password", "password_var", "*"),
            ("Confirm Password", "confirm_password_var", "*"),
            ("Full Name", "name_var"),
            ("Pronouns", "pronouns_var"),
            ("Date of Birth (YYYY-MM-DD)", "dob_var"),
            ("Home Address", "home_address_var"),
            ("Term Time Address (if different)", "term_address_var"),
            ("Emergency Contact Name", "emergency_name_var"),
            ("Emergency Contact Number", "emergency_number_var"),
            ("Course", "course_var")
        ]
        
        # Create variables and entry fields
        self.reg_vars = {}
        row = 1
        
        for field_info in fields:
            field_name = field_info[0]
            var_name = field_info[1]
            
            ttk.Label(reg_frame, text=f"{field_name}:").grid(column=0, row=row, sticky=tk.W, pady=5)
            self.reg_vars[var_name] = tk.StringVar()
            
            # Check if this is a password field
            if len(field_info) > 2 and field_info[2] == '*':
                entry = ttk.Entry(reg_frame, textvariable=self.reg_vars[var_name], show='*', width=30)
            else:
                entry = ttk.Entry(reg_frame, textvariable=self.reg_vars[var_name], width=30)
            
            entry.grid(column=1, row=row, sticky=tk.W, pady=5)
            row += 1
        
        # Buttons
        button_frame = ttk.Frame(reg_frame)
        button_frame.grid(column=0, row=row, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Register", command=self.register_student).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", command=lambda: self.show_frame("welcome")).pack(
            side=tk.LEFT, padx=5)
    
    def create_student_dashboard_frame(self):
        """Create the student dashboard frame"""
        dashboard_frame = ttk.Frame(self.root, padding="20")
        self.frames["student_dashboard"] = dashboard_frame
        
        ttk.Label(dashboard_frame, text="Student Dashboard", 
                 font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 20))
        
        # Welcome message
        self.student_welcome_var = tk.StringVar()
        ttk.Label(dashboard_frame, textvariable=self.student_welcome_var, 
                 font=("Arial", 14)).grid(column=0, row=1, columnspan=2, pady=(0, 20))
        
        # Student data display
        self.student_data_frame = ttk.Frame(dashboard_frame)
        self.student_data_frame.grid(column=0, row=2, columnspan=2, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(dashboard_frame)
        button_frame.grid(column=0, row=3, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Update My Information", 
                  command=lambda: self.show_frame("update_student")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Logout", 
                  command=self.logout).pack(side=tk.LEFT, padx=5)
    
    def create_lecturer_dashboard_frame(self):
        """Create the lecturer dashboard frame"""
        dashboard_frame = ttk.Frame(self.root, padding="20")
        self.frames["lecturer_dashboard"] = dashboard_frame
        
        ttk.Label(dashboard_frame, text="Lecturer Dashboard - All Students", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Search frame
        search_frame = ttk.Frame(dashboard_frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.filter_students())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        # Student list
        list_frame = ttk.Frame(dashboard_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create Treeview
        columns = ("id", "username", "name", "course")
        self.student_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.student_tree.heading("id", text="ID")
        self.student_tree.heading("username", text="Username")
        self.student_tree.heading("name", text="Name")
        self.student_tree.heading("course", text="Course")
        
        # Define columns
        self.student_tree.column("id", width=50, anchor=tk.CENTER)
        self.student_tree.column("username", width=150)
        self.student_tree.column("name", width=200)
        self.student_tree.column("course", width=250)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack Treeview and scrollbar
        self.student_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event to view student details
        self.student_tree.bind("<Double-1>", self.view_student_details)
        
        # Buttons
        button_frame = ttk.Frame(dashboard_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="View Selected Student", 
                  command=self.view_selected_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Logout", 
                  command=self.logout).pack(side=tk.LEFT, padx=5)
    
    def create_student_details_frame(self):
        """Create the student details frame (for lecturer view)"""
        details_frame = ttk.Frame(self.root, padding="20")
        self.frames["student_details"] = details_frame
        
        self.details_header_var = tk.StringVar()
        ttk.Label(details_frame, textvariable=self.details_header_var, 
                 font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 20))
        
        # Student details display
        self.details_frame = ttk.Frame(details_frame)
        self.details_frame.grid(column=0, row=1, columnspan=2, sticky=tk.W)
        
        # Button
        ttk.Button(details_frame, text="Back to All Students", 
                  command=lambda: self.show_frame("lecturer_dashboard")).grid(
            column=0, row=2, columnspan=2, pady=20)
    
    def create_update_student_frame(self):
        """Create the update student data frame"""
        update_frame = ttk.Frame(self.root, padding="20")
        self.frames["update_student"] = update_frame
        
        ttk.Label(update_frame, text="Update Your Information", 
                 font=("Arial", 16, "bold")).grid(column=0, row=0, columnspan=2, pady=(0, 20))
        
        # Update form
        fields = [
            ("Full Name", "update_name_var"),
            ("Pronouns", "update_pronouns_var"),
            ("Date of Birth (YYYY-MM-DD)", "update_dob_var"),
            ("Home Address", "update_home_address_var"),
            ("Term Time Address", "update_term_address_var"),
            ("Emergency Contact Name", "update_emergency_name_var"),
            ("Emergency Contact Number", "update_emergency_number_var"),
            ("Course", "update_course_var")
        ]
        
        # Create variables and entry fields
        self.update_vars = {}
        row = 1
        
        for field_name, var_name in fields:
            ttk.Label(update_frame, text=f"{field_name}:").grid(column=0, row=row, sticky=tk.W, pady=5)
            self.update_vars[var_name] = tk.StringVar()
            ttk.Entry(update_frame, textvariable=self.update_vars[var_name], width=30).grid(
                column=1, row=row, sticky=tk.W, pady=5)
            row += 1
        
        # Buttons
        button_frame = ttk.Frame(update_frame)
        button_frame.grid(column=0, row=row, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save Changes", 
                  command=self.save_student_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Back", 
                  command=lambda: self.show_frame("student_dashboard")).pack(side=tk.LEFT, padx=5)
    
    def register_student(self):
        """Handle student registration"""
        # Get form values
        username = self.reg_vars["username_var"].get().strip()
        password = self.reg_vars["password_var"].get().strip()
        confirm_password = self.reg_vars["confirm_password_var"].get().strip()
        name = self.reg_vars["name_var"].get().strip()
        pronouns = self.reg_vars["pronouns_var"].get().strip()
        dob = self.reg_vars["dob_var"].get().strip()
        home_address = self.reg_vars["home_address_var"].get().strip()
        term_address = self.reg_vars["term_address_var"].get().strip()
        emergency_name = self.reg_vars["emergency_name_var"].get().strip()
        emergency_number = self.reg_vars["emergency_number_var"].get().strip()
        course = self.reg_vars["course_var"].get().strip()
        
        # Validate inputs
        if not all([username, password, confirm_password, name, dob, home_address, 
                    emergency_name, emergency_number, course]):
            messagebox.showerror("Error", "All fields except Pronouns and Term Address are required.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long.")
            return
        
        # Validate date format
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date of Birth must be in YYYY-MM-DD format.")
            return
        
        # Register in database
        success, message = self.db.register_student(
            username, password, name, pronouns, dob, home_address, term_address,
            emergency_name, emergency_number, course
        )
        
        if success:
            messagebox.showinfo("Success", message)
            # Clear form
            for var in self.reg_vars.values():
                var.set("")
            # Go back to welcome screen
            self.show_frame("welcome")
        else:
            messagebox.showerror("Error", message)
    
    def student_login(self):
        """Handle student login"""
        username = self.student_username_var.get().strip()
        password = self.student_password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        
        success, result = self.db.login_student(username, password)
        
        if success:
            self.current_user = result  # student_id
            self.user_type = "student"
            self.student_username_var.set("")
            self.student_password_var.set("")
            self.show_frame("student_dashboard")
        else:
            messagebox.showerror("Login Failed", result)
    
    def lecturer_login(self):
        """Handle lecturer login"""
        username = self.lecturer_username_var.get().strip()
        password = self.lecturer_password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        
        success, result = self.db.login_lecturer(username, password)
        
        if success:
            self.current_user = result  # lecturer_id
            self.user_type = "lecturer"
            self.lecturer_username_var.set("")
            self.lecturer_password_var.set("")
            self.show_frame("lecturer_dashboard")
        else:
            messagebox.showerror("Login Failed", result)
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.user_type = None
        self.show_frame("welcome")
    
    def load_student_data(self):
        """Load and display current student data"""
        if not self.current_user or self.user_type != "student":
            return
        
        student_data = self.db.get_student_data(self.current_user)
        
        if not student_data:
            messagebox.showerror("Error", "Failed to load student data.")
            return
        
        # Clear previous data
        for widget in self.student_data_frame.winfo_children():
            widget.destroy()
        
        # Set welcome message
        self.student_welcome_var.set(f"Welcome, {student_data['name']}!")
        
        # Display student data
        fields = [
            ("Name", student_data['name']),
            ("Pronouns", student_data['pronouns'] or "Not specified"),
            ("Date of Birth", student_data['dob']),
            ("Home Address", student_data['home_address']),
            ("Term Address", student_data['term_address'] or "Same as home address"),
            ("Emergency Contact", f"{student_data['emergency_name']} ({student_data['emergency_number']})"),
            ("Course", student_data['course'])
        ]
        
        row = 0
        for label, value in fields:
            ttk.Label(self.student_data_frame, text=f"{label}:", font=("Arial", 12, "bold")).grid(
                column=0, row=row, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(self.student_data_frame, text=value, font=("Arial", 12)).grid(
                column=1, row=row, sticky=tk.W, pady=5)
            row += 1
        
        # Also populate the update form
        self.update_vars["update_name_var"].set(student_data['name'])
        self.update_vars["update_pronouns_var"].set(student_data['pronouns'] or "")
        self.update_vars["update_dob_var"].set(student_data['dob'])
        self.update_vars["update_home_address_var"].set(student_data['home_address'])
        self.update_vars["update_term_address_var"].set(student_data['term_address'] or "")
        self.update_vars["update_emergency_name_var"].set(student_data['emergency_name'])
        self.update_vars["update_emergency_number_var"].set(student_data['emergency_number'])
        self.update_vars["update_course_var"].set(student_data['course'])
    
    def save_student_changes(self):
        """Save the updated student information"""
        if not self.current_user or self.user_type != "student":
            return
        
        # Get updated data
        name = self.update_vars["update_name_var"].get().strip()
        pronouns = self.update_vars["update_pronouns_var"].get().strip()
        dob = self.update_vars["update_dob_var"].get().strip()
        home_address = self.update_vars["update_home_address_var"].get().strip()
        term_address = self.update_vars["update_term_address_var"].get().strip()
        emergency_name = self.update_vars["update_emergency_name_var"].get().strip()
        emergency_number = self.update_vars["update_emergency_number_var"].get().strip()
        course = self.update_vars["update_course_var"].get().strip()
        
        # Validate required fields
        if not all([name, dob, home_address, emergency_name, emergency_number, course]):
            messagebox.showerror("Error", "All fields except Pronouns and Term Address are required.")
            return
        
        # Validate date format
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date of Birth must be in YYYY-MM-DD format.")
            return
        
        # Update in database
        update_data = {
            'name': name,
            'pronouns': pronouns,
            'dob': dob,
            'home_address': home_address,
            'term_address': term_address,
            'emergency_name': emergency_name,
            'emergency_number': emergency_number,
            'course': course
        }
        
        success, message = self.db.update_student_data(self.current_user, update_data)
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_frame("student_dashboard")
        else:
            messagebox.showerror("Error", message)
    
    def load_all_students(self):
        """Load and display all students for lecturer view"""
        if not self.current_user or self.user_type != "lecturer":
            return
        
        # Clear existing data
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        
        # Get all students
        students = self.db.get_all_students()
        
        # Populate treeview
        for student in students:
            self.student_tree.insert("", tk.END, values=(
                student['id'],
                student['username'],
                student['name'],
                student['course']
            ))
    
    def filter_students(self):
        """Filter students based on search query"""
        search_term = self.search_var.get().lower()
        
        # Clear treeview
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        
        # Get all students
        students = self.db.get_all_students()
        
        # Filter and populate treeview
        for student in students:
            if (search_term in str(student['id']).lower() or
                search_term in student['username'].lower() or
                search_term in student['name'].lower() or
                search_term in student['course'].lower()):
                
                self.student_tree.insert("", tk.END, values=(
                    student['id'],
                    student['username'],
                    student['name'],
                    student['course']
                ))
    
    def view_selected_student(self):
        """View details of selected student"""
        selected_item = self.student_tree.selection()
        if not selected_item:
            messagebox.showinfo("Information", "Please select a student to view.")
            return
        
        # Get student id
        student_id = self.student_tree.item(selected_item[0])['values'][0]
        
        # Display student details
        self.display_student_details(student_id)
    
    def view_student_details(self, event):
        """Handle double-click on student in treeview"""
        selected_item = self.student_tree.selection()
        if not selected_item:
            return
        
        # Get student id
        student_id = self.student_tree.item(selected_item[0])['values'][0]
        
        # Display student details
        self.display_student_details(student_id)
    
    def display_student_details(self, student_id):
        """Display detailed information about a student"""
        student_data = self.db.get_student_data(student_id)
        
        if not student_data:
            messagebox.showerror("Error", "Failed to load student data.")
            return
        
        # Set header
        self.details_header_var.set(f"Student Details: {student_data['name']}")
        
        # Clear previous data
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Display student data
        fields = [
            ("Username", student_data['username']),
            ("Name", student_data['name']),
            ("Pronouns", student_data['pronouns'] or "Not specified"),
            ("Date of Birth", student_data['dob']),
            ("Home Address", student_data['home_address']),
            ("Term Address", student_data['term_address'] or "Same as home address"),
            ("Emergency Contact Name", student_data['emergency_name']),
            ("Emergency Contact Number", student_data['emergency_number']),
            ("Course", student_data['course'])
        ]
        
        row = 0
        for label, value in fields:
            ttk.Label(self.details_frame, text=f"{label}:", font=("Arial", 12, "bold")).grid(
                column=0, row=row, sticky=tk.W, pady=5, padx=(0, 10))
            ttk.Label(self.details_frame, text=value, font=("Arial", 12)).grid(
                column=1, row=row, sticky=tk.W, pady=5)
            row += 1
        
        # Show the details frame
        self.show_frame("student_details")


def main():
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()
    
    # Clean up database connection
    app.db.close()


if __name__ == "__main__":
    main()