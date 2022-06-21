from flask import Flask, Response, redirect, url_for, request, session, abort, render_template,flash
from flask_login import LoginManager, UserMixin,login_required, login_user, logout_user,current_user
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


import sqlite3 as sql



#conn = sql.connect('blog.db')
#print("BD otwarta")
#conn.execute('CREATE TABLE posty (id TEXT, data TEXT, tytul TEXT NOT NULL, tresc TEXT NOT NULL, nick TEXT NOT NULL)')
#print("Tabela utworzona")
#conn.commit()
#conn.close()

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='619619'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)







class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))

@login_manager.user_loader
def get(id):
    return User.query.get(id)






@app.route('/',methods=['GET'])
def main():
	return render_template('index.html',tytul='Strona główna')




@app.route('/addpost',methods = ['POST', 'GET'])
def addpost():

 if request.method == 'POST':

  now = datetime.now()
  data = now.strftime("%d/%m/%Y %H:%M:%S")
  try:
   id = request.form['id']
   tytul = request.form['tytulposta']
   tresc = request.form['trescposta']
   nick = current_user.username
   with sql.connect("blog.db") as con:

    cur = con.cursor()
    cur.execute("INSERT INTO posty (id,data,tytul,tresc,nick) VALUES (?,?,?,?,?)",(id,data,tytul,tresc,nick) )
    con.commit()
    msg = "Post został zapisany"
  except:
     con.rollback()
     msg = "Błąd przy dodawaniu posta"
  finally:
     return render_template("rezultat1.html",tytul = 'Wynik dodawania posta...',msg = msg)
     con.close()

@app.route('/delpost',methods = ['POST', 'GET'])
def delpost():

 if request.method == 'POST':
  try:
   id = request.form['id']
   with sql.connect("blog.db") as con:

    cur = con.cursor()
    cur.execute("DELETE FROM posty WHERE id =?",(id,) )
    con.commit()
    msg = "Post został usunięty"
  except:
     con.rollback()
     msg = "Błąd przy usuwaniu posta"
  finally:
     return render_template("rezultat.html",tytul = 'Wynik usuwania posta...',msg = msg)
     con.close()


@app.route("/dodaj-post")
@login_required
def new_post():
 	return render_template('postadd.html', tytul = 'Dodaj post')

@app.route("/usun-post")
@login_required
def del_post():
 	return render_template('postdel.html',tytul='Usuń post')


@app.route('/blog')
def blog():

 con = sql.connect("blog.db")
 con.row_factory = sql.Row
 cur = con.cursor()
 cur.execute('SELECT * FROM posty ORDER BY data')
 posty = cur.fetchall();
 return render_template("blog.html",tytul='Blog', posty = posty)


@app.route('/login',methods=['GET'])
def get_login():
    return render_template('formularz_logowania.html', tytul= 'Zaloguj się')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email,password=password).first()
    login_user(user)
    return redirect('/')



@app.route('/signup',methods=['GET'])
def get_signup():
    return render_template('signup.html',tytul='Zarejestruj nowe konto')

@app.route('/signup',methods=['POST'])
def signup_post():
    username = request.form['username']
    email = request.form['email']
    password1 = request.form['password1']
    password2 = request.form['password2']

    email_exists = User.query.filter_by(email=email).first()
    username_exists = User.query.filter_by(username=username).first()

    if email_exists:
            tytul="Mail jest już zajęty!"
            blad = "01"
            return render_template('blad.html', tytul=tytul, blad=blad)
    elif username_exists:
            tytul="Nick jest już zajęty!"
            blad = "02"
            return render_template('blad.html', tytul=tytul, blad=blad)
    elif password1 != password2:
            tytul="Hasła nie są takie same!"
            blad = "03"
            return render_template('blad.html', tytul=tytul, blad=blad)
    else:
        user = User(username=username,email=email,password=password1)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/')

@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    return render_template('logout.html', tytul='Wylogowanie')

@app.errorhandler(401)
def page_not_found(e):
 tytul="Coś poszło nie tak..."
 blad = "401"
 return render_template('blad.html', tytul=tytul, blad=blad)

@app.errorhandler(500)
def internal_server_error(e):
    tytul="Błędny login lub hasło"
    blad = "500"
    return render_template('blad.html', tytul=tytul, blad=blad)





if __name__ == "__main__":
	app.run(debug=True)
