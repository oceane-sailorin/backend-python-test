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
from flask_paginate import Pagination, get_page_args
from .models import Users, Todos
from . import db
from sqlalchemy import inspect

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

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

    user = Users.query.filter_by(username = username, password = password).first()   
    if user:
        session['user'] = object_as_dict(user)
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
 
    todo = Todos.query.filter_by(id=id, user_id = session['user']['id']).first()   
    if todo: 
        return render_template('todo.html', todo=todo)
    else:
        flash('unknown id')
        return redirect('/todo')  
   


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')

    total = Todos.query.count()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')

    todos = Todos.query.filter_by(user_id = session['user']['id']).limit(per_page).offset(offset).all()

    pagination = Pagination(page=page, per_page=per_page, total=total,record_name='todos',
                            css_framework='bootstrap3')
    return render_template('todos.html', todos=todos,
                           page=page,
                           per_page=per_page,
                           pagination=pagination)


@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    elif(not (request.form.get('description')) or request.form.get('description').isspace()): 
        flash('Please enter a description')
        return redirect('/todo')

    try:
        todo = Todos(session['user']['id'],request.form.get('description', ''),0) 
        db.session.add(todo)    
        db.session.commit()
        flash('Todo inserted')

    except Exception as e:
        flash('Todo not inserted')     

    return redirect('/todo')


@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    try:   
        todo = Todos.query.filter_by(id=id, user_id = session['user']['id']).first()
        db.session.delete(todo)
        db.session.commit()
        flash('Todo deleted')

    except Exception as e:
        flash('Todo not deleted')     

    return redirect('/todo')

@app.route('/todo/<id>/completed', methods=['POST'])
def todo_completed(id):   
    if not session.get('logged_in'):
        return redirect('/login')

    try: 
        todo = Todos.query.filter_by(id = id, user_id = session['user']['id']).first()   
        if request.form.get('completed'):
            todo.completed = 1
            db.session.commit()
            flash('Task completed')
        else:
            todo.completed = 0
            db.session.commit()
            flash('Task not completed')

    except Exception as e:
        flash('Todo not updated')   

    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = Todos.query.filter_by(id = id, user_id =session['user']['id']).first()   
    if todo:    
        json_data=object_as_dict(todo)
        return jsonify(json_data)
    else:
        flash('unknown id')
        return redirect('/todo')  
