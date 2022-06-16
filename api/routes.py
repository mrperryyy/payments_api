from api import app

@app.route('/index')
def index():
    return "Hello, World!"