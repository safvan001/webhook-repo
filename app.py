from flask import json 
from flask import request
from flask import Flask
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app=Flask(__name__)


client = MongoClient('mongodb://localhost:27017/')
db = client['webhook_db']
collection = db['events']




@app.route('/github', methods=['POST'])
def webhook():
    data = request.json

    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'push':
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = datetime.now()

        event = {
            'type': 'PUSH',
            'author': author,
            'to_branch': to_branch,
            'timestamp': timestamp
        }

    elif event_type == 'pull_request':
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.now()

        event = {
            'type': 'PULL_REQUEST',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }

    elif event_type == 'merge':
        
        author = data['sender']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.now()

        event = {
            'type': 'MERGE',
            'author': author,
            'from_branch': from_branch,
            'to_branch': to_branch,
            'timestamp': timestamp
        }

    collection.insert_one(event)
    
    return jsonify({'status': 'success'}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find().sort('timestamp', -1).limit(10))
    formatted_events = []
    
    for event in events:
        event['_id'] = str(event['_id'])
        
        if 'timestamp' in event and isinstance(event['timestamp'], datetime):
            event['timestamp'] = event['timestamp'].strftime('%d %B %Y - %I:%M %p UTC')
        
        formatted_events.append(event)
    
    return jsonify(formatted_events)

@app.route('/')
def index():
    return render_template('base.html')

if __name__ == '__main__':
    app.run(debug=True)