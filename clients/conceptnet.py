import re
import pandas as pd

class Conceptnet():

    def __init__(self):
        cpath = "../assets/conceptnet/final/"
        self.good_df = pd.read_csv(cpath + "final.csv")
        self.good_concepts = self.good_df.main.tolist()
        #self.concepts_with_srl_vtags = pd.read_csv(cpath + "with_vtags.csv").main.tolist()

    def get_candidates(self):
        # example script for candidate concepts
        filters = ["DefinedAs", "/d/wordnet", "AtLocation", "Antonym", "InstanceOf", "DerivedFrom", "/r/dbpedia",
                    "r/TranslationOf", "r/IsA", "r/Synonym", "r/RelatedTo"]

        df = pd.read_csv("../assets/conceptnet/part_07.csv", sep="\n")
        l = df.values.tolist()
        f = filter(lambda x: "/c/en" in x[0], l)
        better = []
        for term in f:
            ret = filter(lambda x: x in term[0], filters)
            if not ret:
                better.append(term)
        f = better
        df = pd.DataFrame(data={'entry': f})
        df.to_csv("../assets/conceptnet/final/set8.csv")
