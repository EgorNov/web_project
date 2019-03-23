import sqlite3
from flask import Flask, url_for, render_template, redirect, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'NovOsti_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


class NewsForm(FlaskForm):
    submit = SubmitField('Нравится')


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    short_dis = TextAreaField('Краткое описание', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class DB:
    def __init__(self):
        conn = sqlite3.connect('news.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class NewsModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS news 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             title VARCHAR(100),
                             short_dis VARCHAR(500),
                             content MEDIUMTEXT,
                             user_id INTEGER,
                             users MEDIUMTEXT,
                             likes INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, title, short_dis, content, user_id):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO news 
                          (title, short_dis, content, user_id, users, likes) 
                          VALUES (?,?,?,?,?,?)''', (title, short_dis, content, str(user_id), ' ', 0))
        cursor.close()
        self.connection.commit()

    def update(self, news_id, users, likes):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE news
    SET users=?,likes=?
    WHERE id=?''', (users, str(likes), str(news_id)))
        cursor.close()
        self.connection.commit()

    def get(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news WHERE id = ?", (str(news_id),))
        row = cursor.fetchone()
        return row

    def get_all(self, user_id=None):
        if user_id:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM news WHERE user_id = ?", (str(user_id)))
            rows = cursor.fetchall()[::-1]
            return rows
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM news ")
        rows = cursor.fetchall()[::-1]

        return rows

    def delete(self, news_id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM news WHERE id = ?''', (str(news_id),))
        cursor.close()
        self.connection.commit()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128),
                             rating INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash, rating) 
                          VALUES (?,?,?)''', (user_name, password_hash, 0))
        cursor.close()
        self.connection.commit()

    def update(self, user_id, rating):
        cursor = self.connection.cursor()
        cursor.execute('''UPDATE users
    SET rating=?
    WHERE id=?''', (str(rating), str(user_id)))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


db = DB()
us = UsersModel(db.get_connection())
us.init_table()
ns = NewsModel(db.get_connection())
ns.init_table()


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    news = NewsModel(db.get_connection()).get_all()
    return render_template('main.html', username=session['username'],
                           news=news)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        short_dis = form.short_dis.data
        content = form.content.data
        nm = NewsModel(db.get_connection())
        nm.insert(title, short_dis, content, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости',
                           form=form, username=session['username'])


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        exists = us.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'GET':
        form = RegForm()
        if form.validate_on_submit():
            return redirect('/')
        return render_template('reg.html', title='Авторизация', form=form)
    elif request.method == 'POST':
        us.insert(request.form['username'], request.form['password'])
        return redirect('/')


@app.route('/<news_id>', methods=['GET', 'POST'])
def news(news_id):
    news = ns.get(news_id)
    users = news[5].split()
    content = news[3].split('\r\n')
    if request.method == 'GET':
        form = NewsForm()
        return render_template('watch_news.html', news=news, form=form, likes=news[6], content=content,
                               user=us.get(news[4])[1])
    elif request.method == 'POST':
        if str(session['user_id']) not in users and session['user_id'] != news[4]:
            users.append(str(session['user_id']))
            us.update(news[4], us.get(news[4])[3] + 1)
            ns.update(news_id, ' '.join(users), news[6] + 1)
        elif str(session['user_id']) in users:
            del users[users.index(str(session['user_id']))]
            us.update(news[4], us.get(news[4])[3] - 1)
            ns.update(news_id, ' '.join(users), news[6] - 1)
        return redirect('/' + str(news_id))


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user(user_id):
    user = us.get(user_id)
    news = ns.get_all(user_id)
    return render_template('profile.html', user=user, news=news)


@app.route('/about_us')
def about():
    return render_template('about_us.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
