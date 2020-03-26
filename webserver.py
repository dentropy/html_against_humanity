from flask import Flask, request, url_for, render_template, make_response, session, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("homepage.html")

if __name__ == '__main__':
    app.run()
