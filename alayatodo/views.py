from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify
    )


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '{}' AND password = '{}'";
    cur = g.db.execute(sql.format(username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos WHERE id ={} and user_id={}".format(id,session['user']['id']))
    todo = cur.fetchone()
    if todo:
        return render_template('todo.html', todo=todo)
    return redirect('/todo')


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos where user_id={} ".format(session['user']['id']))
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    elif(not (request.form.get('description')) or request.form.get('description').isspace()): 
        flash('Please enter a description')
        return redirect('/todo')    
    g.db.execute(
        "INSERT INTO todos (user_id, description) VALUES ({}, '{}')".format(session['user']['id'],request.form.get('description', ''))     
    )
    g.db.commit()
    flash('Todo inserted')
    return redirect('/todo')

@app.route('/todo/<id>/completed', methods=['POST'])
def todo_completed(id):   
    if not session.get('logged_in'):
        return redirect('/login')
    if request.form.get('completed'):
        g.db.execute("UPDATE todos set completed=1 WHERE id = {} and user_id={}".format(id, session['user']['id']))
        flash('Task completed')
    else:
        g.db.execute("UPDATE todos set completed=0 WHERE id = {} and user_id={}".format(id, session['user']['id']))
        flash('Task not completed')
    g.db.commit()
    return redirect('/todo')

@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id = {} and user_id={}".format(id, session['user']['id']))
    g.db.commit()
    flash('Todo deleted')
    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    cur = g.db.execute("SELECT * FROM todos WHERE id ={} and user_id={}".format(id, session['user']['id']))
    todo = cur.fetchone()
    if todo:
        json_data=dict(todo)
        return jsonify(json_data)
    return redirect('/todo')
