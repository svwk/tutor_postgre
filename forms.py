from flask_wtf import FlaskForm
import wtforms
from wtforms import validators

TEL_REG = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$'


class BookingForm(FlaskForm):
    clientName = wtforms.StringField("Вас зовут", [validators.InputRequired(message="Необходимо ввести имя")])
    clientPhone = wtforms.StringField("Ваш телефон", [validators.InputRequired(message="Необходимо ввести телефон"),
                                                      validators.regexp(
                                                          TEL_REG,
                                                          message="Телефон должен содержать от 6 до 11 цифр")])
    clientTeacher = wtforms.HiddenField()
    clientWeekday = wtforms.HiddenField()
    clientTime = wtforms.HiddenField()


class RequestForm(FlaskForm):
    clientName = wtforms.StringField("Вас зовут", [validators.InputRequired(message="Необходимо ввести имя")])
    clientPhone = wtforms.StringField("Ваш телефон",
                                      [validators.InputRequired(message="Необходимо ввести телефон"),
                                       validators.regexp(
                                           TEL_REG,
                                           message="Телефон должен содержать от 6 до 11 цифр")])
    clientGoal = wtforms.RadioField('Какая цель занятий?', default="travel",
                                    choices=[("travel", "Для путешествий"), ("study", "Для учебы"),
                                             ("work", "Для работы"), ("relocate", "Для переезда"),
                                             ("coding", "для программирования")])
    clientTime = wtforms.RadioField('Сколько времени есть?', default="1-2",
                                    choices=[("1-2", "1-2 часа в неделю"), ("3-5", "3-5 часов в неделю"),
                                             ("5-7", "5-7 часов в неделю"), ("7-10", "7-10 часов в неделю")])
