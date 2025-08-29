from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Server running - v0.1"

if __name__ == '__main__':
    app.run(debug=True)
