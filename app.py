from flask import Flask, render_template, request, session, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail
from flask_mail import Message
import json
import datetime
import requests


app = Flask(__name__)

# session unique key
app.secret_key = 'super-secret-key'

# connection to database
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(
    user='root', password='SAIkumar12', server='localhost', database='portfolio')

db = SQLAlchemy(app)

# loading json file
with open('config.json', 'r') as c:
    params = json.load(c)["params"]


# configuring the mail
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    email = db.Column(db.String(45), nullable=False)
    subject = db.Column(db.String(100))
    message = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(45))

    # def __repr__(self) -> str:
    #     return f'{self.username} {self.phoneNumber}  {self.date}'


class Skills(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(500), nullable=False)


class Certificates(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    certi_image = db.Column(db.String(55), nullable=False)
    certi_from = db.Column(db.String(45), nullable=False)
    certi_on = db.Column(db.String(45), nullable=False)
    discription = db.Column(db.String(100), nullable=False)
    certi_link = db.Column(db.String(500))

# functin for generating quotes using api


def quote():
    category = 'happiness'
    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(
        category)
    response = requests.get(
        api_url, headers={'X-Api-Key': 'UvqqsSrfxhB8CQEZnkY0GA==zEmZ9DY3mGHRrwm5'}).json()

    return response[0]['quote']

# home page


@app.route("/")
def home():
    return render_template('index.html', datetime=str(datetime.date.today()), quote="hello here is quote")


# about page
@app.route("/about")
def about():
    return render_template("about.html")


# logout function
@app.route('/logout')
def logout():
    if session.get('user'):
        # prevent flashing automatically logged out message
        del session['user']
    flash('You have successfully logged yourself out.')
    return render_template('login.html')


# login fuction into dashboard
@app.route("/login", methods=['GET', 'POST'])
def dashboard():
    # if user already logged in
    skill = Skills.query.all()
    certi = Certificates.query.all()
    if('user' in session and session['user'] == params['admin_mail']):

        return render_template('dashboard.html', skill=skill, certi=certi)
    # if user submits mail and password
    if(request.method == 'POST'):
        umail = request.form.get('umail')
        upass = request.form.get('upass')
        if(umail == params['admin_mail'] and upass == params['admin_pass']):
            session['user'] = umail
            # post = Posts.query.all()
            return render_template('dashboard.html', skill=skill, certi=certi)

    return render_template('login.html')


# skills posts delete func
@app.route("/skills/delete/<string:sno>", methods=['GET'])
def delete(sno):

    post = Skills.query.filter_by(sno=sno).first()
    db.session.delete(post)

    db.session.commit()

    return redirect('/login')


# certificate post delete func
@app.route("/certificate/delete/<string:sno>", methods=['GET'])
def certi_delete(sno):

    post = Certificates.query.filter_by(sno=sno).first()
    db.session.delete(post)

    db.session.commit()

    return redirect('/login')


# skills posts edit func
@app.route("/skills/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if('user' in session and session['user'] == params['admin_mail']):
        post = Skills.query.filter_by(sno=sno).first()
        if(request.method == 'POST'):
            # sno = request.form.get('sno')
            ttle = request.form.get('title')
            description = request.form.get('description')

            if(sno == '0'):
                entry = Skills(title=ttle,
                               description=description)

                db.session.add(entry)
                db.session.commit()
            else:

                post.title = ttle
                post.description = description

                db.session.commit()

        return render_template('edit.html', post=post, sno=sno)
    return render_template('login.html')


# certificates posts edit
@app.route("/certificates/edit/<string:sno>", methods=['GET', 'POST'])
def certi_edit(sno):
    if('user' in session and session['user'] == params['admin_mail']):
        post = Certificates.query.filter_by(sno=sno).first()
        if(request.method == 'POST'):
            # sno = request.form.get('sno')
            certi_image = request.form.get('certi_image')
            certi_from = request.form.get('certi_from')
            on = request.form.get('certi_on')
            certi_dis = request.form.get('certi_dis')
            certi_link = request.form.get('certi_link')

            if(sno == '0'):
                entry = Certificates(
                    certi_from=certi_from, certi_on=on, discription=certi_dis, certi_link=certi_link, certi_image=certi_image)

                db.session.add(entry)
                db.session.commit()
            else:
                post.certi_image = certi_image

                post.certi_from = certi_from
                post.certi_on = on
                post.discription = certi_dis
                post.certi_link = certi_link

                db.session.commit()

        return render_template('certi_edit.html', post=post, sno=sno)
    return render_template('login.html')


# int has been used as a filter that only integer will be passed in the url otherwise it will give a 404 error
@app.route('/hello')
def find_question():
    return render_template('hello.html')


# takes contact information and stors in database
@app.route("/contact", methods=['GET', 'POST'])
def contact_database():
    if(request.method == 'POST'):
        mail1 = request.form.get('email')
        sub = request.form.get('subject')
        msg = request.form.get('message')
        name = request.form.get('name')

        entry = Contact(name=name, email=mail1, subject=sub, message=msg,
                        date=datetime.datetime.now())
        db.session.add(entry)
        db.session.commit()

        mail.send_message('New message from ' + name,
                          sender=name,
                          recipients=['gmail@gmail.com'],
                          body=msg
                          )

    return render_template('contact.html')


# skills and certificates page
@app.route("/skills", methods=['GET', 'POST'])
def skills_database():
    skill = Skills.query.filter_by().all()
    certifi = Certificates.query.filter_by().all()
    return render_template('skills.html', sks=skill, certi=certifi)


@app.route("/cetificate")
def cer():
    return render_template('certification.html')


@app.route("/chatbot")
def chatbot():
    return render_template('chatbot.html')


# to run the flask app
if __name__ == "__main__":
    app.run(debug=True, port=3001)
