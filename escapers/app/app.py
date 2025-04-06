from flask import Flask, url_for, render_template

app = Flask(__name__)

@app.route('/')
def index():
    css_url = url_for('static', filename='style.css')
    return render_template('index.html', css_url=css_url)

if __name__ == '__main__':
    app.run(debug=True)