from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
import os
app=Flask(__name__)
app.debug=True
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///paintings.db'
app.config['UPLOAD_FOLDER']='static/upload/'
app.config['MAX_CONTENT']=16*1024*1024
ALLOWED_EXTENSIONS=['png', 'jpeg', 'jpg', 'gif']
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
db=SQLAlchemy(app)
class Paintings(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    painting_title=db.Column(db.String(50), unique=False, nullable=False)
    description=db.Column(db.String, unique=False, nullable=False)
    artist = db.Column(db.String(20), unique=False, nullable=False)
    current_location=db.Column(db.String(20), unique=False, nullable=False)
    date_created=db.Column(db.Integer, unique=False, nullable=False)
    filename=db.Column(db.String(100), unique=False, nullable=True)
    def __repr__(self):
        return f"Title:{self.painting_title}, Artist: {self.artist}"
class Reviews(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    painting_id=db.Column(db.Integer, unique=False, nullable=False)
    name=db.Column(db.String(20), unique=False, nullable=False)
    review_text=db.Column(db.String, unique=False, nullable=False)
    rating=db.Column(db.Integer,unique=False, nullable=False )
    def __repr__(self):
        return f"Name:{self.name}, Content: {self.review_text}, Rate:{self.rating}"

migrate=Migrate(app,db)

@app.route("/")
def home():
    paintings_data=Paintings.query.all()
    return render_template("index.html", painting_data=paintings_data)

@app.route("/add_data")
def add_data():
    return render_template("add_profile.html")

@app.route("/add", methods=["POST", "GET"])
def painting_management():
    if request.method=="POST":
        painting_title=request.form.get("painting_title")
        description = request.form.get("description")
        artist = request.form.get("artist")
        current_location = request.form.get("current_location")
        date_created = request.form.get("date_created")
        file=request.files.get("filename")
        if allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        file_name=file.filename
        painting_row=Paintings(painting_title=painting_title,artist=artist, current_location=current_location,
                         description=description, date_created=date_created, filename=file_name)
        db.session.add(painting_row)
        db.session.commit()
        return redirect("/")

@app.route("/display/<filename>")
def display_image(filename):
    return redirect(url_for('static', filename='upload/' + filename))
@app.route('/painting_info/<painting_id>')
def painting_info(painting_id):
    painting_specific = Paintings.query.get(painting_id)
    reviews_specific=Reviews.query.filter(Reviews.painting_id==painting_id)
    return render_template("painting_info.html", painting_specific=painting_specific, reviews_specific=reviews_specific)

@app.route("/add_review", methods=["POST", "GET"])
def review_management():
    if request.method=="POST":
        name=request.form.get("name")
        review_text = request.form.get("review_text")
        painting_id = request.form.get("painting_id")
        rating=request.form.get("rating")
        review_row=Reviews(name=name, review_text=review_text, painting_id=painting_id,
                           rating=rating)
        db.session.add(review_row)
        db.session.commit()
        return redirect("/")

@app.route("/delete/<int:id>")
def erase(id):
    data=Paintings.query.get(id)
    filename=data.filename
    os.remove(f"{app.config['UPLOAD_FOLDER']}/{filename}")
    db.session.delete(data)
    reviews_specific = Reviews.query.filter(Reviews.painting_id == id)
    for review in reviews_specific:
        db.session.delete(review)
    db.session.commit()
    return redirect("/")

@app.route("/alter_painting/<int:id>", methods=["POST", "GET"])
def alter_painting(id):
    if request.method=="POST":
        data=Paintings.query.get(id)
        painting_title = request.form.get("painting_title")
        description = request.form.get("description")
        artist = request.form.get("artist")
        current_location = request.form.get("current_location")
        date_created = request.form.get("date_created")
        file = request.files.get("filename")
        if allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        file_name=file.filename
        if request.form.get("painting_title"):
            data.painting_title=painting_title
        if request.form.get("description"):
            data.description = description
        if  request.form.get("artist"):
            data.artist = artist
        if  request.form.get("current_location"):
            data.current_location = current_location
        if request.form.get("date_created"):
            data.description = date_created
        if request.files.get("filename"):
            data.filename = file_name
        db.session.commit()
        return redirect(url_for('painting_info', painting_id=id))
    else:
        return render_template("alter_painting.html")

@app.route("/", methods=["GET", "POST"])
def index():
        if request.method == 'POST':
            search = request.form["searchBar"]
            painting_specific = Paintings.query.filter(Paintings.painting_title.ilike(search)).all()[0]
            reviews_specific = Reviews.query.filter(Reviews.painting_id == painting_specific.id)
        return render_template("painting_info.html",painting_specific=painting_specific, reviews_specific=reviews_specific)


if __name__=="__main__":
    app.run()




