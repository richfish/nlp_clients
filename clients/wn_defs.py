import nltk
from nltk.corpus import wordnet as wn
from spacy_helper import SpacyHelper

class WnDefs():
    def __init__(self):
        self.spacyh = SpachyHelper()
        self.defs_raw = [x.definition() for x in wn.all_synsets()] #117,659
        self.defs_good_length = self.get_defs_of_good_length()#
        self.defs_better = self.unformat_defs() #deal with .e.g and ;
        self.x_rel_empty_subj_keys = [] #self.convert_to_empty_subj_x_rel_keys()
        self.x_rel_guessed_subj_keys = [] #self.convert_to_x_rel_keys_guessing_subj(slices)

    def get_defs_of_good_length(self):
        defs = []
        for d in self.defs_raw:
            if len(d) < 50:
                #words = nltk.word_tokenize(d)
                #if len(words) > 3
                if len(d) > 16:
                    defs.append(d)
        return defs

    def unformat_defs(self):
        defs = []
        for d in self.defs_good_length:
            if ";" in d:
                splits = d.split(";")
                defs.append(splits[0].strip())
                defs.append(splits[1].strip())
                continue
            if "e.g." in d:
                splits = d.split("e.g.")
                defs.append(splits[0].strip())
                defs.append(splits[1].strip())
                continue
            defs.append(d)
        return filter(None, defs) #ommit empty str

    def convert_to_empty_subj_x_rel_keys(self):
        keys = []
        for d in self.defs_better:
            keys.append("<X [subj] ><rel {} >".format(d))
        self.x_rel_empty_subj_keys = keys
        return keys

    def convert_to_x_rel_keys_guessing_subj(self, sent_slices=None):
        keys = []
        if not sent_slices:
            sent_slices = self.defs_better
        for d in sent_slices:
            parsedd = self.spacyh.parse(d)
            head_word = self.spacyh.determine_head_from_phrase(parsedd)
            if not head_word: #will return False if broke
                continue
            wtype = self.spacyh.similarity_score_type(head_word[0])
            keys.append("<X **{}><rel {}>".format(wtype, d)) #** to indicate guess
        # if the rel is like, (of books) having a flexible binding --> could use (of books) as key
        self.x_rel_guessed_subj_keys = keys
        return keys
