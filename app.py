from flask import Flask, render_template
from flask_login import login_required

from config import Config
from extensions import (
    bcrypt,
    csrf,
    db,
    limiter,
    login_manager,
    mail,
    migrate,
    oauth,
)
from models import User
from routes.auth import auth
from routes.prediction import prediction

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = ''
mail.init_app(app)
bcrypt.init_app(app)
migrate.init_app(app, db)
csrf.init_app(app)
limiter.init_app(app)
oauth.init_app(app)

oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Register blueprints
app.register_blueprint(auth)
app.register_blueprint(prediction)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)