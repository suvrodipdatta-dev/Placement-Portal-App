
from flask import Flask, render_template, request, redirect
from models import db, Student, Company, Job, Application

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement.db'
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
                return redirect("/company_dashboard")
            else:
                return "Your company account is waiting for Admin approval."

        # --------- Invalid Credentials ---------
        return "Invalid email or password!"

    return render_template("login.html")


# ---------- Temporary Dashboards (to avoid errors) ----------
@app.route("/admin_dashboard")
def admin_dashboard():
    students = Student.query.all()
    companies = Company.query.all()

    try:
        pending_companies = Company.query.filter_by(is_approved=False).all()
    except:
        pending_companies = []

    jobs = Job.query.all()
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

@app.route("/company_dashboard")
def company_dashboard():
    return render_template("company_dashboard.html")


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
