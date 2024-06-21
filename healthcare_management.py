import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# Function to connect to the database
def connect_db():
    return sqlite3.connect('healthcare.db')

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    conn = connect_db()
    cursor = conn.cursor()

    # Check if user exists and password is correct
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    if user:
        role = user[3]
        open_dashboard(username, role, conn, cursor)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to open dashboard based on role
def open_dashboard(username, role, conn, cursor):
    root.withdraw()  # Hide login window

    if role.lower() == "admin":
        admin_dashboard(username, conn, cursor)
    elif role.lower() == "patient":
        patient_dashboard(username, conn, cursor)
    elif role.lower() == "doctor":
        doctor_dashboard(username, conn, cursor)
    else:
        messagebox.showerror("Role Error", f"Unknown role: {role}")

# Admin dashboard
def admin_dashboard(username, conn, cursor):
    admin_window = tk.Toplevel(root)
    admin_window.title(f"Admin Dashboard - {username}")
    admin_window.geometry("600x400")  # Set window size

    def add_patient():
        patient_id = simpledialog.askstring("Add Patient", "Enter patient username:")
        if patient_id:
            # Check if patient already exists
            cursor.execute('SELECT * FROM patients WHERE username=?', (patient_id,))
            existing_patient = cursor.fetchone()
            
            if not existing_patient:
                # Prompt for patient details
                unique_id = simpledialog.askstring("Patient Details", "Enter unique ID:")
                username = simpledialog.askstring("Patient Details", "Enter patient username:")
                password = simpledialog.askstring("Patient Details", "Enter patient's password:")
                name = simpledialog.askstring("Patient Details", "Enter patient's name:")
                doctor_assigned = simpledialog.askstring("Patient Details", "Enter assigned doctor:")
                
                # Insert patient into patients table
                cursor.execute('INSERT INTO patients VALUES (?, ?, ?, ?, ?)', (unique_id, username, password, name, doctor_assigned))
                conn.commit()
                messagebox.showinfo("Success", "Patient added successfully")

                # Insert user into users table
                cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'patient'))
                conn.commit()
            else:
                messagebox.showerror("Error", "Patient already exists")
        else:
            messagebox.showerror("Error", "Invalid input")

    def remove_patient():
        name = simpledialog.askstring("Remove Patient", "Enter patient name:")
        if name:
            cursor.execute('DELETE FROM patients WHERE name=?', (name,))
            conn.commit()
            messagebox.showinfo("Success", "Patient removed successfully")
        else:
            messagebox.showerror("Error", "Invalid input")

    def view_patients():
        cursor.execute('SELECT * FROM patients')
        patients = cursor.fetchall()
        
        if patients:
            patients_window = tk.Toplevel(admin_window)
            patients_window.title("List of Patients")
            patients_window.geometry("500x300")  # Set window size

            patients_text = tk.Text(patients_window, height=15, width=60, font=("Helvetica", 12))
            patients_text.pack(padx=20, pady=20)

            for patient in patients:
                patients_text.insert(tk.END, f"Patient ID: {patient[0]}\n")
                patients_text.insert(tk.END, f"Username: {patient[1]}\n")
                patients_text.insert(tk.END, f"Name: {patient[3]}\n")
                patients_text.insert(tk.END, f"Doctor Assigned: {patient[4]}\n")
                patients_text.insert(tk.END, "-" * 40 + "\n")
        else:
            messagebox.showinfo("No Patients", "No patients found.")

    add_patient_btn = tk.Button(admin_window, text="Add Patient", command=add_patient, font=("Helvetica", 14), bg="#4CAF50", fg="white")
    add_patient_btn.pack(pady=20)

    remove_patient_btn = tk.Button(admin_window, text="Remove Patient", command=remove_patient, font=("Helvetica", 14), bg="#F44336", fg="white")
    remove_patient_btn.pack(pady=20)

    view_patients_btn = tk.Button(admin_window, text="View Patients", command=view_patients, font=("Helvetica", 14), bg="#2196F3", fg="white")
    view_patients_btn.pack(pady=20)

