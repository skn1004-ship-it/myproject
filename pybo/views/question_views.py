from flask import Blueprint, render_template, url_for, redirect, request, g, flash
from pybo.models import Question
from datetime import datetime
from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required # 데코레이터 임포트

bp = Blueprint('question', __name__, url_prefix='/question')

@bp.route('/List/')
def _list():
    # 현재 페이지 번호 가져오기 (기본값은 1)
    page = request.args.get('page', type=int, default=1)
    question_list = Question.query.order_by(Question.create_date.desc()).paginate(page=page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list)

@bp.route('detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()  # 상세 조회 라우터 내부에서 빈 답변 폼 생성
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question=question, form=form)

# 질문 등록 라우트 함수 추가
@bp.route('/create/', methods=('GET', 'POST'))
@login_required # 인증 유효성 상시 체크 가동
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, content=form.content.data, create_date=datetime.now(), user=g.user)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('question._list'))
    return render_template('question/question_form.html', form=form)

@bp.route('/modify/<int:question_id>/', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    if request.method == 'POST':
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question) # 폼 데이터를 question 객체에 동적 복사
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:
        # GET 요청일 경우 기존 데이터를 폼에 채워서 렌더링
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)

@bp.route('/delete/<int:question_id>/')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))

@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)

    # 로그인한 사용자가 본인의 글을 추천하는 것을 막음.
    if g.user == question.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))

    # 중복 추천 방지 로직
    if g.user in question.voter:
        flash('이미 추천한 질문입니다')
        return redirect(url_for('question.detail', question_id=question_id))
    
    # 기존 추천 처리 로직
    question.voter.append(g.user)
    db.session.commit()
    
    return redirect(url_for('question.detail', question_id=question_id))



