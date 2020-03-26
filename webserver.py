from flask import Flask, request, url_for, render_template, make_response, session, redirect
from database import session, UserSessions
from cookie_generator import generate_random_cookie

app = Flask(__name__)
app.config['SECRET_KEY'] =  'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

@app.route('/')
def index():
    cookie = request.cookies.get("game_session")
    print("User connected:", cookie)
    return render_template("homepage.html")

@app.route('/cookie')
def create_cookie():
    cookie = request.cookies.get("game_session")
    print(cookie)
    if not cookie:
        res = make_response(redirect('/'))
        unique_cookie = generate_random_cookie()
        session.add(UserSessions(user_cookie=unique_cookie))
        session.commit()
        res.set_cookie("game_session", unique_cookie, max_age=60*60*24*365*2)
        return res
    else:
        return make_response(redirect('/'))

if __name__ == '__main__':
    app.run()
