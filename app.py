from flask import Flask, render_template, request, jsonify, send_file, session, redirect, flash, get_flashed_messages
import requests
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

app = Flask(__name__)

csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Login.db'
app.config['SECRET_KEY'] = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3)])
    password = PasswordField('Password', [validators.Length(min=3)])

class RegistrationForm(FlaskForm):
    dusername = StringField('DUsername', [validators.Length(min=4)])
    dpassword = PasswordField('DPassword', [validators.Length(min=4)])
    email = StringField('EmailUser', [validators.Email()])

@app.route('/set_ngrok')
def set_ngrok():
    return render_template("set_ngrok.html")

@app.route('/loggedIn')
def logged_in():
    return render_template("loggedIn.html")

@app.route("/")
def homepage():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    return render_template("index.html", login_form=login_form, registration_form=registration_form)

@app.route("/login", methods=["POST"])
def check_login():
    UN = request.form['Username']
    entered_password = request.form['Password']

    user = User.query.filter_by(username=UN).first()
    if user and check_password_hash(user.password, entered_password):
        session['user_id'] = user.id
        return redirect('/set_ngrok')
    else:
        flash("Invalid username or password. Please try again.", "error")
        return redirect("/")

@app.route('/register', methods=['POST'])
def register_page():
    dUN = request.form['DUsername']
    dPW = generate_password_hash(request.form['DPassword'], method='pbkdf2:sha256')
    Uemail = request.form['EmailUser']

    existing_user = User.query.filter_by(username=dUN).first()
    if existing_user:
        flash("Username already exists. Please choose a different username.", "error")
    else:
        new_user = User(username=dUN, password=dPW, email=Uemail)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/')
    return render_template("index.html")

@app.route('/set_ngrok_url', methods=['POST'])
def set_ngrok_url():
    ngrok_url = request.form.get('ngrok_url')
    session['ngrok_url'] = ngrok_url
    return redirect("/loggedIn")

@app.route('/image')
def index():
    return render_template('image.html')

@app.route('/video')
def video_index():
    return render_template('video.html')

@app.route('/image2')
def image2():
    return render_template('image2.html')

@app.route('/models')
def models():
    return render_template('models.html')

def get_ngrok_url():
    return session.get('ngrok_url', '')

@app.route('/history')
def history():
    user_id = session.get('user_id')
    if user_id:
        images = Image.query.filter_by(user_id=user_id).all()
        return render_template('history.html', images=images)
    else:
        return redirect('/')

@app.route('/download_image/<int:image_id>')
def download_image(image_id):
    image = Image.query.get(image_id)
    if image:
        return send_file(BytesIO(image.image), mimetype='image/png', as_attachment=True, download_name='generated_image.png')
    return jsonify(error="Image not found"), 404

@app.route('/generate_image', methods=['POST'])
def generate_image():
    prompt = request.form.get('text')
    if not prompt:
        return jsonify(error="No prompt provided"), 400

    try:
        ngrok_url = f"{get_ngrok_url()}/generate_image"
        response = requests.post(ngrok_url, data={'text': prompt}, timeout=1200)
        response.raise_for_status()

        img = BytesIO(response.content)

        user_id = session.get('user_id')
        if user_id:
            new_image = Image(user_id=user_id, image=img.read())
            db.session.add(new_image)
            db.session.commit()

        img.seek(0)
        return send_file(img, mimetype='image/png')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error generating image: {e}")
        return jsonify(error=str(e)), 500

@app.route('/generate_image_new', methods=['POST'])
def generate_image_new():
    prompt = request.form.get('text')
    if not prompt:
        return jsonify(error="No prompt provided"), 400

    try:
        ngrok_url = f"{get_ngrok_url()}/generate_image_new"
        response = requests.post(ngrok_url, data={'text': prompt}, timeout=1200)
        response.raise_for_status()

        if 'image' not in response.headers['Content-Type']:
            return jsonify(error="Generated content is not an image"), 500

        img = BytesIO(response.content)

        user_id = session.get('user_id')
        if user_id:
            new_image = Image(user_id=user_id, image=img.read())
            db.session.add(new_image)
            db.session.commit()

        img.seek(0)
        return send_file(img, mimetype='image/png')
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error generating image: {e}")
        return jsonify(error=str(e)), 500

@app.route('/generate_video', methods=['POST'])
def generate_video():
    prompt = request.form.get('text')
    if not prompt:
        return jsonify(error="No prompt provided"), 400

    try:
        ngrok_url = f"{get_ngrok_url()}/generate_video"
        response = requests.post(ngrok_url, data={'text': prompt}, timeout=1200)
        response.raise_for_status()

        video = BytesIO(response.content)
        return send_file(video, mimetype='video/mp4', as_attachment=False)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error generating video: {e}")
        return jsonify(error=str(e)), 500

@app.route('/image/<int:image_id>')
def serve_image(image_id):
    image = Image.query.get(image_id)
    if image:
        return send_file(BytesIO(image.image), mimetype='image/png')
    return jsonify(error="Image not found"), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
