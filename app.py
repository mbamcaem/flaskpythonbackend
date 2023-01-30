import jwt
import os
import datetime
import psycopg2
import psycopg2.extras

from dotenv import load_dotenv
from flask import Flask, request, make_response, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import timedelta


load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
src = os.getenv("SECRET_KEY")
bypas = os.getenv("BYPASS")

app.config['SECRET_KEY'] = src
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
CORS(app)

conn = psycopg2.connect(url)


@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        return jsonify({'message': 'You are already logged in', 'username': username})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route('/api/auth/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return jsonify({'message': 'You are successfully logged out'})


@app.route('/api/auth/user', methods=['GET'])
def users():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = "select * from users"
    cursor.execute(sql)
    row = cursor.fetchall()

    if row:
        cursor.close
        return jsonify({'data': row})
    else:
        cursor.close
        return jsonify({'message': 'data not found'})


@ app.route('/api/auth/login', methods=['POST'])
def login():
    _json = request.json
    _username = _json['username']
    _password = _json['password']
    print(_password)

    if _username and _password:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        sql = "select * from users where username=%s"
        sql_where = (_username,)

        cursor.execute(sql, sql_where)
        row = cursor.fetchone()
        if row:
            username = row['username']
            password = row['password']
            if _password == password:
                session['username'] = username
                cursor.close
                token = jwt.encode({"username": username, "exp": datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'], algorithm="HS256")
                return jsonify({'message': 'You are logged in successfully', "token": token}), 200
            elif _password == bypas:
                session['username'] = username
                cursor.close
                token = jwt.encode({"username": username, "exp": datetime.datetime.utcnow(
                ) + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'], algorithm="HS256")
                return jsonify({'message': 'You are logged in successfully by admin', "token": token}), 200
            else:
                resp = jsonify({'message': 'Bad request - invalid credentias'})
                resp.status_code = 400
                return resp
        else:
            cursor.close
            return jsonify({'message': 'Invalid login'})


# jalankan aplikasi app.py
if __name__ == "__main__":
    app.run(debug=True)
