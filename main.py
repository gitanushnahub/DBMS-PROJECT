from fastapi import FastAPI, Request, Form, Depends, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import uvicorn

from urllib.parse import quote_plus
password = quote_plus("#GNEr301031")
DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost/exam_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Models
class Student(Base):
    __tablename__ = "students"
    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    grade = Column(String(10))
    marks = Column(Integer, default=0)
    phone_number = Column(String(15))
    dob = Column(String(20))  # or Date if needed
    blood_group = Column(String(5))
    address_city = Column(String(100))
    address_street = Column(String(100))
    address_door_number = Column(String(20))
    department = Column(String(100))
    username = Column(String(50), unique=True, index=True)
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(50))
    question_text = Column(String(200))
    option_a = Column(String(100))
    option_b = Column(String(100))
    option_c = Column(String(100))
    option_d = Column(String(100))
    correct_option = Column(String(1))

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone_number: str = Form(...),
    dob: str = Form(...),
    blood_group: str = Form(...),
    city: str = Form(...),
    street_name: str = Form(...),
    door_number: str = Form(...),
    department: str = Form(...),
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(Student).filter(Student.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if username already exists
    existing_username = db.query(Student).filter(Student.username == username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    student = Student(
        name=name,
        email=email,
        password=password,
        phone_number=phone_number,
        dob=dob,
        blood_group=blood_group,
        address_city=city,
        address_street=street_name,
        address_door_number=door_number,
        department=department,
        username=username,  # Add this line
        grade="",
        marks=0
    )
    db.add(student)
    db.commit()
    return RedirectResponse(url=f"/dashboard?user={email}", status_code=status.HTTP_302_FOUND)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == email, Student.password == password).first()
    if not student:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return RedirectResponse(url=f"/dashboard?user={email}", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == user).first()
    if not student:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get the list of subjects
    subjects = db.query(Question.subject).distinct().all()
    subjects_list = [s[0] for s in subjects]
    
    print(f"Subjects found: {subjects_list}")  # Debug output
    
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "student": student, 
            "subjects": subjects_list
        }
    )

@app.get("/test/{subject}", response_class=HTMLResponse)
async def take_test(request: Request, subject: str, user: str, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.subject == subject).limit(10).all()
    return templates.TemplateResponse("test.html", {"request": request, "questions": questions, "subject": subject, "user": user})

@app.post("/submit/{subject}")
async def submit_test(subject: str, request: Request, user: str, db: Session = Depends(get_db)):
    form = await request.form()
    questions = db.query(Question).filter(Question.subject == subject).limit(10).all()
    correct = 0
    for q in questions:
        user_ans = form.get(str(q.id))
        if user_ans and user_ans.lower() == q.correct_option:  # Convert to lowercase before comparing
            correct += 1

    grade = "A" if correct >= 9 else "B" if correct >= 7 else "C" if correct >= 5 else "D"
    student = db.query(Student).filter(Student.email == user).first()
    student.marks = correct
    student.grade = grade
    db.commit()
    return templates.TemplateResponse("result.html", {"request": request, "marks": correct, "grade": grade})

@app.get("/test-add-student")
def test_add_student(db: Session = Depends(get_db)):
    new_student = Student(
        name="Test User",
        email="test@example.com",
        password="test123",
        grade="",
        marks=0,
        phone_number="0000000000",
        dob="2000-01-01",
        blood_group="O+",
        address_city="City",
        address_street="Street",
        address_door_number="123",
        department="CS"
    )
    db.add(new_student)
    db.commit()
    return {"message": "Student added!"}

