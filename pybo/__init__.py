from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pybo.filter import format_datetime



import config

db = SQLAlchemy()
migrate = Migrate()

# 애플리케이션 팩토리 함수정의
def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM 초기화
    from . import models
    db.init_app(app) 
    migrate.init_app(app, db)

    # jinja_env 필터에 등록
    app.jinja_env.filters['datetime'] = format_datetime

    # 블루프린트 등록
    from .views import main_views, question_views, answer_views, auth_views, comment_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(answer_views.bp)
    app.register_blueprint(auth_views.bp) # 회원 가입 등록
    app.register_blueprint(comment_views.bp)
    
    return app