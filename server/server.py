#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, jsonify, render_template, url_for, request
from modules.scheduler import Scheduler
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
@app.route('/')
def index():
    data = {}
    data['title'] = 'Schemaläggare 3000'
    data['body'] = """<p>Här kommer schemat</p>"""

    # Render a template with the content of the data dictionary
    return render_template('index.html', data=data)
@app.route('/api/getschedule', methods=['POST'])
def generate_schedule():
    
# {
# 	"resources": ["Jim", "Pam", "Dwight", "Stan", "Creed", "Andy", "Michael", "Phyllis"],
# 	"shifts": ["O", "A", "C"],
#   "weeks": 3,
#   "fixed_assignments": [
#             [0, 0, 0],
#             [1, 0, 0],
#             [2, 1, 0],
#             [3, 1, 0],
#             [4, 2, 0],
#             [5, 2, 0],
#             [6, 2, 3],
#             [0, 1, 1],
#             [1, 1, 1],
#             [2, 2, 1],
#             [3, 2, 1],
#             [4, 2, 1],
#             [5, 0, 1],
#             [6, 0, 1]
#  	],
#   "requests": [
#             [3, 0, 5, -2],
#             [5, 2, 10, -2],
#             [2, 2, 4, 4]
#         ],
# 	"shift_constraints":  [
# 			[0, 1, 1, 0, 2, 2, 0]
# 	],

# 	"cover_demands": [
# 			[3, 3],
# 			[3, 3],
# 			[3, 3],
# 			[3, 3],
# 			[3, 3],
# 			[2, 2],
# 			[2, 2]
# 	]
# }

    post_data = request.get_json(force=True)
    print(post_data)

    post_params = {
        'resources': post_data['resources'],
        'shifts': post_data['shifts'],
        'weeks': post_data['weeks'],
        'fixed_assignments': [tuple(sub_array) for sub_array in post_data['fixed_assignments']],
        'requests': [tuple(sub_array) for sub_array in post_data['requests']],
        'shift_constraints':  [tuple(sub_array) for sub_array in post_data['shift_constraints']],
        'cover_demands': [tuple(sub_array) for sub_array in post_data['cover_demands']],
        'penalized_transitions': [tuple(sub_array) for sub_array in post_data['penalized_transitions']]
    }

    print(post_params)
    
        
    s = Scheduler(post_params)
    solution = s.solve()
    return solution

app.run(host='0.0.0.0')
