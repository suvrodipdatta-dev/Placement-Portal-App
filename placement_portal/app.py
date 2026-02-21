
from flask import Flask, render_template, request, redirect, session
from models import db, Student, Company, Job, Application

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
app.secret_key = "supersecretkey123"

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------- Predefined Admin Credentials ----------
ADMIN_EMAIL = "admin@portal.com"
ADMIN_PASSWORD = "admin123"


# ---------- Home Page ----------
@app.route("/")
def home():
    return render_template("base.html")


# ---------- Login Page ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # --------- Admin Login ---------
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            return redirect("/admin_dashboard")

        # --------- Student Login ---------
        student = Student.query.filter_by(email=email, password=password).first()
        if student:
            return redirect("/student_dashboard")

        # --------- Company Login ---------
        company = Company.query.filter_by(hr_email=email, password=password).first()
        if company:
            if company.is_approved:
                return redirect(f"/company/dashboard/{company.company_id}")
            else:
                return "Your company account is waiting for Admin approval."

        # --------- Invalid Credentials ---------
        return "Invalid email or password!"

    return render_template("login.html")


# ---------- Temporary Dashboards (to avoid errors) ----------
@app.route("/admin_dashboard")
def admin_dashboard():
    # Fetch all students
    students = Student.query.all()

    # Fetch all companies
    companies = Company.query.all()

    # Fetch only pending (unapproved) companies
    pending_companies = Company.query.filter_by(is_approved=False).all()

    # Fetch all jobs
    jobs = Job.query.all()

    # Fetch all applications
    applications = Application.query.all()

    return render_template(
        "admin_dashboard.html",
        students=students,
        companies=companies,
        pending_companies=pending_companies,
        jobs=jobs,
        applications=applications
    )

@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/company/<int:company_id>/create_drive", methods=["GET", "POST"])
def create_drive(company_id):
    if request.method == "POST":
        drive_name = request.form.get("drive_name")
        job_role = request.form.get("job_role")
        job_title = request.form.get("job_title")
        desc = request.form.get("job_description")
        cgpa = request.form.get("eligibility_cgpa")
        salary = request.form.get("salary_package")

        new_drive = Job(
            drive_name=drive_name,
            job_role=job_role,
            job_title=job_title,
            job_description=desc,
            salary_package=salary,
            eligibility_cgpa=cgpa,
            status="upcoming",
            company_id=company_id
        )

        db.session.add(new_drive)
        db.session.commit()

        return redirect(f"/company_dashboard/{company_id}")

    return render_template("create_drive.html", company_id=company_id)

@app.route("/drive/<int:job_id>")
def view_drive(job_id):
    drive = Job.query.get(job_id)
    return render_template("view_drive.html", drive=drive)

@app.route("/mark_drive_complete/<int:job_id>", methods=["POST"])
def mark_drive_complete(job_id):
    job = Job.query.get(job_id)

    if job:
        job.status = "completed"
        db.session.commit()

    return redirect("/admin_dashboard")

@app.route("/company/dashboard/<int:company_id>")
def company_dashboard(company_id):
    company = Company.query.get(company_id)

    if not company:
        return "Company not found"

    # Load drives created by this company
    upcoming_drives = Job.query.filter_by(company_id=company.company_id, status="upcoming").all()
    closed_drives = Job.query.filter_by(company_id=company.company_id, status="closed").all()

    return render_template(
        "company_dashboard.html",
        company=company,
        upcoming_drives=upcoming_drives,
        closed_drives=closed_drives
    )

@app.route("/admin/approve_company/<int:company_id>", methods=["POST"])
def approve_company(company_id):
    company = Company.query.get(company_id)

    if not company:
        return "Company not found"

    company.is_approved = True
    db.session.commit()

    return redirect("/admin_dashboard")

@app.route("/student_register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        department = request.form.get("department")
        cgpa = request.form.get("cgpa")

        # Check if email already exists
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            return "Email already registered!"

        # Create new student object
        new_student = Student(
            full_name=name,
            email=email,
            password=password,
            department=department,
            cgpa=cgpa
        )

        db.session.add(new_student)
        db.session.commit()

        return redirect("/login")

    # GET request → show registration page
    return render_template("student_register.html")


@app.route("/company_register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        
        company_name = request.form.get("company_name")
        email = request.form.get("hr_email")
        password = request.form.get("password")
        industry = request.form.get("industry")
        location = request.form.get("location")

        new_company = Company(
            company_name=company_name,
            hr_email=email,
            password=password,
            industry=industry,
            location=location,
            is_approved=False
        )

        db.session.add(new_company)
        db.session.commit()

        return "Company Registered Successfully! Waiting for Admin Approval."

    return render_template("company_register.html")



# ---------- Run Flask ----------
if __name__ == "__main__":
    app.run(debug=True)
