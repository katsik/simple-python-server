###### Start of Congfiguration code put at the beginning #########
import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

####### End of Configuration code put at the beginning ###########

class Department(Base):
    __tablename__ = 'department'

    name = Column(String(80), nullable = False)
    id = Column(Integer,primary_key = True)


class Employee(Base):
    __tablename__ = 'employee'

    name = Column(String(80),nullable = False)
    id = Column(Integer, primary_key=True)
    address = Column(String(80))
    job_description = Column(String(80))
    salary = Column(String(80))
    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship(Department)

    @property
    def serialize(self):
        return {
            'name'  :   self.name,
            'job_description'   :   self.job_description,
            'id'    :   self.id,
            'salary' :   self.salary,
            'address'    :   self.address
        }

######### insert at the end of the file ##########
engine = create_engine('sqlite:///depts_and_employees.db')

Base.metadata.create_all(engine)