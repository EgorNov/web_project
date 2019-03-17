from flask import Flask, url_for, render_template

app = Flask(__name__)


@app.route('/')
def form_sample():
    return render_template('base.html', code=123)
@app.route('/')
def form_sample():
    return render_template('base.html', code=123)



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
