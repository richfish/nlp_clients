from clients.verbnet import Verbnet

class VerbnetHelper():
    def __init__(self):
        vbn = Verbnet()
        self.vbn = vbn
        self.verbnets = vbn.all_templates
        self.words_by_class = vbn.all_words_per_group

    def return_verbnet_by_word(self, word):
        vns = []
        for i, wset in enumerate(self.words_by_class):
            wset_flat = [y for x in wset for y in x]
            if word in wset_flat:
                vns.append(self.verbnets[i])
        return vns

    def return_classes_by_word(self, word):
        classes = []
        for i, group in enumerate(self.words_by_class):
            for i2, class_set in enumerate(group):
                if word in class_set:
                    vn = self.verbnets[i]
                    klass = vn["class" + str(i2+1)]
                    classes.append(klass)
        return classes

    def return_all_constructions_for_word(self, word):
        constructions = []
        classes = self.return_classes_by_word(word)
        for klass in classes:
            for frame in klass['frames']:
                constructions.append(frame['construction'])
        return constructions
