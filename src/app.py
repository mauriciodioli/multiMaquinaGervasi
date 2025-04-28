from src import create_app

from flask import Blueprint, render_template

app = create_app()

@app.route("/index/")
def index():
   return render_template("index.html")


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000, debug=True)
