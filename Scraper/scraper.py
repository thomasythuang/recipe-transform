#!/usr/bin/python

import sys, requests, json, nltk, re, string, pprint
from lxml import html
from itertools import groupby
from fractions import Fraction

# nltk.download()


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

url = sys.argv[1]

def scrape_recipe(url):
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
			print tokens
			for value, tag in tokens:
				if re.search("VB(?!G)", tag) != None:
					prep.append(value)
				elif tag == "RB":
					prepDesc.append(value)
				elif tag == "JJ" or tag == "VBG" or re.search("NN\w?", tag) != None or tag == "-NONE-":
					desc.append(value)
				#end if
			#end for

			ingredient["name"] = desc.pop(len(desc) - 1)
			ingredient["descriptor"] = " ".join(desc) if len(desc) > 0 else "none"
			ingredient["preparation"] = " ".join(prep) if len(prep) > 0 else "none"
			ingredient["prep-description"] = " ".join(prepDesc) if len(prepDesc) > 0 else "none"
		#end if

		if len(current) > 0:
			delimited = current[0].split(" ")
			ingredient["quantity"] = float(sum(Fraction(s) for s in delimited.pop(0).split()))
			ingredient["measurement"] = " ".join(delimited) if len(delimited) > 0 else "none"
		#end if
		
		if hasattr(ingredient, "name"):
			ingredients.append(ingredient)
	#end for

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
		#end try
		try:
			if TOOLS.index(token):
				tools.append(token)
		except Exception:
			pass
		#end try
	#end for

	frequencies = [len(list(group)) for key, group in groupby(sorted(methods))]
	methods = sorted(list(set(methods)))
	tools = list(set(tools))

	data = {
		"ingredients": ingredients,
		"primary cooking method": methods.pop(frequencies.index(max(frequencies))),
		"cooking methods": methods,
		"cooking tools": tools,
		"url": url,
	}


	data_string = json.dumps(data)
	return data

	
print scrape_recipe(url)

