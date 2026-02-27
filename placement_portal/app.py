
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
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
        # ----- Student Login -----
        student = Student.query.filter_by(email=email, password=password).first()
        if student:
          session["student_id"] = student.student_id   # <-- IMPORTANT
          return redirect(url_for("student_dashboard"))
        # --------- Company Login ---------
        company = Company.query.filter_by(hr_email=email, password=password).first()
        if company:
            if company.is_approved:
                session["company_id"] = company.company_id   
                return redirect(url_for("company_dashboard", company_id=company.company_id))
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
    student_id = session.get("student_id")

    if not student_id:
        return redirect("/login")   # User not logged in

    student = Student.query.get(student_id)
    companies = Company.query.filter_by(is_approved=True).all()
    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template("student_dashboard.html",
                           student=student,
                           companies=companies,
                           applications=applications)

@app.route("/company/create_drive/<int:company_id>/", methods=["GET", "POST"])
def create_drive(company_id):
    company = Company.query.get(company_id)
    print("Create drive")
    if not company:
        return "Company not found"

    if request.method == "POST":
        drive_name = request.form['drive_name']
        job_role = request.form['job_role']
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        eligibility_cgpa = request.form['eligibility_cgpa']
        salary_package = request.form['salary_package']
        location = request.form['location']

        new_drive = Job(
            company_id = company.company_id,
            drive_name = drive_name,
            job_role = job_role,
            job_title = job_title,
            job_description = job_description,
            eligibility_cgpa = eligibility_cgpa,
            salary_package = salary_package,
            location = location
        )

        db.session.add(new_drive)
        db.session.commit()

        return redirect(f"/company/dashboard/{company.company_id}")

    return render_template("create_drive.html", company=company)

@app.route("/drive/<int:job_id>")
def view_drive(job_id):
    drive = Job.query.get(job_id)

    if not drive:
        return "Drive not found"
    
    from_student = False
    if "student_id" in session:
        from_student = True

    return render_template("view_drive.html", drive=drive, from_student=from_student )

@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.args.get("query", "")  # from URL ?query=

    # For now, just open the page
    return render_template("search.html", query=query)

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

@app.route("/company/drive/<int:job_id>/applications")
def view_drive_applications(job_id):
    drive = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()
    print(drive.job_id, applications)
    return render_template("company_view_applicants.html",
                           drive=drive,
                           applications=applications)

@app.route("/company/application/<int:application_id>")
def company_view_application(application_id):
    app = Application.query.get_or_404(application_id)
    return render_template("company_student_application.html", app=app)

@app.route("/company/application/<int:application_id>/update", methods=["POST"])
def update_application_status(application_id):
    app = Application.query.get_or_404(application_id)
    app.status = request.form.get("status")
    db.session.commit()

    return redirect(f"/company/drive/{app.job_id}/applications")

@app.route("/company/drive/<int:job_id>/close")
def close_drive(job_id):
    drive = Job.query.get_or_404(job_id)
    drive.is_closed = True
    db.session.commit()

    return redirect(f"/company/dashboard/{drive.company_id}")

@app.route("/company/<int:company_id>")
def company_details(company_id):
    company = Company.query.get(company_id)

    if not company:
        return "Company not found"

    jobs = Job.query.filter_by(company_id=company_id).all()

    return render_template("company_details.html", company=company, jobs=jobs)

@app.route("/admin/approve_company/<int:company_id>")
def approve_company(company_id):
    company = Company.query.get(company_id)

    if not company:
        return "Company not found"

    company.is_approved = True
    db.session.commit()

    return redirect("/admin_dashboard")

@app.route("/student_history/<int:student_id>")
def student_history(student_id):
    student = Student.query.get(student_id)

    if not student:
        return "Student not found"

    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_history.html",
        student=student,
        applications=applications
    )

@app.route("/apply/<int:job_id>", methods=["POST"])
def apply_drive(job_id):
    print("-------"+str(job_id))
    student_id = session.get("student_id")

    if not student_id:
        return redirect("/login")

    job = Job.query.get(job_id)
    if not job:
        return "Job not found"

    # Check if already applied
    existing = Application.query.filter_by(student_id=student_id, job_id=job_id).first()
    if existing:
        return redirect(url_for("student_dashboard", student_id=student_id))

    new_application = Application(
        student_id=student_id,
        job_id=job_id,
        application_date=datetime.utcnow()
    )

    db.session.add(new_application)
    db.session.commit()
    print("applied for job successfully")

    return redirect(url_for("student_dashboard", student_id=student_id))

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
