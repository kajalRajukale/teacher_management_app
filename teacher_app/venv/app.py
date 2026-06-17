from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Teacher Attendance App</h1>
    <p>App Running Successfully</p>
    """

if __name__ == "__main__":
    app.run(debug=True)