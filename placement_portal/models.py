from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# --------------------------
# Student Model
# --------------------------
class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    skills = db.Column(db.Text)
    resume_link = db.Column(db.String(500))

    applications = db.relationship("Application", back_populates="student")

    def __repr__(self):
        return f"<Student {self.full_name}>"


# --------------------------
# Company Model
# --------------------------
class Company(db.Model):
    __tablename__ = "companies"

    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(200))
    location = db.Column(db.String(200))
    hr_email = db.Column(db.String(200), unique=True, nullable=False)

    jobs = db.relationship("Job", back_populates="company")

    def __repr__(self):
        return f"<Company {self.company_name}>"


# --------------------------
# Job Model
# --------------------------
class Job(db.Model):
    __tablename__ = "jobs"

    job_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.company_id"), nullable=False)
    job_role = db.Column(db.String(200), nullable=False)
    job_description = db.Column(db.Text)
    salary_package = db.Column(db.Float)
    eligibility_cgpa = db.Column(db.Float)
    skills_required = db.Column(db.Text)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship("Company", back_populates="jobs")
    applications = db.relationship("Application", back_populates="job")

    def __repr__(self):
        return f"<Job {self.job_role}>"


# --------------------------
# Application Model
# --------------------------
class Application(db.Model):
    __tablename__ = "applications"

    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.job_id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.student_id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")

    # Relationships (back_populates)
    job = db.relationship("Job", back_populates="applications")
    student = db.relationship("Student", back_populates="applications")

    def __repr__(self):
        return f"<Application Student={self.student_id} Job={self.job_id}>"
