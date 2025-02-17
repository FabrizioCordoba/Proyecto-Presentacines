from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def formulario():
    return render_template("formulario.html")

@app.route("/submit", methods=["POST"])
def submit_form():
    apellidos = request.form["apellidos"]
    nombres = request.form["nombres"]
    dni = request.form["dni"]
    email = request.form["email"]
    return f"Datos recibidos: {apellidos}, {nombres}, {dni}, {email}"

if __name__ == "__main__":
    app.run(debug=True)
