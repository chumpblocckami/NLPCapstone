import pandas as pd
import numpy as np

def trunc_articles():
	df = pd.read_csv("fnc_1_baseline_master/fnc-1/train_bodies.csv")
	articles = df["articleBody"]
	id_article_dict = {}
	id_length_dict = {}
	for i, article in enumerate(articles):
		words = article.split()
		length = -1
		if len(words) > 200:
			words = words[:200]
			length = 200
		else:
			length = len(words)
			padding_length = 200 - len(words)
			for j in range(padding_length):
				words.append(' ') # special padding symbol (a space should not have a word embedding) 
		id_article_dict[df["Body ID"][i]] = words
		id_length_dict[df['Body ID'][i]] = length
	return id_article_dict, id_length_dict  # might want to add in a return for the original length of the sentence here too
			
