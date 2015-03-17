#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask
from flask import render_template, request, jsonify, make_response, Response, flash, redirect, session, url_for, g
from flask.ext.pymongo import PyMongo
from skeleton import config
import os, json, sys, requests, nltk, re, string, time, random
from lxml import html
from itertools import groupby
from fractions import Fraction
from bson import BSON
from bson import json_util

app = Flask(__name__)
app.config.from_object(config)

mongo = PyMongo(app)

COMMANDS = [
	"bake", "baste", "batter", "beat", "blend", "boil", "braise", "break", "broil", "brush", "burn",
	"carve", "chill", "chop", "crack", "cook", "cool", "cut",
	"debone", "dice", "drain", "dress",
	"fillet", "flour", "fold", "freeze", "fry",
	"garnish", "glaze", "grate", "grind", "grill", "gut",
	"heat",
	"knead",
	"macerate", "mash", "melt", "mince", "mix",
	"parboil", "peel", "pickle", "poach", "pour", "prepare",
	"refrigerate", "remove", "rinse", "roast", "roll", "roll", "rub",
	"salt", "saute", "scoop", "scorch", "season", "simmer", "skim", "slice", "soak", "spice", "spread", "sprinkle", "squeeze", "steam", "stir", "strain", "sugar", "sweeten",
	"thaw", "thicken", "toast",
	"warm", "wash", "whip", "whisk", "wipe"
]

TOOLS = [
	"bag", "baller", "baster", "blender", "blowtorch", "board", "bowl", "brush",
	"cheesecloth", "chinoise", "chopper", "cleaver", "colander", "corer", "corkscrew", "cracker", "cutter", "cup",
	"fork", "funnel",
	"glove", "grater", "grinder", "guard",
	"holder",
	"knife",
	"ladle", "lame",
	"mandoline", "masher", "measuring", "mezzaluna", "mill", "minder", "mortar",
	"needle", "nutcracker",
	"opener", "oven",
	"peeler", "pestle", "pick", "piercer", "pin", "pitter", "poacher", "pot", "press",
	"reamer", "ricer", "rolling",
	"saucepan", "scale", "scaler", "scissors", "scoop", "scraper", "separator", "server", "shaker", "shears", "sieve", "sifter", "skillet", "slicer", "spatula", "spider", "spoon", "squeezer", "stainer",
	"tamis", "tenderizer", "thermometer", "timer", "tongs", "torch", "tray", "twine",
	"whisk",
	"zester"
]

@app.route('/index', methods=['GET'])
def welcome():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "static", "kb.json")
	with open(json_url) as json_file:
	    json_data = json.load(json_file)

	return render_template('index.html')


@app.route('/store_recipe', methods=['POST'])
def store_recipe():


	#url = request.form['recipe_url']
	data = json.loads(request.data.decode('utf8'))
	url = data['recipe_url']
	print url

	page = requests.get(url)
tree = html.fromstring(page.text)

ingredientInfo = [];
listItems = tree.xpath("//li[@id='liIngredient']");
for listItem in listItems:
	ingredientInfo.append(listItem.xpath("./label/p/span/text()"))
directions = " ".join(tree.xpath("//span[@class='plaincharacterwrap break']/text()"))

ingredients = []
length = len(ingredientInfo)

