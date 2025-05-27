from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse

# app = FastAPI()
#
# students = []
#
#
# # Pydantic model for full data (POST)
# class Student(BaseModel):
#     name: str
#     age: int
#     grade: str
#
#
# # Pydantic model for partial data (PATCH)
# class UpdateStudent(BaseModel):
#     name: Optional[str] = None
#     age: Optional[int] = None
#     grade: Optional[str] = None
#
#
# # Custom exception class
# class StudentNotFound(Exception):
#     def _init_(self, student_id: int):
#         self.student_id = student_id
#
#
# # Custom exception handler
# @app.exception_handler(StudentNotFound)
# def student_not_found_handler(request: Request, exc: StudentNotFound):
#     return JSONResponse(
#
#
#         status_code=404,
#         content={"message": f"Student with ID {exc.student_id} not found."},
#     )
#
#
# # POST - Add a new student
# @app.post("/students", status_code=status.HTTP_201_CREATED)
# def create_student(student: Student):
#     students.append(student.dict())
#     return {
#         "message": "Student added successfully",
#         "data": student
#     }
#
#
# # PATCH - Update existing student partially
# @app.patch("/students/{student_id}")
# def partial_update_student(student_id: int, student: UpdateStudent):
#     if student_id < 0 or student_id >= len(students):
#         raise StudentNotFound(student_id)
#
#     updated_data = student.dict(exclude_unset=True)
#     students[student_id].update(updated_data)
#
#     return {
#         "message": "Student updated successfully",
#         "data": students[student_id]
#     }
#
#
# # GET - Retrieve all students (optional utility)
# @app.get("/students")
# def get_all_students():
#     return {
#         "message": "List of all students",
#         "data": students
#     }


from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from models import Student
from database import engine, create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/students")
def add_student(student: Student):
    with Session(engine) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
        return student


@app.get("/students")
def get_students():
    with Session(engine) as session:
        statement = select(Student)
        results = session.exec(statement).all()
        return results


@app.put("/students/{student_id}")
def update_student(student_id: int, updated_student: Student):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        student.name = updated_student.name
        student.age = updated_student.age
        student.grade = updated_student.grade

        session.add(student)
        session.commit()
        session.refresh(student)
        return student

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None


@app.patch("/students/{student_id}")
def patch_student(student_id: int, student_update: StudentUpdate):
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        update_data = student_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(student, key, value)

        session.add(student)
        session.commit()
        session.refresh(student)
        return student