# Patient dashboard
def patient_dashboard(username, conn, cursor):
    patient_window = tk.Toplevel(root)
    patient_window.title(f"Patient Dashboard - {username}")
    patient_window.geometry("500x300")  # Set window size

    def book_appointment():
        doctor = simpledialog.askstring("Book Appointment", "Enter doctor username:")
        appointment_time = simpledialog.askstring("Book Appointment", "Enter appointment time (YYYY-MM-DD HH:MM):")
        cursor.execute('INSERT INTO appointments (patient_username, doctor_username, appointment_time) VALUES (?, ?, ?)', (username, doctor, appointment_time))
        conn.commit()
        messagebox.showinfo("Success", "Appointment booked successfully")

    book_appointment_btn = tk.Button(patient_window, text="Book Appointment", command=book_appointment, font=("Helvetica", 14), bg="#FFC107", fg="black")
    book_appointment_btn.pack(pady=20)

# Doctor dashboard
def doctor_dashboard(username, conn, cursor):
    doctor_window = tk.Toplevel(root)
    doctor_window.title(f"Doctor Dashboard - {username}")
    doctor_window.geometry("500x300")  # Set window size

    def prescribe_medicine():
        patient = simpledialog.askstring("Prescribe Medicine", "Enter patient username:")
        medicine = simpledialog.askstring("Prescribe Medicine", "Enter prescribed medicine:")
        cursor.execute('UPDATE patients SET medicine=? WHERE username=?', (medicine, patient))
        conn.commit()
        messagebox.showinfo("Success", "Medicine prescribed successfully")

    def view_assigned_patients():
        cursor.execute('SELECT * FROM patients WHERE doctor_assigned=?', (username,))
        assigned_patients = cursor.fetchall()
        
        if assigned_patients:
            assigned_patients_window = tk.Toplevel(doctor_window)
            assigned_patients_window.title("Patients Assigned to You")
            assigned_patients_window.geometry("500x300")  # Set window size

            assigned_patients_text = tk.Text(assigned_patients_window, height=15, width=60, font=("Helvetica", 12))
            assigned_patients_text.pack(padx=20, pady=20)

            for patient in assigned_patients:
                assigned_patients_text.insert(tk.END, f"Patient ID: {patient[0]}\n")
                assigned_patients_text.insert(tk.END, f"Username: {patient[1]}\n")
                assigned_patients_text.insert(tk.END, f"Name: {patient[3]}\n")
                assigned_patients_text.insert(tk.END, "-" * 40 + "\n")
        else:
            messagebox.showinfo("No Patients", "You have no assigned patients.")

    prescribe_medicine_btn = tk.Button(doctor_window, text="Prescribe Medicine", command=prescribe_medicine, font=("Helvetica", 14), bg="#9C27B0", fg="white")
    prescribe_medicine_btn.pack(pady=20)

    view_assigned_patients_btn = tk.Button(doctor_window, text="View Assigned Patients", command=view_assigned_patients, font=("Helvetica", 14), bg="#607D8B", fg="white")
    view_assigned_patients_btn.pack(pady=20)

# GUI setup
root = tk.Tk()
root.title("FAST Healthcare Management System")
root.geometry("400x300")  # Set window size
root.configure(bg="#E0E0E0")  # Set background color

username_label = tk.Label(root, text="Username:", font=("Helvetica", 16), bg="#E0E0E0")
username_label.pack(pady=10)
username_entry = tk.Entry(root, font=("Helvetica", 14))
username_entry.pack(pady=5)

password_label = tk.Label(root, text="Password:", font=("Helvetica", 16), bg="#E0E0E0")
password_label.pack(pady=10)
password_entry = tk.Entry(root, show="*", font=("Helvetica", 14))
password_entry.pack(pady=5)

login_button = tk.Button(root, text="Login", command=login, font=("Helvetica", 14), bg="#2196F3", fg="white")
login_button.pack(pady=20)

root.mainloop()
