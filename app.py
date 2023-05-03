from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.globals import request, session
from flask.helpers import make_response
from datetime import date, datetime
from flask import jsonify
from flask_marshmallow import Marshmallow
from sqlalchemy.sql.elements import Null, True_
from sqlalchemy.sql.operators import exists

#
#               Data Base
#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://{host_name}'

#
#           DataBase
#

db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('Database dropped!')


@app.cli.command('db_seed')
def db_seed():
    week_1 = Subject(subject = 'Introduction to projects')
    week_2 = Subject(subject = 'Internship kick-off')
    week_3 = Subject(subject = 'SDLC and Software methodology')
    week_4 = Subject(subject = 'BA process organization and planning')
    week_5 = Subject(subject = 'Requirements development (Elicitation and Analysis)')
    week_6 = Subject(subject = 'Requirements development (Documenting requirements)')
    week_7 = Subject(subject = 'Requirements development (UI design artifacts)')
    week_8 = Subject(subject = 'Requirements development (Clarification, Prioritization, Risk Management, Traceability)')
    week_9 = Subject(subject = 'Base IT knowledge')
    week_10 = Subject(subject = 'Soft skills')
    week_11 = Subject(subject = 'Closure')


    db.session.add(week_1)
    db.session.add(week_2)
    db.session.add(week_3)
    db.session.add(week_4)
    db.session.add(week_5)
    db.session.add(week_6)
    db.session.add(week_7)
    db.session.add(week_8)
    db.session.add(week_9)
    db.session.add(week_10)
    db.session.add(week_11)
    db.session.commit()
    print('Database seeded!')


class Subject(db.Model):
    __tablename__='subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Lesson %r>' & self.id

class SubjectSchema(ma.Schema):
    class Meta:
        fields = ('id', 'subject')


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)    
    birth_date = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    

    def __repr__(self):
        return '<Student %r>' % self.id

class StudentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'birth_date', 'date')


class Mark(db.Model):
    __tablename__="marks"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    mark = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Mark %r>' % self.id

class MarkSchema(ma.Schema):
    class Meta:
        fields = ('id', 'student_id', 'subject_id','date', 'mark')


student_schema = StudentSchema()
students_schema = StudentSchema(many = True)
subject_schema = SubjectSchema()
subjects_schema = SubjectSchema(many = True)
mark_schema = MarkSchema()
marks_schema = MarkSchema(many = True)


@app.route('/')
def index():
    return "Hello!"

#
#           Students API
#

@app.route('/student/add', methods=['POST'])
def add_student():
    try:
              
        if 'first_name' in request.form:
            first_name = request.form['first_name']
        else:
             return jsonify(message=f"Required String parameter 'first_name' is not present"), 400
        if 'last_name' in request.form:
                last_name = request.form['last_name']
        else:
            return jsonify(message=f"Required String parameter 'last_name' is not present"), 400
        if 'birth_date' in request.form:
            birth_date = request.form['birth_date']
        else:
            return jsonify(message=f"Required DateTime parameter 'birth_date' is not present"), 400
        if Student.query.filter((Student.first_name == first_name) & (Student.last_name == last_name)).first() != None:
            return jsonify(message=f"Student {request.form['first_name']} {request.form['last_name']} has already existed"), 409  

        student = Student(first_name=first_name, last_name=last_name, birth_date=datetime.strptime(birth_date, '%Y-%m-%d'))

        db.session.add(student)
        db.session.commit()

        st = db.session.query(Student).order_by(Student.date.desc()).first()
        result = student_schema.dump(st)
        return jsonify(result), 200
    
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400


@app.route('/student/update', methods=['PUT'])
def update_student():
    try:
        if 'id' in request.form:
            id = request.form['id']
        else:
            return jsonify(message=f"Required Integer parameter 'id' is not present"), 400
        student = Student.query.filter_by(id = id).first_or_404(description = f"There is no record with id={id}")
        if 'first_name' in request.form and request.form['first_name'] is not "":
            first_name = request.form['first_name']
        else:
            first_name = student.first_name
        if 'last_name' in request.form and request.form['last_name'] is not "":
            last_name = request.form['last_name']
        else:
            last_name = student.last_name
        if 'birth_date' in request.form and request.form['birth_date'] is not "":
            birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d') 
        else:
            birth_date = student.birth_date
        student.date = datetime.utcnow()
        if Student.query.filter((Student.first_name == first_name) & (Student.last_name == last_name) & (Student.birth_date == birth_date)).first() != None:
                return jsonify(message=f"Student {student.first_name} {student.last_name} has already existed"), 409  
        student.first_name = first_name
        student.last_name = last_name
        student.birth_date = birth_date

        db.session.commit()

        result = student_schema.dump(student)
        return jsonify(result), 200    
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400


