from database import db

#Stores login credentials and role of each user
class User(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True,nullable=False)
    password = db.Column(db.String(200),nullable=False)  
    role = db.Column(db.String(50),nullable=False)             #admin, student, company 
    is_blacklisted = db.Column(db.Boolean, default=False)  

#Stores student details
class Student(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # One-to-one relationship with User
    department = db.Column(db.String(100), default="")
    name = db.Column(db.String(100),default="")                # Added name field for better identification of students
    resume_filename = db.Column(db.String(200), default="")    # To store the filename of the uploaded resume
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(20), default='')
    location = db.Column(db.String(100), default='')
    cgpa = db.Column(db.Float, default=0.0)        
    year = db.Column(db.Integer, default=0) 
    
#Stores company details
class Company(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # One-to-one relationship with User
    approved = db.Column(db.Boolean, default=False)            # Approval status for company accounts
    overview = db.Column(db.Text, default="")                  # Added overview field to store company description
    company_name = db.Column(db.String(150), default="")
    hr_contact = db.Column(db.String(150), default="")
    website = db.Column(db.String(200), default="")
    

#Drive represents a job opportunity posted by a company
class Drive(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  # Many-to-one relationship with Company
    drive_name = db.Column(db.String(100),default="")
    job_title = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(100),default="")
    location = db.Column(db.String(100),default="")
    eligibility = db.Column(db.String(200), default="")  
    deadline = db.Column(db.String(100), default="")  
    is_closed = db.Column(db.Boolean, default=False) 
    admin_status = db.Column(db.String(20), default='Pending')

#Application represents a student's application to a specific drive/job opportunity   
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)  # Many-to-one relationship with Student
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)      # Many
    status = db.Column(db.String(50), default="Applied")             # e.g., "Applied", "Shortlisted", "Rejected"
    interview_type = db.Column(db.String(50), default="")            # e.g., "Online", "Onsite"
    result = db.Column(db.String(50), default="")                    # e.g., "Pending", "Passed", "Failed"
    remark = db.Column(db.String(200), default="")                   # For interview feedback or remarks from the company
    interview_date  = db.Column(db.String(100), default="")
    interview_link  = db.Column(db.String(300), default="")
    interview_notes = db.Column(db.Text, default="")

#Gives Notification
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.now())