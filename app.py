import random
import hashlib
import json
from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests

class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.string = self.stringify(value, suit)
        self.halfsuit = (self.suit, self.value < 8)

    def same_halfsuit_as(self, card):
        return self.halfsuit == card.halfsuit

    def equals(self, card):
        return self.value == card.value and self.suit == card.suit

    @staticmethod
    def stringify(value, suit):
        out = ""
        if value == 1:
            out += "Ace"
        elif value < 11:
            out += str(value)
        elif value == 11:
            out += "Jack"
        elif value == 12:
            out += "Queen"
        elif value == 13:
            out += "King"
        out += " of "
        if suit == 0:
            out += "Clubs"
        elif suit == 1:
            out += "Diamonds"
        elif suit == 2:
            out += "Hearts"
        elif suit == 3:
            out += "Spades"
        return out
        
class Deck(object):
    def __init__(self):
        values = [i+1 for i in range(13)]
        suits = [0, 1, 2, 3]
        self.cards = [Card(a,b) for a in values for b in suits]

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    def contains(self, card):
        for deck_card in self.cards:
            if card.equals(deck_card):
                return True
        return False

    def replace(self, card):
        if not self.contains(card):
            self.cards.append(card)

class Player(object):
    def __init__(self, id):
        self.hand = []
        self.id = id
        self.team = id % 2
        self.name = str(id)
        self.ip = ""

    def halfsuits(self):
        return set(card.halfsuit for card in self.hand)

    def in_hand(self, card):
        for held_card in self.hand:
            if card.equals(held_card):
                return held_card
        return False

    def take_card(self, card):
        held_card = self.in_hand(card)
        if held_card:
            self.hand.remove(held_card)
            return held_card
        return False

    def give_card(self, card):
        if not self.in_hand(card):
            self.hand.append(card)
            return True
        return False


class Game(object):
    def __init__(self):
        self.deck = Deck()
        bad_cards = []
        for card in self.deck.cards:
            if card.value == 8:
                bad_cards.append(card)
        for card in bad_cards:
            self.deck.cards.remove(card)
        self.deck.shuffle()
        
        self.players = [Player(id) for id in range(6)]
        self.players_by_ip = {}
        count = 0
        while count < 48:
            self.players[count % 6].give_card(self.deck.draw())
            count += 1

        self.active_player = self.players[0]
        self.declaring = False
        self.declaring_halfsuit = False
        self.halfsuits_in_play = set(card.halfsuit for card in self.deck.cards)

    def valid_query(self, card):
        return card.halfsuit in self.active_player.halfsuits()

    def query(self, id, card):
        if self.valid_query(self.players[id], card):
            card_in_hand = self.players[id].take(card)
            if card_in_hand:
                self.active_player.give(card_in_hand)
                return 1
            else:
                self.active_player = self.players[id]
                return 0
        return -1

    def declaration_query(self, id, card):
        if self.declaring and self.declaring.id % 2 == id % 2 and self.declaring_halfsuit == card.halfsuit:
                return self.players[id].take_card(card)
        return -1

    def begin_declaration(self, id, halfsuit):
        if halfsuit in self.halfsuits_in_play:
            self.halfsuits.remove(halfsuit)
            self.declaring = self.players[id]
            self.declaring_halfsuit = halfsuit
            return 1
        return -1

    def end_declaration(self):
        removed_cards = []
        if self.declaring:
            for player in self.players:
                current_hand = [card for card in player.hand]
                for card in current_hand:
                    if card in self.declaring_halfsuit:
                        removed_cards += player.take_card(card)
            return removed_cards
        return -1

app = Flask(__name__)
game = Game()

@app.route('/')
def homepage():
    return """
    <h1>Hello!</h1>
    <p>This is a test because Heroku is hot garbage.</p>
    """

@app.route('/join', methods=['POST'])
def add_user():
    remote_ip = request.environ['REMOTE_ADDR']
    values = request.get_json()
    if 'name' not in values:
        return 'Missing values', 400

    for player in game.players:
        if player.ip == remote_ip:
            return 'Duplicate player', 400
        if not player.ip:
            player.ip = remote_ip
            player.name = values['name']
            game.players_by_ip[remote_ip] = player
    response = {'message': 'Player ' + values['name'] + ' added to the game.'}
    return jsonify(response), 201

@app.route('/hand', methods=['GET'])
def get_hand():
    remote_ip = request.environ['REMOTE_ADDR']
    player = game.players_by_ip[remote_ip]
    hand = player.hand
    response = {
            'hand_suits' : [card.suit for card in hand],
            'hand_values' : [card.value for card in hand],
            'name' : player.name
    }
    return jsonify(response), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
