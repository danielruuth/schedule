#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify, render_template, url_for
app = Flask(__name__)
@app.route('/')
def index():
    data = {}
    data['title'] = 'Schemaläggare 3000'
    data['body'] = """<p>Här kommer schemat</p>"""

    # Render a template with the content of the data dictionary
    return render_template('index.html', data=data)
@app.route('/api/getschedule', methods=['POST'])
def generate_schedule():
    return jsonify({'action':'Generate schedule'})

app.run()
