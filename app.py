from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html', name=name)

@app.route('/login')
def login():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html', name=name)

@app.route('/register')
def register():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html', name=name)

@app.route('/dashboard')
def dashboard():
    # Data to be passed to the template
    name = "Flask User"
    # Render the template and pass data to it
    return render_template('index.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