@app.route('/student/<id>', methods=['DELETE'])
def delete_student(id):    
    try:
        student = Student.query.filter_by(id = id).first_or_404(description = f"There is no record with id={id}")
        first_name = student.first_name
        last_name = student.last_name

        db.session.delete(student)
        db.session.commit()

        return jsonify(message=f'Student {first_name} {last_name} with id = {id} was deleted')
    except Exception as ex:
        return jsonify(error=f"{ex}"), 400


@app.route('/student/<id>')
def get_student(id):
    try:
        student = Student.query.filter_by(id = id).first_or_404(description = f"There is no record with id={id}")
        result = student_schema.dump(student)
        return jsonify(result)
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400


@app.route('/student/all')
def all_students():
    try:
        user_list = db.session.query(Student).all()   
        result = students_schema.dump(user_list) 
        return jsonify(result)
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400


#
#           Subject API
#


@app.route('/subject/all')
def all_subjects():
    try:
        subject_list = db.session.query(Subject).all()   
        result = subjects_schema.dump(subject_list) 
        return jsonify(result)
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400
    

#
#           Marks API
#


@app.route('/mark/add', methods=['POST'])
def add_mark():
    try:
        if 'student_id' in request.form:
            student_id = request.form['student_id']
        else:
            return jsonify(message=f"Required Integer parameter 'student_id' is not present"), 400
        if 'subject_id' in request.form:
            subject_id = request.form['subject_id']
        else:
            return jsonify(message=f"Required Integer parameter 'subject_id' is not present"), 400
        if 'mark' in request.form:
            if int(request.form['mark']) > 10 or int(request.form['mark']) < 1:
                return jsonify(message=f"Mark should be from 1 to 10"), 400
            else:
                mark = request.form['mark']
        else:
            return jsonify(message=f"Required Integer parameter 'mark' is not present"), 400
        if Student.query.filter(Student.id == student_id).first_or_404(description = f"There is no record with student_id={student_id}") and Subject.query.filter(Subject.id == subject_id).first_or_404(description = f"There is no record with subject_id={subject_id}") != None:              

            add_mark = Mark(student_id=student_id, subject_id=subject_id, mark=mark)

            db.session.add(add_mark)
            db.session.commit()

            st = db.session.query(Mark).order_by(Mark.date.desc()).first()
            result = mark_schema.dump(st)
            return jsonify(result), 200
                           
          
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400


@app.route('/mark/all')
def all_marks():
    try:
        mark_list = db.session.query(Mark).all()   
        result = marks_schema.dump(mark_list) 
        return jsonify(result)
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400


@app.route('/mark/<id>')
def get_mark(id):
    try:
        mark = Mark.query.filter(Mark.id == id).first_or_404(description = f"There is no record with id={id}")
        result = mark_schema.dump(mark)
        return jsonify(result)
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400  

    
@app.route('/mark/student/<student_id>')
def get_student_marks(student_id):
    try:
        marks_list =db.session.query(Mark).filter(Mark.student_id == student_id)
        result = marks_schema.dump(marks_list)
        return jsonify(result)
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400       


@app.route('/mark/update', methods=['PUT'])
def update_mark():
    try:
        if 'id' in request.form:
            id = request.form['id']
            mark = Mark.query.filter(Mark.id == id).first_or_404(description = f"There is no record with id={id}")
        else:
            return jsonify(message=f"Required Integer parameter 'id' is not present"), 400
        if 'mark' in request.form and request.form['mark'] is not "":
            m = int(request.form['mark'])
            if m > 10 or m < 1:
                return jsonify(message=f"Mark should be from 1 to 10"), 400       
        else:
            return jsonify(message=f"Required Integer parameter 'mark' is not present"), 400
        if 'student_id' in request.form and request.form['student_id'] is not "":
            student_id = request.form['student_id']
            Student.query.filter(Student.id == student_id).first_or_404(description = f"There is no record with student_id={student_id}")            
        else:
            student_id = mark.student_id
        if 'subject_id' in request.form and request.form['subject_id'] is not "":
            subject_id = request.form['subject_id']
            Subject.query.filter(Subject.id == subject_id).first_or_404(description = f"There is no record with subject_id={subject_id}")            
        else:
            subject_id = mark.subject_id       
        mark.mark = m
        mark.student_id = student_id
        mark.subject_id = subject_id
        mark.date = datetime.utcnow()

        db.session.commit()

        result = mark_schema.dump(mark)
        return jsonify(result), 200
    
    except Exception as ex:
        return jsonify(message=f"{ex}"), 400

@app.route('/mark/<id>', methods=['DELETE'])
def delete_mark(id):
    try:
        mark = Mark.query.filter(Mark.id == id).first_or_404(description = f"There is no record with id={id}")
        student = db.session.query(Student).filter_by(id = int(mark.student_id)).first()
        subject = db.session.query(Subject).filter_by(id = int(mark.subject_id)).first()
        db.session.delete(mark)
        db.session.commit()

        return jsonify(message=f'Mark {mark.mark} {student.first_name} {student.last_name} in {subject.subject} was deleted'), 200
    except Exception as ex:
        return ex, 400


if __name__ == "__main__":
    app.run(debug=True)
