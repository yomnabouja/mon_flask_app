from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        return f"<h2>Merci {name}, nous avons bien reçu ton message !</h2>"
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
