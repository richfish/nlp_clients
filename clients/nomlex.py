# identify nominalizations and if present defer to the propbank structure

import re

class Nomlex():
    def __init__(self):
        self.nom_text = self.get_nom_text()
        self.raw_noms = self.get_raw_noms()
        self.nom_verb_pairs = self.get_nom_verb_pairs()

    def get_nom_text(self):
        with open("../assets/NOMLEX-2001.txt", 'r') as myfile:
            raw_txt = myfile.read()
        return raw_txt.replace("  ", "") # double space == large amounts whitespace

    def get_raw_noms(self):
        ret = self.nom_text.split("(NOM :ORTH")
        del ret[0]
        return [x.strip() for x in ret]

    def get_nom_verb_pairs(self):
        final = []
        pat_nom = re.compile("^\"([a-zA-Z\s]{2,20})\"")
        pat_verb = re.compile(":VERB\s?\"([a-zA-Z\s]{2,30})\"")
        for nom_set in self.raw_noms:
            noun = pat_nom.findall(nom_set)
            if noun:
                noun = noun[0]
            verb = pat_verb.findall(nom_set)
            if verb:
                verb = verb[0]
            final.append([noun, verb])
        return final
