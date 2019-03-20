from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class YandexLyceumStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), unique=False, nullable=False)
    surname = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    group = db.Column(db.String(80), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<YandexLyceumStudent {} {} {} {}>'.format(
            self.id, self.username, self.name, self.surname)



db.create_all()
user1 = YandexLyceumStudent(username='student1',
                            email='student1@yandexlyceum.ru',
                            name='Иван',
                            surname='Иванов',
                            group='Пенза, Лицей 2',
                            year=2)

user2 = YandexLyceumStudent(username='student2',
                            email='student2@yandexlyceum.ru',
                            name='Петр',
                            surname='Петров',
                            group='Москва, Лицей 1234',
                            year=1)
db.session.add(user1)
db.session.add(user2)
db.session.commit()
print(YandexLyceumStudent.query.all())
print(YandexLyceumStudent.query.filter_by(name='Петр').first())