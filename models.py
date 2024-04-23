# SQLAlchemy models that correspond to the database tables.
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# TODO: Add the values of each column
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
#    title = Column(String, index=True)
#    inscriptions = relationship("Inscription", back_populates="course")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
#    name = Column(String, index=True)
#    inscriptions = relationship("Inscription", back_populates="student")

class Inscription(Base):
    __tablename__ = "inscriptions"
    id = Column(Integer, primary_key=True, index=True)
#    course_id = Column(Integer, ForeignKey('courses.id'))
#    student_id = Column(Integer, ForeignKey('students.id'))
#    course = relationship("Course", back_populates="inscriptions")
#    student = relationship("Student", back_populates="inscriptions")
