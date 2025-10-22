from flask import Blueprint,render_template,redirect,request,url_for,flash
from flask_login import login_required,current_user
from models.models import Quiz,Question,User,Subject,Chapter,UserAnswer,Score,db
from datetime import datetime
from collections import defaultdict

user_bp=Blueprint('user_bp',__name__)

@user_bp.route('/user')
@login_required
def user_portal():
    quizzes = Quiz.query.all()
    users = User.query.filter_by(is_admin=False).all()
    
    scores = Score.query.filter_by(user_id=current_user.id).all()

    score_distribution = {
        '0-50': 0,
        '51-70': 0,
        '71-85': 0,
        '86-100': 0
    }

    attempts_over_time = defaultdict(int)
    completion_percentage = 80  # Example static value

    for score in scores:
        percentage = score.total_score
        if percentage <= 50:
            score_distribution['0-50'] += 1
        elif percentage <= 70:
            score_distribution['51-70'] += 1
        elif percentage <= 85:
            score_distribution['71-85'] += 1
        else:
            score_distribution['86-100'] += 1

        week_num = score.time_stamp.isocalendar()[1]
        attempts_over_time[week_num] += 1

    attempts_over_time_data = {
        'labels': list(attempts_over_time.keys()),
        'data': list(attempts_over_time.values())
    }

    no_attempts = len(scores) == 0  # Flag

    return render_template(
        'user.html',
        username=current_user.full_name,
        score_distribution=score_distribution,
        attempts_over_time=attempts_over_time_data,
        completion_percentage=completion_percentage,
        no_attempts=no_attempts
    )


@user_bp.route('/user/profile')
@login_required
def user_profile():
    return render_template(
        'user_profile.html',
        full_name=current_user.full_name,
        email=current_user.username,
        dob=current_user.dob
    )
@user_bp.route('/user/profile/edit', methods=['GET', 'POST'])
@login_required
def user_edit_profile():
    if request.method == 'POST':
        # Update user attributes
        current_user.full_name = request.form.get('full_name')
        current_user.qualification = request.form.get('qualification')
        dob_str = request.form.get('dob')
        if dob_str:
            current_user.dob = datetime.strptime(dob_str, '%Y-%m-%d')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_bp.user_profile'))

    return render_template(
        'user_edit_profile.html',
        full_name=current_user.full_name,
        qualification=current_user.qualification,
        dob=current_user.dob.strftime('%Y-%m-%d') if current_user.dob else ''
    )
from sqlalchemy.orm import joinedload
@user_bp.route('/user/quizzes')
@login_required
def available_quiz():
    print("Function has been called")
    subjects = Subject.query.outerjoin(Chapter).outerjoin(Quiz).all()
    quizzes = Quiz.query.all() 
    print("Quizzes fetched:", quizzes)
    print("Subjects fetched:", subjects)
    return render_template('available_quiz.html',subjects=subjects,quizzes=quizzes)

@user_bp.route('/user/prev')
@login_required
def previous_scores():
    sort_by = request.args.get('sort_by', 'desc')
    query = Score.query.filter_by(user_id=current_user.id)

    if sort_by == 'asc':
        scores = query.order_by(Score.time_stamp.asc()).options(
            joinedload(Score.quiz).joinedload(Quiz.chapter).joinedload(Chapter.subject)
        ).all()
    else:
        scores = query.order_by(Score.time_stamp.desc()).options(
            joinedload(Score.quiz).joinedload(Quiz.chapter).joinedload(Chapter.subject)
        ).all()
    return render_template('previous_quiz.html', scores=scores)

@user_bp.route('/user/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    if quiz.time_duration:
        hh, mm = map(int, quiz.time_duration.split(":"))
        total_minutes = hh * 60 + mm
    else:
        total_minutes = 10
    print("Total mins..",total_minutes)
    return render_template('quiz.html', quiz=quiz, questions=questions,total_minutes=total_minutes)

@user_bp.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    score = 0
    user_answers_to_commit = []

    new_score = Score(user_id=current_user.id, quiz_id=quiz_id, total_score=0)
    db.session.add(new_score)
    db.session.commit() 

    for question in questions:
        selected_answer = request.form.get(f"answer_{question.id}")     
        if selected_answer and selected_answer == question.correct_option:
            score += 1

        user_answer = UserAnswer(
            user_id=current_user.id,
            question_id=question.id,
            selected_option=selected_answer if selected_answer else None, 
            attempt_id=new_score.id 
        )
        user_answers_to_commit.append(user_answer)
        
    new_score.total_score = score
    db.session.add_all(user_answers_to_commit)
    db.session.commit() 
    
    return render_template('quiz_result.html', quiz=quiz, score=score, total_questions=len(questions), score_id=new_score.id)

@user_bp.route('/quiz/performance/<int:score_id>')
@login_required
def quiz_performance(score_id):
    user_score = Score.query.get_or_404(score_id)
    if user_score.user_id != current_user.id:
        flash('You do not have permission to view this score.', 'danger')
        return redirect(url_for('user_bp.previous_scores'))
    quiz = Quiz.query.options(
        joinedload(Quiz.chapter).joinedload(Chapter.subject)
    ).get_or_404(user_score.quiz_id)
    questions = quiz.questions 
    user_answers_list = UserAnswer.query.filter_by(attempt_id=score_id).all()
    user_answers_map = {
        answer.question_id: answer.selected_option
        for answer in user_answers_list
    }
    correct_count = 0
    incorrect_count = 0
    unattempted_count = 0
    for question in questions:
        user_selection_key = user_answers_map.get(question.id)
        
        if user_selection_key is None:
            unattempted_count += 1
        elif user_selection_key == question.correct_option:
            correct_count += 1
        else:
            incorrect_count += 1

    return render_template(
        'quiz_performance.html',
        quiz=quiz,
        questions=questions,
        user_score=user_score,
        user_answers=user_answers_map,
        correct_count=correct_count,
        incorrect_count=incorrect_count,
        unattempted_count=unattempted_count
    )

@user_bp.route('/user/search', methods=['GET'])
@login_required
def user_search():
    query = request.args.get('q', '').strip()
    results = {"subjects": [], "chapters": [], "quizzes": []}

    if query:
        results["subjects"] = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        results["chapters"] = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
        results["quizzes"] = Quiz.query.filter(Quiz.title.ilike(f"%{query}%")).all()

    return render_template('user_search.html', query=query, results=results)

@user_bp.route('/quiz/<int:quiz_id>')
def quiz_page(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    return render_template('quiz.html', quiz=quiz, questions=questions)