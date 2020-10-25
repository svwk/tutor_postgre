import json
import random
import secrets
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import OperationalError, ProgrammingError

import forms

db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)
csrf = CSRFProtect(app)
SECRET_KEY = secrets.token_urlsafe()
app.config['SECRET_KEY'] = SECRET_KEY


def load_db():
    try:
        with open('config.json', 'r') as f:
            config = (json.load(f))
    except FileNotFoundError:
        config = None
    
    if config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tutordb.db"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = config["connection_string"][config["dbtype"]][1]
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    migrate.init_app(app, db)


load_db()


class TimeValue(db.Model):
    __tablename__ = 'time_values'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(5), nullable=False)
    order = db.Column(db.Integer, unique=True, nullable=False)
    
    schedules = db.relationship("Schedule", back_populates='time')


class DayValue(db.Model):
    __tablename__ = 'day_values'
    id = db.Column(db.String(3), primary_key=True, unique=True, nullable=False, autoincrement=False)
    name = db.Column(db.String(20), nullable=False)
    order = db.Column(db.Integer, unique=True, nullable=False)
    
    schedules = db.relationship("Schedule", back_populates='day')


goals_teachers = db.Table('goals_teachers',
                          db.Column('goal_id', db.String(10), db.ForeignKey('goals.id')),
                          db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'))
                          )


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    sign = db.Column(db.String(1), default="")
    
    teachers = db.relationship('Teacher', secondary=goals_teachers, back_populates='goals')


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    about = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    picture = db.Column(db.String(50), default="")
    price = db.Column(db.Integer, default=100)
    
    goals = db.relationship('Goal', secondary=goals_teachers, back_populates='teachers')
    schedules = db.relationship("Schedule", back_populates='teacher')


class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Boolean, default=True)
    
    day_id = db.Column(db.String(3), ForeignKey('day_values.id'), nullable=False)
    day = db.relationship("DayValue", back_populates='schedules')
    time_id = db.Column(db.Integer, ForeignKey('time_values.id'), nullable=False)
    time = db.relationship("TimeValue", back_populates='schedules')
    teacher_id = db.Column(db.Integer, ForeignKey('teachers.id'), nullable=False)
    teacher = db.relationship("Teacher", back_populates='schedules')
    bookings = db.relationship("Booking", back_populates='schedule')


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    goal = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(20), nullable=False)


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)
    
    schedule_id = db.Column(db.Integer, ForeignKey('schedules.id'), nullable=False)
    schedule = db.relationship("Schedule", back_populates='bookings')


@app.route('/reloaddb/')
def reload_db():
    load_db()
    return redirect(url_for('render_main'))


@app.route('/createdb/')
def create_db():
    db.drop_all()
    db.create_all()
    import data
    day_values = []
    for num, val in enumerate(data.weekdays, 1):
        day_values.append(DayValue(id=val[0], name=val[1], order=num))
    
    time_values = []
    for num, val in enumerate(data.time_values, 1):
        time_values.append(TimeValue(value=val, order=num))
    
    goals = []
    for key, val in data.goals.items():
        goals.append(Goal(id=key, title=val[0], sign=val[1]))
    
    teachers = []
    schedules = []
    
    for t in data.teachers:
        teacher = Teacher(id=t["id"], name=t["name"], about=t["about"], rating=t["rating"], picture=t["picture"],
                          price=t["price"])
        for g in t["goals"]:
            goal = next((gg for gg in goals if gg.id == g))
            if goal:
                teacher.goals.append(goal)
        
        teachers.append(teacher)
        
        for day, val in t["free"].items():
            for time, status in val.items():
                day_obj = next((d for d in day_values if d.id == day))
                time_obj = next((tt for tt in time_values if tt.value == time))
                sh = Schedule(value=status, day=day_obj, time=time_obj, teacher=teacher)
                schedules.append(sh)
    
    db.session.add_all(day_values)
    db.session.add_all(time_values)
    db.session.add_all(goals)
    db.session.add_all(teachers)
    db.session.add_all(schedules)
    db.session.commit()
    return redirect(url_for('render_main'))


@app.route('/')
def render_main():
    # Загрузка данных
    try:
        teachers = db.session.query(Teacher).all()
        goals = db.session.query(Goal).all()
    except OperationalError:
        # Ошибка, которую выдает локальный сервер, когда не может найти бд
        return render_template('bd_empty.html')
    except ProgrammingError:
        # Ошибка, которую выдает Heroku, когда не может найти бд
        return render_template('bd_empty.html')
    
    if len(teachers) > 6:
        random.seed()
        teachers = random.sample(teachers, 6)
    
    return render_template('index.html', goals=goals, teachers=teachers)


@app.route('/goals/<goal>/')
def render_goals_item(goal):
    # Загрузка данных
    try:
        goals = db.session.query(Goal).all()
        goal_obj = db.session.query(Goal).filter(Goal.id == goal).first()
        if goal_obj is None:
            return render_template('error.html', text="К сожалению, вы ввели неверную цель"), 404
    
    except OperationalError:
        return render_template('bd_empty.html')
    except ProgrammingError:
        return render_template('bd_empty.html')
    
    return render_template('goal.html', goals=goals, teachers=goal_obj.teachers, goal=goal_obj)


