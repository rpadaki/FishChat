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
        self.values = [i+1 for i in range(13)]
        self.suits = [0, 1, 2, 3]
        self.cards = [Card(a,b) for a in self.values for b in self.suits]
    
    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    def replace(self, card):
        if card not in self.cards:
            self.cards.append(card)

class Player(object):
    def __init__(self, id, name=str(id)):
        self.hand = []
        self.id = id
        self.team = id % 2
        self.name = name

    def halfsuits(self):
        return set(card.halfsuit for card in self.hand)

    def in_hand(self, card):
        for held_card in self.hard:
            if card.equals(held_card):
                return card
        return False


class Game(object):
    def __init__(self, id):
        self.deck = Deck()
        bad_cards = []
        for card in self.deck.cards:
            if card.value == 8:
                bad_cards.append(card)
        for card in bad_cards:
            self.deck.cards.remove(card)
        self.deck.shuffle()

        self.players = [Player(id, str(id)) for id in range(6)]
        self.active_player = players[0]

    def valid_query(self, card):
        return card.halfsuit in self.active_player.halfsuits()

    def query(self, player, card):
        if self.valid_query(player, card):
            card_in_hand = player.in_hand(card)
            if card_in_hand:
                player.hand.remove(card_in_hand)
                self.active_player.hand.append(card_in_hand)
                return 1
            self.active_player = player
            return 0
        return 2

    #def declare(self, halfsuit):