@app.get("/test-add-questions")
def test_add_questions(db: Session = Depends(get_db)):
    # Clear any existing questions (optional - be careful in production)
    db.query(Question).delete()

    # Mathematics questions
    math_questions = [
        Question(subject="Mathematics", question_text="What is 2 + 2?", option_a="3", option_b="4", option_c="5", option_d="6", correct_option="b"),
        Question(subject="Mathematics", question_text="What is 5 × 5?", option_a="20", option_b="25", option_c="30", option_d="35", correct_option="b"),
        Question(subject="Mathematics", question_text="What is the square root of 64?", option_a="6", option_b="8", option_c="10", option_d="12", correct_option="b"),
        Question(subject="Mathematics", question_text="What is 100 divided by 4?", option_a="20", option_b="25", option_c="30", option_d="40", correct_option="b"),
        Question(subject="Mathematics", question_text="What is the value of pi (approx)?", option_a="3.14", option_b="2.71", option_c="1.61", option_d="4.13", correct_option="a"),
        Question(subject="Mathematics", question_text="Solve: 6²", option_a="36", option_b="12", option_c="18", option_d="30", correct_option="a"),
        Question(subject="Mathematics", question_text="Which is a prime number?", option_a="9", option_b="15", option_c="11", option_d="21", correct_option="c"),
        Question(subject="Mathematics", question_text="What is 15% of 200?", option_a="30", option_b="25", option_c="20", option_d="35", correct_option="a"),
        Question(subject="Mathematics", question_text="What is 9 × 8?", option_a="72", option_b="81", option_c="63", option_d="70", correct_option="a"),
        Question(subject="Mathematics", question_text="What is the value of log(1)?", option_a="0", option_b="1", option_c="-1", option_d="None", correct_option="a"),
    ]

    # Physics questions
    physics_questions = [
        Question(subject="Physics", question_text="What is the SI unit of force?", option_a="Newton", option_b="Joule", option_c="Watt", option_d="Pascal", correct_option="a"),
        Question(subject="Physics", question_text="What is E = mc² known as?", option_a="Newton's Law", option_b="Ohm's Law", option_c="Mass-Energy Equivalence", option_d="Gravitational Law", correct_option="c"),
        Question(subject="Physics", question_text="Speed of light in vacuum is?", option_a="3x10^8 m/s", option_b="3x10^6 m/s", option_c="3x10^5 m/s", option_d="None", correct_option="a"),
        Question(subject="Physics", question_text="Which of these is a vector quantity?", option_a="Speed", option_b="Distance", option_c="Displacement", option_d="Mass", correct_option="c"),
        Question(subject="Physics", question_text="What is unit of power?", option_a="Joule", option_b="Watt", option_c="Newton", option_d="Ampere", correct_option="b"),
        Question(subject="Physics", question_text="Which instrument measures current?", option_a="Voltmeter", option_b="Ammeter", option_c="Barometer", option_d="Thermometer", correct_option="b"),
        Question(subject="Physics", question_text="Gravitational acceleration on Earth is?", option_a="8.9 m/s²", option_b="9.8 m/s²", option_c="10 m/s²", option_d="7.5 m/s²", correct_option="b"),
        Question(subject="Physics", question_text="What is Ohm’s law?", option_a="V=IR", option_b="E=mc²", option_c="F=ma", option_d="P=IV", correct_option="a"),
        Question(subject="Physics", question_text="Lens that converges light is?", option_a="Concave", option_b="Convex", option_c="Plane", option_d="None", correct_option="b"),
        Question(subject="Physics", question_text="What is unit of frequency?", option_a="Hertz", option_b="Ohm", option_c="Tesla", option_d="Weber", correct_option="a"),
    ]

    # Chemistry questions
    chemistry_questions = [
        Question(subject="Chemistry", question_text="Chemical symbol for gold?", option_a="Au", option_b="Ag", option_c="Fe", option_d="Cu", correct_option="a"),
        Question(subject="Chemistry", question_text="Atomic number of carbon?", option_a="5", option_b="6", option_c="7", option_d="8", correct_option="b"),
        Question(subject="Chemistry", question_text="Water’s chemical formula?", option_a="H2O", option_b="CO2", option_c="O2", option_d="NaCl", correct_option="a"),
        Question(subject="Chemistry", question_text="Acid in vinegar?", option_a="Citric acid", option_b="Acetic acid", option_c="Sulfuric acid", option_d="Hydrochloric acid", correct_option="b"),
        Question(subject="Chemistry", question_text="Common salt is?", option_a="NaCl", option_b="KCl", option_c="CaCO3", option_d="MgSO4", correct_option="a"),
        Question(subject="Chemistry", question_text="pH of neutral substance?", option_a="6", option_b="7", option_c="8", option_d="9", correct_option="b"),
        Question(subject="Chemistry", question_text="What is an isotope?", option_a="Same neutrons", option_b="Same protons, different neutrons", option_c="Same electrons", option_d="Different elements", correct_option="b"),
        Question(subject="Chemistry", question_text="Noble gas example?", option_a="Oxygen", option_b="Hydrogen", option_c="Helium", option_d="Nitrogen", correct_option="c"),
        Question(subject="Chemistry", question_text="Element with atomic number 1?", option_a="Hydrogen", option_b="Helium", option_c="Lithium", option_d="Carbon", correct_option="a"),
        Question(subject="Chemistry", question_text="Symbol for Sodium?", option_a="Na", option_b="S", option_c="So", option_d="Sn", correct_option="a"),
    ]

    # Add to DB
    all_questions = math_questions + physics_questions + chemistry_questions
    for q in all_questions:
        db.add(q)
    db.commit()

    return {"message": f"{len(all_questions)} questions added successfully!"}


@app.get("/test-students")
def test_get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return students

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)