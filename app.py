import random
import hashlib
import json
from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests
import fish

app = Flask(__name__)
game = fish.Game()
game_id = str(random.getrandbits(64))

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

app.after_request(add_cors_headers)

@app.route('/')
def homepage():
    return """
    <h1>Hello!</h1>
    <p>This is a test because Heroku is hot garbage.</p>
    """

@app.route('/join', methods=['POST'])
def add_user():
    remote_uuid = str(random.getrandbits(64))
    print("Join request by " + remote_uuid)
    values = request.get_json()
    if 'name' not in values:
        return 'Missing values', 400

    for player in game.players:
        if player.uuid == remote_uuid:
            return 'Duplicate player', 400
        if not player.uuid:
            player.uuid = remote_uuid
            player.name = values['name']
            game.players_by_uuid[remote_uuid] = player
            break
    response = {
            'message': 'Player ' + values['name'] + ' added to the game.',
            'player_id': remote_uuid
    }
    return jsonify(response), 201

@app.route('/hand', methods=['POST'])
def get_hand():
    values = request.get_json()
    if 'player_id' not in values:
        return 'Missing values', 400
    remote_uuid = values['player_id']
    print("Hand request by " + remote_uuid)
    print("Game: " + game_id)
    print([key for key in game.players_by_uuid])
    player = game.players_by_uuid[remote_uuid]
    hand = player.hand
    response = {
            'hand' : [card.string for card in hand],
            'name' : player.name,
            'player_id': remote_uuid
    }
    return jsonify(response), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
