from flask import Flask, jsonify, render_template, request
from src.helper import Chat_With_Sql
import os

app = Flask(__name__)
db_user = os.getenv("DB_USER") 
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

# making object of class and passing the arguments
obj = Chat_With_Sql(db_user,db_password,db_host, db_name) 


@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    output = obj.message(msg)
    return str(output)


if __name__ == '__main__':
    app.run(debug=True)