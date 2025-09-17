from flask import Blueprint,render_template,request,redirect,url_for
from flask_login import login_required,current_user
from models.models import User,Quiz,Question,Chapter,Subject,UserAnswer,db
from flask_bcrypt import bcrypt
admin_bp = Blueprint('admin_bp',__name__)

@admin_bp.route('/admin')
@login_required
def admin_portal():
    print(f"Current user: {current_user.username}, Authenticated: {current_user.is_authenticated}, Is Admin: {current_user.is_admin}")
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))
    elif current_user.is_admin:
        users = User.query.filter_by(is_admin=False).all()
        subjects = Subject.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()
        questions = Question.query.all()
        print("Users: ",users)
        return render_template('admin.html', users=users, subjects=subjects, chapters=chapters, quizzes=quizzes, questions = questions)

@admin_bp.route('/admin/search', methods=['GET'])
@login_required
def admin_search():
    query = request.args.get('q', '').strip()
    results = {"subjects": [], "chapters": [], "quizzes": [], "users": [], "questions": []}

    if query:
        results["subjects"] = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        results["chapters"] = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
        results["quizzes"] = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()
        results["users"] = User.query.filter(User.username.ilike(f"%{query}%"), User.username != "admin").all()
        results["questions"] = Question.query.filter(Question.question_statement.ilike(f"%{query}%")).all()

    return render_template('admin_search.html', query=query, results=results)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id) 
    if user:
        print("Deleted user : ",user.username)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin_bp.admin_portal'))

@admin_bp.route('/admin/users')
@login_required
def view_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('view_users.html', users=users)

@admin_bp.route('/admin/subjects')
@login_required
def manage_subjects():
    subjects = Subject.query.all()
    return render_template('manage_subjects.html', subjects=subjects)

@admin_bp.route('/admin/chapters')
@login_required
def manage_chapters():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    return render_template('manage_chapters.html', subjects=subjects, chapters=chapters)

@admin_bp.route('/admin/quizzes')
@login_required
def manage_quizzes():
    quizzes = (
        db.session.query(Quiz)
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .all()
    )
    chapters = Chapter.query.all()
    return render_template('manage_quizzes.html', quizzes=quizzes, chapters=chapters)

@admin_bp.route('/admin/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        quiz_id = request.form.get('quiz_id')
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        
        print(f"Quiz ID: {quiz_id}, Question: {question_statement}, Options: {option1}, {option2}, {option3}, {option4}, Correct: {correct_option}")

        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        db.session.add(new_question)
        db.session.commit()
    return redirect(url_for('admin_bp.manage_quiz', quiz_id=quiz_id))

@admin_bp.route('/admin/delete_question', methods=['POST'])
@login_required
def delete_question():
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    question_id = request.form.get('question_id')
    question = Question.query.get(question_id)
    if question:
        UserAnswer.query.filter_by(question_id=question.id).delete()
        quiz_id = question.quiz_id
        db.session.delete(question)
        db.session.commit()
        print(f"Deleted question: {question.question_statement}")

    return redirect(url_for('admin_bp.manage_quiz', quiz_id=quiz_id))

@admin_bp.route('/admin/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    question_to_update = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        # Update statement and options
        question_to_update.question_statement = request.form.get('question_statement')
        question_to_update.option1 = request.form.get('option1')
        question_to_update.option2 = request.form.get('option2')
        question_to_update.option3 = request.form.get('option3')
        question_to_update.option4 = request.form.get('option4')
        question_to_update.correct_option = request.form.get('correct_option')

        db.session.commit()
        return redirect(url_for('admin_bp.manage_quiz', quiz_id=question_to_update.quiz_id))

    return render_template('edit_question.html', question=question_to_update)

@admin_bp.route('/admin/add_subject', methods=['POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    name = request.form.get('name')
    if Subject.query.filter_by(name=name).first():
        return redirect(url_for('admin_bp.admin_portal',flag="danger",message="Subject already exists!"))

    new_subject = Subject(name=name)
    db.session.add(new_subject)
    db.session.commit()
    print("Subject added: ",name)
    return redirect(url_for('admin_bp.manage_subjects'))

@admin_bp.route('/admin/delete_subject/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    subject = Subject.query.get(subject_id)
    if subject:
        print("Deleting subject:", subject.name)
        Chapter.query.filter_by(subject_id=subject_id).delete()
        db.session.delete(subject)
        db.session.commit()
        print("Subject deleted.")
    else:
        print("Subject not found.")

    return redirect(url_for('admin_bp.manage_subjects'))

@admin_bp.route('/admin/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        new_name = request.form.get('subject_name')
        if new_name:
            subject.name = new_name
            db.session.commit()
        return redirect(url_for('admin_bp.manage_subjects'))

    return render_template('edit_subject.html', subject=subject)


@admin_bp.route('/admin/add_chapter', methods=['POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    subject_id = request.form.get('subject_id')
    name = request.form.get('name')
    existing_chapter = Chapter.query.filter_by(subject_id=subject_id, name=name).first()
    if existing_chapter:
        return redirect(url_for('admin_bp.admin_portal', flag="danger", message="Chapter already exists!"))
    new_chapter = Chapter(subject_id=subject_id, name=name)
    db.session.add(new_chapter)
    db.session.commit()
    print("Chapter added: ",name)
    return redirect(url_for('admin_bp.manage_chapters'))

@admin_bp.route('/admin/delete_chapter/<int:chapter_id>')
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    chapter = Chapter.query.get(chapter_id)
    if chapter:
        print("Deleting chapter:", chapter.name)
        db.session.delete(chapter)
        db.session.commit()
        print("Chapter deleted.")
    else:
        print("Chapter not found.")

    return redirect(url_for('admin_bp.manage_chapters'))

@admin_bp.route('/admin/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == 'POST':
        new_name = request.form.get('chapter_name')
        if new_name:
            chapter.name = new_name
            db.session.commit()
        return redirect(url_for('admin_bp.manage_chapters'))

    return render_template('edit_chapter.html', chapter=chapter)


@admin_bp.route('/admin/add_quiz', methods=['POST'])
@login_required
def add_quiz():
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    chapter_id = request.form.get('chapter_id')
    title = request.form.get('title')
    time_duration = request.form.get('time_duration')

    new_quiz = Quiz(chapter_id=chapter_id, title=title, time_duration=time_duration)
    db.session.add(new_quiz)
    db.session.commit()
    print("new quiz added: ",title)
    return redirect(url_for('admin_bp.manage_quizzes'))

@admin_bp.route('/admin/delete_quiz/<int:quiz_id>')
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    quiz = Quiz.query.get(quiz_id)

    if quiz:
        print("Deleting quiz: ", quiz.title)
        db.session.delete(quiz)
        db.session.commit()
        print("Deleted quiz")

    return redirect(url_for('admin_bp.manage_quizzes'))

@admin_bp.route('/admin/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return redirect(url_for('main_bp.home'))

    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        new_title = request.form.get('quiz_title')
        if new_title:
            quiz.title = new_title
            db.session.commit()
        return redirect(url_for('admin_bp.manage_quizzes'))

    return render_template('edit_quiz.html', quiz=quiz)

@admin_bp.route('/manage_quiz/<int:quiz_id>')
def manage_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('manage_quiz.html', quiz=quiz, questions=questions)

@admin_bp.route('/quiz/<int:quiz_id>')
def quiz_page(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('quiz.html', quiz=quiz, questions=questions)