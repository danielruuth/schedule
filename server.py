#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify
app = Flask(__name__)
@app.route('/')
def index():
    return jsonify({'action': 'Create schedule'})
@app.route('/', methods=['POST'])
def generate_schedule():
    return jsonify({'action':'Generate schedule'})

app.run()
