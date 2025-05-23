from flask import Flask, redirect, url_for
from routes import main_routes

app = Flask(__name__)
app.register_blueprint(main_routes)

@app.route('/')
def home():
    return redirect(url_for('main_routes.projects'))

if __name__ == '__main__':
    app.run(debug=True)