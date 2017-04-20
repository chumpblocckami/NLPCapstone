from csv import DictReader
import codecs
from truncate_articles import trunc_articles

class DataSet():
    #path="/fnc_1_baseline_master/fnc-1"
    def __init__(self, path="/homes/iws/liliang/WindowsFolders/NLPCapstone/fnc_1_baseline_master/fnc-1"):
        self.path = path

        print("Reading dataset")
        bodies = "train_bodies.csv"
        stances = "train_stances.csv"

        self.stances = self.read(stances)
        articles = self.read(bodies)
	self.articles = dict()

        #make the body ID an integer value
        for s in self.stances:
            s['Body ID'] = int(s['Body ID'])

        # Use truncated articles instead
	trunc_art = trunc_articles()
	
	#copy all bodies into a dictionary
        for body_id, body in enumerate(trunc_art):
            #self.articles[int(article['Body ID'])] = article['articleBody']
	    self.articles[int(body_id)] = body

        print("Total stances: " + str(len(self.stances)))
        print("Total bodies: " + str(len(articles)))
        #print("Total trunc bodies: " + str(len(trunc_art)))


    def read(self,filename):
        rows = []
        with codecs.open(self.path + "/" + filename, "r") as table:
            r = DictReader(table)

            for line in r:
                rows.append(line)
        return rows

ds = DataSet()