@app.route('/profiles/<int:teacher_id>/')
def render_profiles_item(teacher_id):
    # Загрузка данных
    try:
        teacher = db.session.query(Teacher).get(teacher_id)
        goals = db.session.query(Goal).all()
        weekdays = db.session.query(DayValue).order_by(DayValue.order).all()
    except OperationalError:
        return render_template('bd_empty.html')
    except ProgrammingError:
        return render_template('bd_empty.html')
    
    if teacher is None:
        return render_template('error.html', text="К сожалению, данного преподавателя в нашей базе данных нет"), 404
    
    free_days = []
    for day in weekdays:
        tt = [s for s in teacher.schedules if (s.day_id == day.id and s.value)]
        if tt:
            free_days.append({day.name: sorted(tt, key=lambda x: x.time.order)})
        else:
            free_days.append({day.name: []})
    
    return render_template('profile.html', t=teacher, goals=goals, free_days=free_days)


@app.route('/request/', methods=['GET', 'POST'])
def render_request():
    form = forms.RequestForm()
    return render_template('request.html', form=form)


@app.route('/request_done/', methods=['POST'])
def render_request_done():
    # Если данные не были отправлены
    if request.method != "POST":
        # Если пользователь попал на эту страницу не из формы ввода, выдаем 404 ошибку
        return render_template('error.html', text="К сожалению, данной страницы не существует"), 404
    
    # Если данные были отправлены
    form = forms.RequestForm()
    if not form.validate_on_submit():
        # отправляем форму назад
        return render_template('request.html', form=form)
    
    # получаем данные
    client_name = form.clientName.data
    client_phone = form.clientPhone.data
    client_goal = form.clientGoal.data
    client_time = form.clientTime.data
    
    goal = next((g[1] for g in form.clientGoal.choices if g[0] == client_goal), -1)
    time = next((t[1] for t in form.clientTime.choices if t[0] == client_time), -1)
    
    if goal == -1 or time == -1:
        return render_template('error.html', text="К сожалению, вы ввели неверные данные"), 404
    
    # сохраняем данные
    try:
        db.session.add(Request(name=client_name, phone=client_phone, goal=goal, time=time))
        db.session.commit()
    except OperationalError:
        return render_template('bd_empty.html')
    
    # переходим на request_done
    return render_template('request_done.html', clientName=client_name, clientPhone=client_phone,
                           clientGoal=goal, clientTime=time)


@app.route('/booking/<int:teacher_id>/<weekday>/<time>/', methods=['GET', 'POST'])
def render_booking_item(teacher_id, weekday, time):
    # Проверка состояния бд
    try:
        time_obj = db.session.query(TimeValue).filter(TimeValue.value == time).first()
        weekday_obj = db.session.query(DayValue).get(weekday)
        teacher = db.session.query(Teacher).get(teacher_id)
    except OperationalError:
        return render_template('bd_empty.html')
    except ProgrammingError:
        return render_template('bd_empty.html')
    
    form = forms.BookingForm()
    if request.method == "POST":
        # если данные post и get отличаются, приводим их к одному виду
        time = form.clientTime.data
        teacher_id = int(form.clientTeacher.data)
        weekday = form.clientWeekday.data
    
    # Проверки входных данных
    if time_obj is None:
        return render_template('error.html', text="К сожалению, вы ввели неверное время"), 404
    
    if weekday_obj is None:
        return render_template('error.html', text="К сожалению, вы ввели неверный день недели"), 404
    
    if teacher is None:
        return render_template('error.html', text="К сожалению, данного преподавателя в нашей базе данных нет"), 404
        
        # Если данные были отправлены
    if request.method == "POST":
        if form.validate_on_submit():
            # получаем данные
            client_name = form.clientName.data
            client_phone = form.clientPhone.data
            
            schedule = db.session.query(Schedule).filter(
                (Schedule.day_id == weekday) & (Schedule.time_id == time_obj.id) & (
                        Schedule.teacher_id == teacher_id)).first()
            if not schedule.value:
                return render_template('error.html', text="К сожалению, указанное время занято"), 200
            
            schedule.value = False
            
            # сохраняем данные
            db.session.add(schedule)
            
            db.session.add(Booking(name=client_name, phone=client_phone, schedule=schedule))
            db.session.commit()
            
            # переходим на booking_done
            return render_template('booking_done.html', clientName=client_name, clientPhone=client_phone,
                                   clientWeekday=weekday_obj.name, clientTime=time)
    
    # Если данные еще НЕ были отправлены или неверны
    # выводим форму
    form.clientTime.data = time
    form.clientTeacher.data = teacher_id
    form.clientWeekday.data = weekday
    return render_template('booking.html', form=form, t=teacher, weekday=weekday_obj, time=time)


@app.errorhandler(404)
def render_not_found(error):
    return render_template('error.html', text="Ничего не нашлось!"), 404


@app.errorhandler(500)
def render_server_error(error):
    return render_template('error.html',
                           text="Что-то не так, но мы все починим:\n{}".format(error.original_exception)), 500


if __name__ == '__main__':
    app.run()
