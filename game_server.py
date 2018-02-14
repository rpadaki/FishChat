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
        return self.halfsuit = card.halfsuit

    def equals(self, card):
        return self.value == card.value and self.suit == card.suit

    def value(self):
        return self.value

    def suit(self):
        return self.suit

    def string(self):
        return self.string

    def halfsuit(self):
        return self.halfsuit
    
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
        self.cards = [Card(a,b) for a in self.values for b in self.suits]

    def cards(self):
        return self.cards
    
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

    def hand(self):
        return self.hand

    def id(self):
        return self.id

    def team(self):
        return self.team

    def name(self):
        return self.name

    def ip(self):
        return self.ip

    def halfsuits(self):
        return set(card.halfsuit() for card in self.hand)

    def set_name(self, name):
        self.name = name

    def set_ip(self, ip):
        self.ip = ip

    def in_hand(self, card):
        for held_card in self.hard:
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
    def __init__(self, id):
        self.deck = Deck()
        bad_cards = []
        for card in self.deck.cards():
            if card.value() == 8:
                bad_cards.append(card)
        for card in bad_cards:
            self.deck.cards().remove(card)
        self.deck.shuffle()
        
        self.players = [Player(id) for id in range(6)]
        self.players_by_ip = {}
        count = 0
        while len(self.deck):
            self.players[count % 6].give(self.deck.draw())
            count += 1

        self.active_player = players[0]
        self.declaring = False
        self.declaring_halfsuit = False
        self.halfsuits_in_play = set(card.halfsuit() for card in self.deck)

    def deck(self):
        return self.deck

    def players(self):
        return self.players

    def player(self, id):
        return self.players[id]

    def active_player(self):
        return self.active_player

    def declaring(self):
        return self.declaring

    def declaring_halfsuit(self):
        return self.declaring_halfsuit

    def valid_query(self, card):
        return card.halfsuit() in self.active_player.halfsuits()

    def halfsuits_in_play(self):
        return self.halfsuits_in_play

    def players_by_ip(self):
        return self.players_by_ip

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
        if self.declaring and self.declaring.id() % 2 == id % 2 and self.declaring_halfsuit == card.halfsuit():
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
                current_hand = [card for card in player.hand()]
                for card in current_hand:
                    if card in self.declaring_halfsuit:
                        removed_cards += player.take_card(card)
            return removed_cards
        return -1

app = Flask(__name__)
game = Game()

@app.route('/join', methods=['POST'])
def add_user():
    remote_ip = request.environ['REMOTE_ADDR']
    values = request.get_json()
    if 'name' not in values:
        return 'Missing values', 400

    for player in game.players():
        if player.ip == remote_ip:
            return 'Duplicate player', 400
        if not player.ip:
            player.set_ip(remote_ip)
            player.set_name(values['name'])
            game.players_by_ip()[remote_ip] = player
    response = {'message': 'Player ' + values['name'] + ' added to the game.'}
    return jsonify(response), 201

@app.route('/hand', methods=['GET'])
def get_hand():
    remote_ip = request.environ['REMOTE_ADDR']
    response = {
            'hand' : game.players_by_ip()[remote_ip].hand()
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)