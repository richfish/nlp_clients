from clients.propbank import PropbankMiner

class PropbankHelper():
    def __init__(self):
        self.pbm = PropbankMiner()
        self.all_rolesets = self.pbm.all_rolesets

    def get_roleset_per_word_general_match(self, word, pos=None):
        candidate_rs = []
        word = word.lower()
        if pos:
            pos = pos.lower()
        for roleset in self.all_rolesets:
            # note, could be more exact with lemma on per roleset basis
            r_name = roleset['meta']['name'] # str
            r_pos = roleset['meta']['pos'] # arr
            is_pos = True
            if pos:
                is_pos = pos in r_pos
            alias_txt = " ".join([x.replace("_", "") for x in roleset['meta']['alias_txts']])
            if word in alias_txt or word in r_name:
                 candidate_rs.append(roleset)
        return candidate_rs

    def get_roleset_per_word_exact_match(self, word, pos=None):
        candidate_rs = []
        word = word.lower()
        if pos:
            pos = pos.lower()
        for roleset in self.all_rolesets:
            # note, could be more exact with lemma on per roleset basis
            #r_name = roleset['meta']['name'] # str
            r_pos = roleset['meta']['pos'] # arr
            is_pos = True
            if pos:
                is_pos = pos in r_pos
            alias_list = [x.replace("_", "") for x in roleset['meta']['alias_txts']]
            if word in alias_list and is_pos:
                 candidate_rs.append(roleset)
        return candidate_rs

    def get_01_roles_for_word_exact_match(self, word, pos=None):
        roles_01 = []
        rolesets_per_word = self.get_roleset_per_word_exact_match(word)
        for roleset in rolesets_per_word:
            name_id = roleset['meta']['lemma'] + "; " + "-".join(roleset['meta']['pos']) + "; " + roleset['meta']['name'] + "; " + " ".join([x.replace("_", "") for x in roleset['meta']['alias_txts']])
            roles = filter(lambda x: x[0] in ['0','1'], roleset['roles'])
            roles_01.append([name_id, roles])
        return roles_01