for i in range(0, length):
	ingredient = {}

	current = ingredientInfo[i]
	name = current.pop(len(current) - 1)
	tokens = nltk.pos_tag(nltk.word_tokenize(name.replace(",", "")))
	numTokens = len(tokens)
	desc = []
	prep = []
	prepDesc = []
	if len(tokens) > 0:
		for value, tag in tokens:
			if re.search("VB(?!G)", tag) != None:
				prep.append(value)
			elif tag == "RB":
				prepDesc.append(value)
			elif tag == "JJ" or tag == "VBG" or re.search("NN\w?", tag) != None or tag == "-NONE-":
				desc.append(value)
		ingredient["name"] = desc.pop(len(desc) - 1)
		ingredient["descriptor"] = " ".join(desc) if len(desc) > 0 else "none"
		ingredient["preparation"] = " ".join(prep) if len(prep) > 0 else "none"
		ingredient["prep-description"] = " ".join(prepDesc) if len(prepDesc) > 0 else "none"

	if len(current) > 0:
		delimited = current[0].split(" ")
		ingredient["quantity"] = float(sum(Fraction(s) for s in delimited.pop(0).split()))
		ingredient["measurement"] = " ".join(delimited) if len(delimited) > 0 else "none"

	ingredients.append(ingredient)

	methods = []
	tools = []
	exclude = set(string.punctuation)
	directions = directions.replace("-", " ")
	directions = "".join(char for char in directions if char not in exclude)
	tokens = nltk.word_tokenize(directions)
	for token in tokens:
		token = token.lower()
		try:
			if COMMANDS.index(token):
				methods.append(token)
		except Exception:
			pass
		try:
			if TOOLS.index(token):
				tools.append(token)
		except Exception:
			pass

	frequencies = [len(list(group)) for key, group in groupby(sorted(methods))]
	methods = sorted(list(set(methods)))
	tools = list(set(tools))

	data = {
		"ingredients": ingredients,
		"primary cooking method": methods.pop(frequencies.index(max(frequencies))),
		"cooking method": methods,
		"cooking tools": tools,
		"url": url,
		"time": int(time.time())
	}

	data_string = json.dumps(data)
	new_recipe_id = mongo.db.recipes.insert(data)
	return data_string


@app.route('/transform_recipe', methods=['POST'])
def tranform_recipe():

	data = json.loads(request.data.decode('utf8'))
	url = data['recipe_url']
	transform = data['transform']
	#url = request.form['recipe_url']
	#transform = request.form['transform']

	recipe = mongo.db.recipes.find_one({"url": url})
	knowledge_base = load_knowledge_base()

	for ingredient_group in knowledge_base['ingredients']:
		for ingredient in knowledge_base['ingredients'][ingredient_group]:
			if ingredient['name'] in [x['name'] for x in recipe['ingredients']]:
				# the ingredient exists in our knowledge base!!
				print ingredient['name'] + " is a match!"
				# check if the ingredient has the boolean we are transforming too
				if ingredient.has_key(transform) and ingredient[transform] == False:
					# we need to change this ingredient!
					print "let's transform this"
					#loop through ingredient group, grab first one that matches
					new_ingredient_list = []
					old_ingredient = ingredient['name']
					for ingredient in knowledge_base['ingredients'][ingredient_group]:
						if ingredient[transform] == True:
							new_ingredient_list.append(ingredient['name'])

					if len(new_ingredient_list) > 0:
						new_ingredient = random.choice(new_ingredient_list)
						print " old ingredient %s" % old_ingredient

						# loop through recipe ingredients and update it 
						for recipe_ingredient in recipe['ingredients']:
							print recipe_ingredient['name']
							if recipe_ingredient['name'] == old_ingredient:
								recipe_ingredient['name'] = new_ingredient
								recipe_ingredient['descriptor'] = ""



	return json.dumps(recipe, sort_keys=True, indent=4, default=json_util.default)


def load_knowledge_base():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "static", "kb.json")
	with open(json_url) as json_file:
	    json_data = json.load(json_file)

	print "Number of proteins: %s" % str(len(json_data['ingredients']['proteins']))
	print "Number of fruits-veggies: %s" % str(len(json_data['ingredients']['fruits-veggies']))
	print "Number of oils: %s" % str(len(json_data['ingredients']['oils']))
	print "Number of grains: %s" % str(len(json_data['ingredients']['grains']))
	# print "Number of dairy: %s" % str(len(json_data['ingredients']['dairy']))
	
	return json_data


# Example of ajax route that returns JSON
@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)