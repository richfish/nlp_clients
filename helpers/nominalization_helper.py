from clients.nomlex import Nomlex

class NominalizationHelper():
    def __init__(self):
        self.nl = Nomlex()

    def is_nominalization(self, nom_word):
        finds = filter(lambda x: x[0] == nom_word, self.nl.nom_verb_pairs)
        if finds:
            return True
        else:
            return False

    def get_verb_for_nom(self, nom_word):
        finds = filter(lambda x: x[0] == nom_word, self.nl.nom_verb_pairs)
        return finds[0][1]

    def get_nom_for_verb(self, verb_word):
        finds = filter(lambda x: x[1] == verb_word, self.nl.nom_verb_pairs)
        return finds[0][0]
