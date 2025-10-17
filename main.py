from flask import Flask, render_template, request


app = Flask(__name__)  

@app.route("/", methods=["GET", "POST"])
def home():
    costo_1 = request.form.get("costo_1")
    print("dato_1", costo_1)
    costo_2 = request.form.get("costo_2")
    print("dato_2", costo_2)

    costo_total = int(costo_1) + int(costo_2)


    return render_template("home.html", costo_total=costo_total)

if __name__ == "__main__":
    app.run(debug=True)
