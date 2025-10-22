from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db=SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(255))
    qualification = db.Column(db.String(255))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False) 
    name = db.Column(db.String(255), nullable=False)

    subject = db.relationship('Subject', backref=db.backref('chapters', lazy=True, cascade="all, delete"))


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(255), nullable=False) 
    date_of_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    time_duration = db.Column(db.String(5))
    chapter = db.relationship('Chapter', backref=db.backref('quizzes', lazy=True, cascade="all, delete-orphan"))


class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete="CASCADE"), nullable=False)
    selected_option = db.Column(db.String(255), nullable=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('score.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref='answers')
    question = db.relationship('Question', backref='answers')
    attempt = db.relationship('Score', backref=db.backref('user_answers', lazy=True, cascade="all, delete-orphan"))


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False) 
    question_statement = db.Column(db.Text, nullable=False)  
    difficulty = db.Column(db.String(10), nullable=False, default='easy')
    option1 = db.Column(db.String(255), nullable=False)  
    option2 = db.Column(db.String(255), nullable=False)  
    option3 = db.Column(db.String(255), nullable=False)  
    option4 = db.Column(db.String(255), nullable=False)  
    correct_option = db.Column(db.String(255), nullable=False) 

    quiz = db.relationship('Quiz', backref=db.backref('questions', lazy=True, cascade="all, delete-orphan"))


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False) 
    time_stamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('scores', lazy=True))  
    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True, cascade="all, delete"))
