#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask
from flask import render_template, request, jsonify, make_response, Response, flash, redirect, session, url_for, g
from skeleton import config


app = Flask(__name__)
app.config.from_object(config)

@app.route('/index', methods=['GET'])
def welcome():	
	return render_template('index.html')


@app.route('/class/<class_id>')
def show_class(class_id):

	classShown = db.session.query(Class).filter_by(id=class_id).first()
	classLessons = db.session.query(Lesson).filter_by(class_id=class_id)


	return render_template('class.html', course=classShown, lessons=classLessons)

# Example of ajax route that returns JSON
@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)