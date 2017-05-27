import re
from collections import defaultdict
import itertools
from pprint import pprint as pp
import json
import nltk
import pdb
import traceback
from nltk.stem.lancaster import LancasterStemmer
import pyPdf
# import spacy
# from spacy.en import English
# from spacy import attrs
# parser = English()


class OxCollocations():
    def __init__(self, pdf=None, current_page=None):
        if not pdf:
            pdf = pyPdf.PdfFileReader(open("../assets/oxford_collocations_dictionary.pdf", "rb"))
        self.pdf = pdf
        #self.set_header_regex = re.compile("[A-Z]{2}[A-Z\.\s\+]{1,26}") #QUANT. / ADJ. / CHAIN + NOUN etc.
        self.set_header_regex = re.compile("[A-Z]{1}[A-Z\.\s\+]{2,26}")

        self.all_coll_chunks = []
        self.skipped_multi_page = []
        self.total_skip_list = [578,706,2229,2655,3218,3502,3508,3633,3634,3657,3805,3980,4567,4581,4628,4623,4689,4836,5094,5266,
                                5481,5546,6079,6108,6908,6970,7140,7315,7541,7908,7979,8238,8471,8647,8902] #too annoying to work with
        self.exceptions_in_iter = []
        self.all_templates = []
        self.current_template = None

        if current_page in [222, None]:
            return None
        self.current_page = current_page

        self.first_entry = self.pdf.pages[self.current_page].extractText()
        self.base_word = self.get_base_word()
        self.base_word_pos = self.get_base_word_pos()
        self.base_word_with_pos = self.base_word + "_" + self.base_word_pos
        self.multi_page = self.determine_if_multi_page()
        self.num_pages_for_word = self.page_tracker()[1]

        self.text_entries = self.setup_and_concat_pages()
        self.text_entries_stripped = self.strip_text_entries()

        self.definitions0 = self.get_definitions() #can have problem with zero def collocations, but still want to keep def
        self.definitions = self.definitions0
        self.definition_chunks = self.split_into_definition_chunks() #all str below a definition

        self.sets_per_definition_chunk = self.get_all_sets_for_chunks()
        self.csets = self.sets_per_definition_chunk #testing
        self.base_template = self.return_template_with_head_and_definition_chunks()

        #self.example_sents = [] #todo, by definition chunks?
        self.collocation_by_def_chunks = self.get_collocations_per_definition_chunks()
        self.csets2 = self.collocation_by_def_chunks #testing

    legal_categories = ["ADJ", "VERB", "VERBS", "PHRASES", "QUANT", "ADV", "NOUN", "PREP"]

    def pp_template(self):
        pp(json.loads(json.dumps(self.base_template)))
        #pp(json.loads(json.dumps(t)))

    def get_base_word(self):
        leading = self.first_entry.split("OXFORD Collocations", 1)[0]
        pat = re.compile("^file.+\/(.+)_[a-z]+.htm")
        match = pat.findall(leading)[0]
        if self.current_page == 4746:
            match = "lead1"
        if self.current_page == 4748:
            match = "lead2"
        if self.current_page == 4750:
            match = "lead3"
        if self.current_page == 3495:
            match = "journalist"
        return match

    def get_base_word_pos(self):
        leading = self.first_entry.split("OXFORD Collocations", 1)[0]
        pat = re.compile("^file.+\/.+_([a-z]+).htm")
        match = pat.findall(leading)[0]
        if self.current_page == 4746:
            match = "noun"
        if self.current_page == 4748:
            match = "verb"
        if self.current_page == 4750:
            match = "noun"
        if self.current_page == 3495:
            match = "noun"
        return match

    def setup_and_concat_pages(self):
        text_entries = self.first_entry
        n = self.num_pages_for_word
        if n > 1:
            for i in range(1,n):
                text_entries = text_entries + self.pdf.pages[self.current_page+i].extractText()
        return text_entries

    def page_tracker(self):
        if not self.multi_page:
            return [1,1]
        footer = self.first_entry.split("file://")[-1]
        page_matcher = re.compile("\((\d) of (\d)\)")
        match = page_matcher.findall(footer)[0]
        return [int(match[0]), int(match[1])]

    def determine_if_multi_page(self):
        footer = self.first_entry.split("file://")[-1]
        page_matcher = re.compile("\(\d of \d\)")
        if page_matcher.findall(footer):
            return True
        else:
            return False

    def should_skip_because_multi_page(self):
        if self.multi_page:
            if self.page_tracker()[0] is not 1:
                return True
            else:
                return False
        else:
            return False

    def get_definitions(self):
        definition_chunk_pattern = re.compile("[^1-9][1-9]{1}\s([APMCDJa-z\s,\/\.:\(\);'?\-]{2,70}?)\s[A-Z]{3,30}")
        #definition_chunk_pattern2 = re.compile("[^1-9][1-9]{1}\s(\D{2,70}?)\s[1-9]{1}")
        #definition_chunk_pattern = re.compile("\s[1-9]\s(\D+?)\s[A-Z]{3,30}")
        #definition_chunk_pattern = re.compile("\s[1-9]\s(\D+?)")
        #removal_pat1 = re.compile("> Note at")
        #removal_pat2 = re.compile("> Note at [A-Z]{2,20}[\(a-z\s\)]{0,20}")
        if self.multi_page:
            if not self.should_skip_because_multi_page():
              self.current_page + self.num_pages_for_word #todo forgot where going here
        defs = definition_chunk_pattern.findall(self.text_entries_stripped)
        #raw_defs2 = definition_chunk_pattern2.findall(self.text_entries_stripped)

        #custom page filters because fucking Oxford typos
        if self.current_page in [483,2956,4278,5669,8746]:
            defs = []
        #if self.current_page == 472:
            #print(defs)
            #defs.remove('and ')
        if self.current_page == 1106:
            defs.remove('metres in breadth.')
        if self.current_page == 2841:
            defs.remove('million people.')
        if self.current_page == 3476:
            defs.remove('is an improper fraction, equivalent to one and three-eighths.')
        if self.current_page == 4288:
            defs.remove('points.')
        if self.current_page == 4647:
            defs.remove("is the shortcut key for calling up help.")
        if self.current_page == 5739:
            defs.remove('paper.')
        if self.current_page == 6100:
            defs.remove('hours.')
        if self.current_page == 6177:
            defs.remove("o'clock.")
        if self.current_page == 6392:
            defs.remove('billion.')
        if self.current_page == 6676:
            defs.remove('draw.')
        if self.current_page == 7680:
            defs.remove('has lined up a galaxy of stars for the coming season.')
        if self.current_page == 8033:
            defs.remove("p.m.")
        if self.current_page == 8490:
            defs.remove('billion.')

        return defs

    def return_template_with_head_and_definition_chunks(self):
        if self.definitions == []:
            return defaultdict(str, {
                self.base_word_with_pos: defaultdict(str, {
                    'base_word': self.base_word,
                    'pp': self.current_page,
                    "pos": self.base_word_pos,
                    'sets': defaultdict(str, {
                        1: defaultdict(str, {
                            'definition': 'SELF',
                            'set_cats': [],
                            'collocations': [], #[[NOUN, collocations... ], [VERB, collocations...]
                            'examples': []
                        })
                    })
                })
            })
        else:
            ret_dict = defaultdict(str)
            ret_dict[self.base_word_with_pos] = defaultdict(str)
            ret_dict[self.base_word_with_pos]['pp'] = self.current_page
            ret_dict[self.base_word_with_pos]['pos'] = self.base_word_pos
            ret_dict[self.base_word_with_pos]['base_word'] = self.base_word
            ret_dict[self.base_word_with_pos]['sets'] = defaultdict(str)
            for i, definition in enumerate(self.definitions):
                ret_dict[self.base_word_with_pos]['sets'][i+1] = defaultdict(str)
                ret_dict[self.base_word_with_pos]['sets'][i+1]['definition'] = definition
                ret_dict[self.base_word_with_pos]['sets'][i+1]['set_cats'] = []
                ret_dict[self.base_word_with_pos]['sets'][i+1]['collocations'] = []
                ret_dict[self.base_word_with_pos]['sets'][i+1]['examples'] = []
            return ret_dict

    def strip_text_entries(self):
        #Note,head removal mysteriously wont work in certain cases
        pat1 = re.compile("file:\/\/\/C\|\/TEMP\/htm\/OXFORD_PHRASEBUILDER_HTML\/files\/[_a-z]+\.htmOXFORD Collocations \| dictionary for students of English")
        pat2 = re.compile("file:\/\/\/C\|\/TEMP\/htm\/OXFORD_PHRASEBUILDER_HTML\/files\/[_a-z]+\.htm.{0,16}\[.{6,50}\]")
        pat3 = re.compile("file:\/\/\/C\|\/TEMP\/htm\/OXFORD_PHRASEBUILDER_HTML\/files\/[_a-z]+\.htm")
        pat4 = re.compile("> Note at SUBJECT\([a-z\s]{16,30}\)")
        pat5 = re.compile("> Note at [A-Z]{2,20}[\(a-z\s\)]{0,20}")
        pat6 = re.compile("> See [A-Z\s]{2,20}")
        pat7 = re.compile("> Special page at [A-Z\s]{2,20}")
        ret = re.sub(pat1, '', self.text_entries)
        ret = re.sub(pat2, '', ret)
        ret = re.sub(pat3, '', ret)
        ret = ret.replace('\n', '').strip()
        ret = re.sub(pat4, '', ret)
        ret = re.sub(pat5, '', ret)
        ret = re.sub(pat6, '', ret)
        ret = re.sub(pat7, '', ret)
        ret = ret.replace(u"\xa3", '$') #well
        ret = ret.replace("PHRASAL VERBS", 'phrasal-todo')
        #special logic for redundant base words (e.g. actor, actress), may want to handle differently in future
        if not ret[:4] == 'file': #weird header pages wont work here
            pat_special = re.compile("^([A-Za-z]{1}[a-z\s,]{2,30})"+self.base_word_pos)
            finds = pat_special.findall(ret[:60])
            if finds:
                finds = finds[0].split(',')
                if len(finds) > 1 and not ret[:4] == 'file':
                    print("SHOULD ONLY HIT RARELY")
                    remove_redundant = finds[1].strip().upper()
                    ret = ret.replace(", {}".format(remove_redundant), '')

        # Shoot me. Page by page exceptions...
        if self.current_page == 284:
            ret = ret.replace("1 playing card", "1 playing card ADJ. remove-eventually")
        if self.current_page == 816:
            ret = ret.replace("1 noble", "1 noble ADJ. remove-eventually")
        if self.current_page == 942:
            #pat = re.compile("\s([1-9]\s\D{2,100})\s[A-Z]{3,30}") #pages have multi defs same number
            #finds = pat.findall(ret)
            #if finds
            ret = ret.replace("2 part/piece of sth", "3 part/piece of sth")
            ret = ret.replace("a bit small amount", "a bit: small amount")
        if self.current_page == 782:
            ret = ret.replace("3 party", "4 party")
            ret = ret.replace("We're going to a masked ball.", '')
            ret = ret.replace("costume, fancy dress, masked", '')
            ret = ret.replace("college, charity, hunt |", "college, charity, hunt | costume, fancy dress, masked")
        if self.current_page == 1237:
            ret = ret.replace("(usually Cabinet) in government", "in government such as cabinet")
        if self.current_page == 1507:
            ret = ret.replace("2 of a newspaper/magazine", "3 of a newspaper/magazine")
        if self.current_page == 1639: #a lot of ways you could fix the page...
            ret = ret.replace("2 redness in the face", ", redness in the face")
            ret = ret.replace("1 quality that makes sth red, etc.", '')
            ret = ret.replace("PREP. off ~ (= looking or feeling ill)", "1 quality that makes sth red, etc. PREP. off ~ (= looking or feeling ill)")
            ret = ret.replace("3 interesting or exciting details", "2 interesting or exciting details")
        if self.current_page == 2098:
            ret = ret.replace("crown 2 the Crown", 'crown')
        if self.current_page == 2160:
            ret = ret.replace("1 interrupt sb/sth", "3 interrupt sb/sth")
            ret = ret.replace("2 prevent sb/sth leaving/reaching a place", "4 prevent sb/sth leaving/reaching a place")
        if self.current_page == 2201:
            ret = ret.replace("period of 24 hours", "period of twenty-four hours")
        if self.current_page == 2496:
            ret = ret.replace("1 computer disk", "1 computer disk ADJ. remove-eventually")
            ret = ret.replace("2 CD/record", "2 CD/record ADJ. remove-eventually")
        if self.current_page == 3031:
            ret = ret.replace("6 for soldiers/police", "5 for soldiers/police")
            ret = ret.replace("5 for a particular result", "6 for a particular result")
        if self.current_page == 3289:
            ret = ret.replace("3 apparatus for heating rooms", "2 apparatus for heating rooms")
            ret = ret.replace("4 shots from guns", "3 shots from guns")
            ret = ret.replace("2 burning fuel for cooking/heating", "4 burning fuel for cooking/heating")
        if self.current_page == 3496:
            ret = ret.replace(u"below 0\xb0", "below zero degrees")
        if self.current_page == 4437:
            ret = ret.replace(u"by 1.2\xb0C", "by 1.2 degrees celsius")
        if self.current_page == 4746:
            ret = ret.replace("lead1 /li:d/ noun", "lead/first noun")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_1_noun.htmOXFORD Collocations | dictionary for students of English", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_1_noun.htm (1 of 2) [8/26/2009 1:38:43 pm]file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_1_noun.htm", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_1_noun.htm (2 of 2) [8/26/2009 1:38:43 pm]", "")
        if self.current_page == 4748:
            ret = ret.replace("lead2 /li:d/ verb", "lead/second verb")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_2_verb.htmOXFORD Collocations | dictionary for students of English", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_2_verb.htm (1 of 2) [8/26/2009 1:38:44 pm]file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_2_verb.htm", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_2_verb.htm (2 of 2) [8/26/2009 1:38:44 pm]", "")
        if self.current_page == 4750:
            ret = ret.replace("lead3 /led/ noun", "lead/third noun")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_3_noun.htmOXFORD Collocations | dictionary for students of English", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/lead_3_noun.htm [8/26/2009 1:38:45 pm]", "")
        if self.current_page == 4813:
            ret = ret.replace("2 generous", "3 generous")
        if self.current_page == 4915:
            ret = ret.replace("4 sb/sth's appearance", "3 sb/sth's appearance")
            ret = ret.replace("3 expression on sb's face", "4 expression on sb's face")
            ret = ret.replace("4 sb/sth's appearance", "3 sb/sth's appearance")
        if self.current_page == 5779:
            ret = ret.replace("4 happen", "3 happen")
        if self.current_page == 5876:
            ret = ret.replace(u"90\xb0", "90 degrees")
        if self.current_page == 5957:
            ret = ret.replace("measure of liquid", "measure of liquid ADJ. remove-eventually")
        if self.current_page == 6550:
            ret = ret.replace("4 number/note/symbol", "3 number/note/symbol")
            ret = ret.replace("5 letter about your character/abilities", "4 letter about your character/abilities")
            ret = ret.replace("3 book containing facts/information", "6 book containing facts/information")
        if self.current_page in [7040, 8383]:
            ret = ret.replace("TV", "television")
        if self.current_page == 7790:
            ret = ret.replace("strength noun PREP", "strength noun 1 not sure strength def PREP")
            ret = ret.replace("1 how strong sb/sth is", "3 how strong sb/sth is")
        if self.current_page in [8104,8105,8106]:
            ret = ret.replace("tear1 /tie(r)/ noun", "tear/first noun")
            ret = ret.replace("tear2 /tee(r)/ noun", "tear/second noun")
            ret = ret.replace("tear3 /tee(r)/ verb", "tear/third verb")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/tear_1_noun.htmOXFORD Collocations | dictionary for students of English", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/tear_2_noun.htmOXFORD Collocations | dictionary for students of English", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/tear_3_verb.htmOXFORD Collocations | dictionary for students of English", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/tear_1_noun.htm [8/26/2009 2:02:39 pm]", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/tear_2_noun.htm [8/26/2009 2:02:39 pm]", "")
            ret = ret.replace("file:///C|/TEMP/htm/OXFORD_PHRASEBUILDER_HTML/files/tear_3_verb.htm [8/26/2009 2:02:40 pm]", "")
        if self.current_page == 8128:
            ret = ret.replace(u"\xb0", " degrees ")
        if self.current_page == 8806:
            ret = ret.replace("3 the vote: legal right to vote in elections", "2 the vote: legal right to vote in elections")
        return ret

    def split_into_definition_chunks(self):
        definition_chunks = []
        txt = self.text_entries_stripped
        if self.definitions == []:
            first_head = re.findall(self.set_header_regex, txt)[0]
            index_first_head = txt.find(first_head)
            relevant_text = txt[index_first_head:]
            definition_chunks.append(relevant_text)
        else:
            for i, def_s in enumerate(list(reversed(self.definitions))): #easier going in reverse and remove str chunk after appending
                i = len(self.definitions) - i
                i2 = self.special_logic_for_rare_formats_i(i)
                #index_s = txt.find(str(i+1) + ' ' + def_s)
                def_s = (str(i2) + ' ' + def_s).strip()
                index_s = txt.find(def_s)
                end_index = index_s + len(def_s) + 1
                relevant_txt = txt[end_index:]
                #print('banana', txt, def_s, relevant_txt, index_s, end_index)
                if relevant_txt == "":#exception where no sets actually listed for a random def
                    relevant_txt = "ADJ. todo-remove"
                definition_chunks.append(relevant_txt)
                txt = txt[:index_s-1] #for next iteration get rid of extra formatting
        #print('def chunks', list(reversed(definition_chunks)))
        return list(reversed(definition_chunks))

    def get_all_sets_for_chunks(self):
        chunks_final = []
        for chunk in self.definition_chunks:
            sets = self.get_sets_for_chunk(chunk)
            chunks_final.append(sets)
        return chunks_final
        #Note, there could be a duplication issue with certain sets spanning pages on multi page entries

    def get_sets_for_chunk(self, definition_chunk):
        # add logic to avoid PERCENT as a heading, etc.
        tokens = nltk.word_tokenize(definition_chunk)
        all_the_sets = []
        current_token_set = []
        prev_token = None
        prev_token2 = None
        for i, token in enumerate(tokens):
            if i == len(tokens) - 1:
                current_token_set.append(token)
                all_the_sets.append(current_token_set)
                continue
            match = re.match(self.set_header_regex, token)
            special_logic = self.special_logic(tokens, i)
            if special_logic or (prev_token is None and match) or (match and (not prev_token == "+") and (not prev_token2 == "+") and not (prev_token.isupper() and tokens[i+1] == "+")): #e.g. can have VERB + WORD1 WORD2, or W1 W2 + VERB
                all_the_sets.append(current_token_set)
                current_token_set = []
                current_token_set.append(token)
            else:
                current_token_set.append(token)
            prev_token2 = prev_token
            prev_token = token
        if all_the_sets[0] == []:
            all_the_sets = all_the_sets[1:]

        sets_final = []
        sets_final_i = 0
        for i, collset in enumerate(all_the_sets):
            #print(sets_final_i)
            #print(collset)
            for i, token in enumerate(collset):
                if token == "file" and (not collset[i-1] == "NOUN") and collset[i+1] == ":":
                     print('delete wonky footer...', self.base_word)
                     #bad if multi page...????
                     collset = collset[:i]
                # print(collset)
                # if token == "PHRASAL" and collset[i+1] == "VERBS":
                #     collset = collset[:i] + collset[i+2:]
            if filter(lambda x: x in self.legal_categories, collset[:4]): #w1 w1 + V is 4
                'noop - muy bien'
            else:
                collset[:4]
                if collset[0] == 'TEMP' or collset[0][:4] == 'TEMP':
                    print('finicky regex issue with header,removing collset')
                    #print(collset)
                    continue
                elif i != 0:
                    print('bad -- merging into previous',collset[:3])
                    print(collset)
                    sets_final[sets_final_i-1].extend(collset)
                    continue
                else:
                    print(" problemo --- not adding", collset)
                    continue
            sets_final_i += 1
            #print('good in theory', collset)
            sets_final.append(collset)

        return sets_final


    def get_collocations_per_definition_chunks(self):
        # returns array of arrays to map to definitions
        collocations_for_definition_chunks = []
        for def_set in self.sets_per_definition_chunk:
            collocations_for_def_set = []
            for coll_set in def_set:
                collocations_for_set = []
                rule = self.__determine_rule_for_coll_set(coll_set) #append_left, append_right, phrases
                pos_head = coll_set[0]
                coll_set = self.__remove_rule_tokens_from_coll_set(coll_set)
                coll_set = self.__squash_parens(coll_set) # otherwise counts paraens as own characters
                coll_set = self.__filter_out_odd_equal_sign_parens(coll_set)
                coll_set = self.__remove_example_sents_from_coll_set(coll_set, pos_head)
                coll_set = self.__filter_out_misc_noise(coll_set)
                print('and here---',coll_set)
                skip_indexes = []
                last_iter = len(coll_set)-1
                word_in_question = ""
                stops = [",", "|"]
                for i, token in enumerate(coll_set):
                    # need to substitute sb/ sth -- need to substitute ~ -- need to split out slash /
                    # assume up to 5 words in colloc. (phrases...)
                    if i in skip_indexes:
                        continue
                    if token in stops:
                        continue
                    if (last_iter not in [i, i+1]) and (coll_set[i+1] in stops):
                        word_in_question = token
                    elif (i+1 == last_iter) or ((last_iter not in [i, i+1, i+2]) and (coll_set[i+2] in stops)):
                        word_in_question = "{} {}".format(token,coll_set[i+1])
                        skip_indexes.append(i+1)
                    elif (i+2 == last_iter) or ((last_iter not in [i, i+1, i+2, i+3]) and (coll_set[i+3] in stops)):
                        word_in_question = "{} {} {}".format(token,coll_set[i+1],coll_set[i+2])
                        skip_indexes.append(i+1)
                        skip_indexes.append(i+2)
                    elif (i+3 == last_iter) or ((last_iter not in [i, i+1, i+2, i+3, i+4]) and (coll_set[i+4] in stops)):
                        word_in_question = "{} {} {} {}".format(token,coll_set[i+1],coll_set[i+2],coll_set[i+3])
                        skip_indexes.append(i+1)
                        skip_indexes.append(i+2)
                        skip_indexes.append(i+3)
                    elif (i+4 == last_iter) or ((last_iter not in [i, i+1, i+2, i+3, i+4, i+5]) and (coll_set[i+5] in stops)):
                        word_in_question = "{} {} {} {} {}".format(token,coll_set[i+1],coll_set[i+2],coll_set[i+3],coll_set[i+4])
                        skip_indexes.append(i+1)
                        skip_indexes.append(i+2)
                        skip_indexes.append(i+3)
                        skip_indexes.append(i+3)
                    else:
                        word_in_question = token

                    if "~" in word_in_question:
                        collocation = word_in_question.replace("~", self.base_word)
                    elif rule == "append_left":
                        collocation = self.base_word + " " + word_in_question
                    elif rule == "append_right":
                        collocation = word_in_question + " " + self.base_word
                    elif rule == "phrases":
                        collocation = word_in_question
                    elif rule == "quant": #what about WORD ~ QUANT. instead of just QUANT.
                        collocation = word_in_question + " of " + self.base_word
                    else:
                        pdb.set_trace()
                        raise ValueError("something bad w/ rule", self.current_page, coll_set)
                    #print("{} --> {}".format(word_in_question, collocation))
                    collocations_for_set.append(collocation)
                collocations_for_def_set.append(collocations_for_set)
            #collocations_for_set = [y for x in collocations_for_set for y in x] #flatten at this point
            collocations_for_definition_chunks.append(collocations_for_def_set)
        return collocations_for_definition_chunks


    def __remove_example_sents_from_coll_set(self, coll_set, pos_head):
        sent = " ".join(coll_set)
        # Capital letter + period heuristuc
        #pat1 = re.compile("([A-Z]{1}.+?[\.\?]{1})")
        pat1 = re.compile("([A-Z]{1}.+?[\.\?]{1}[a-zA-A'\s]{0,40}\.{0,1})") #accounts for awkwarwd run ins (like p 222)
        matches = pat1.findall(sent)
        self.example_sents.append(matches)
        for match in matches:
            if len(filter(lambda x: x.isupper(), list(match))) > 1 and 'etc' in match: #--> catch Western Europe, NATO, etc.
                continue
            # exception with etc. ...
            match_i_start = sent.find(match)
            match_i_end = match_i_start + len(match)
            sent = sent[:match_i_start] + sent[match_i_end:]
        coll_set2 = sent.split()

        # a/ an phrase, at least 3 words, and word before it appears in it
        delete_indexes = []
        delete_phrases = [] #arr of strings
        for i in range(0, len(coll_set2)-2): #3-gram checking
            if i in delete_indexes:
                continue
            word_set = [coll_set2[i], coll_set2[i+1], coll_set2[i+2]]
            if filter(lambda x: x in [",", "|"], word_set):
                continue
            else:
                if word_set[0] in ["a", "an"]:
                    start_index = i
                    end_index = i+2
                    for i2 in range(end_index+1, len(coll_set2)):
                        if coll_set2[i2] in [",", "|"]:
                            end_index = i2-1
                            break
                        elif i2 == len(coll_set2)-1: #very end
                            end_index = i2
                    full_phrase = coll_set2[start_index:end_index+1]
                    prevw1 = coll_set2[i-1]
                    prevw2 = coll_set2[i-2]
                    if filter(lambda x: x in [prevw1, prevw2], full_phrase): # crude, but try to make sure example phrase has a prev word
                        delete_phrases.append(" ".join(full_phrase))
                        for i3 in range(start_index, end_index+1):
                            delete_indexes.append(i3)
        self.example_sents.append(delete_phrases)
        for phrase in delete_phrases:
            match_i_start = sent.find(phrase)
            match_i_end = match_i_start + len(phrase)
            sent = sent[:match_i_start] + sent[match_i_end:]

        # heuristic for partial phrases outside of above criteria
          # phrase contains base word, word on left end appears in phrase
            # plus logic on word after comma...
            # need stems/ lemmas
            # 'case six cases of suspected child abuse'
            #  | child , elder victims of child abuse | human rights ~s allegations of human rights abuses |
        #print('trying weird shit with', pos_head, sent)
        if not pos_head == "PHRASES":
            sent = self.rare_example_removal(sent)
            st = LancasterStemmer()
            tokens = sent.split()
            base_word_is = [] #can be multi in same sent
            for j, token in enumerate(tokens):
                if st.stem(self.base_word) == st.stem(token):
                    if not self.example_detection_exceptions(token, tokens, j):
                        print('attempting tricky phrase removal')
                        base_word_is.append(j)
            example_strs = []
            for base_word_i in base_word_is:
                # GET WINDOW
                print('at very top...', tokens, base_word_is, base_word_i)
                stops = [",", "|"]
                end_token_i = len(tokens)-1
                start_token_i = 0
                right_stop_token_i = None
                left_stop_token_i = None
                left_boundary_i = None #most important to find
                #assume the phrases always have stop on right (or hit end)
                #assume never a example immediately after stop on left (always another colloc word(s))
                  # will be 1 or more words on left that are colloc words
                #pdb.set_trace()
                if end_token_i != base_word_i:
                    for j2 in range(base_word_i, end_token_i+1):
                        if j2 == end_token_i or tokens[j2+1] in stops:
                            right_stop_token_i = j2
                            break
                else:
                    right_stop_token_i = end_token_i
                if start_token_i != base_word_i:
                    for j3 in list(reversed(range(0, base_word_i+1))):
                        if j3 == start_token_i or tokens[j3-1] in stops or (self.all_are_upper(tokens[j3-1]) and (tokens[j3-1] not in ['TV', 'CD', 'UK', 'B', 'BCG','RAM'])):
                            left_stop_token_i = j3
                            break
                else:
                    left_stop_token_i = start_token_i
                #you know i and everyright to right will be taken, so start left (at stop)
                if right_stop_token_i == None or left_stop_token_i == None:
                    print("problemo - should be finding example but bookends failing", left_stop_token_i, right_stop_token_i)
                    raise ValueError("YIKES")
                if not (right_stop_token_i > left_stop_token_i):
                    print("problemo - should be finding example but bookends failing2", left_stop_token_i, right_stop_token_i)
                    raise ValueError("YIKES2")
                if not (right_stop_token_i - left_stop_token_i > 2):
                    print("***************** possible problemo - should be finding example but bookends failing3", left_stop_token_i, right_stop_token_i)
                    #raise ValueError("YIKES3")
                    print('probably not example, probably is colloc... stemming mishap, or something, just cary on')
                    continue

                #FOR NOW ignore logic about prior word (outside left stop) appearing in example. ... eg child, elder
                lefti = left_stop_token_i
                righti = right_stop_token_i
                if tokens[left_stop_token_i] in stops:
                    lefti = left_stop_token_i+1
                if tokens[right_stop_token_i] in stops:
                    righti = righti-1
                relevant_slice = tokens[lefti:righti+1]
                print('relevant slice', relevant_slice)

                #j4 = lefti
                tokens[lefti] #you know must be colloc or part of colloc (but still dont know if appears in example, because word prior could)
                t1 = tokens[lefti+1].replace("~", self.base_word)
                if filter(lambda x: st.stem(x) == st.stem(t1), relevant_slice[2:]):
                    t2 = tokens[lefti+2].replace("~", self.base_word)
                    if filter(lambda x: st.stem(x) == st.stem(t2), relevant_slice[3:]):
                        t3 = tokens[lefti+3].replace("~", self.base_word)
                        if filter(lambda x: st.stem(x) == st.stem(t3), relevant_slice[4:]):
                            t4 = tokens[lefti+4].replace("~", self.base_word)
                            if filter(lambda x: st.stem(x) == st.stem(t4), relevant_slice[5:]): #5 word colloc with example that follows
                                print("problemo - something probably wrong finding left boudnary", lefti, righti)
                                raise ValueError("Yikes4")
                            else:
                                left_boundary_i = lefti+4
                        else:
                            left_boundary_i = lefti+3
                    else:
                        left_boundary_i = lefti+2
                else:
                    left_boundary_i = lefti+1
                example_strs.append(" ".join(tokens[left_boundary_i:righti+1]))
            self.example_sents.append(example_strs)
            for example_str in example_strs:
                print("----- fuck me if this works ---- subbing our caputred strings", example_str)
                sent = sent.replace(example_str, '')

        return sent.split()


    def __remove_rule_tokens_from_coll_set(self, coll_set):
        coll_set = coll_set[1:] #always get rid of first
        if coll_set[0] == "." or coll_set[0] == "+":
            coll_set = coll_set[1:]
            if coll_set[0].isupper():
                coll_set = coll_set[1:]
        if coll_set[0].isupper():
            if coll_set[1] == "+": # (W1) W2 + POS
                coll_set = coll_set[3:]
            else:
                coll_set = coll_set[1:] #???
        return coll_set

    def __squash_parens(self, coll_set):
        #del_indexes = []
        for i, token in enumerate(coll_set):
            if token == "(":
                coll_set[i+1] = "(" + coll_set[i+1]
                del coll_set[i]
            elif token == ")":
                coll_set[i-1] = coll_set[i-1] + ")"
                del coll_set[i]
        return coll_set

    def __filter_out_odd_equal_sign_parens(self, coll_set):
        collstr = " ".join(coll_set)
        if "=" in collstr:
          finds = re.compile("\(=[a-zA-Z1-9\s]{2,30}\)").findall(collstr)
          for found in finds:
              collstr = collstr.replace(found, '').strip()
          coll_set = collstr.split(" ")
        return coll_set



    def __filter_out_misc_noise(self, coll_set):
        coll_set = filter(lambda x: x not in ["."], coll_set)

        # (= ) stuff remove for now, though may be useful eventually
        # collstr = " ".join(coll_set)
        # if "=" in collstr:
        #   finds = re.compile("\(=[a-zA-Z1-9\s]{2,30}\)").findall(collstr)
        #   for found in finds:
        #       collstr = collstr.replace(found, '').strip()
        #   coll_set = collstr.split(" ")
        return coll_set

    def __determine_rule_for_coll_set(self, coll_set):
        #print("here in rule checking", coll_set)
        if coll_set[0] == "PHRASES":
            return "phrases"
        if coll_set[0] == "QUANT":
            return "quant"
        if coll_set[1] == "." and coll_set[0] == "PREP":
            if self.base_word_pos == 'noun':
                return "append_right"
            elif self.base_word_pos in ['verb', 'adj']:
                return "append_left"
        if coll_set[1] == "." or coll_set[0] == "VERBS":
            return "append_right"
        if coll_set[1] == "+":
            if self.base_word in coll_set[0].lower():
                return "append_left"
            else:
                return "append_right"
        if coll_set[2] == "+":
            return "append_right"

    def __mine_collocations_for_word(self):
        self.first_entry = self.pdf.pages[self.current_page].extractText()
        self.base_word = self.get_base_word()
        self.base_word_pos = self.get_base_word_pos()
        self.base_word_with_pos = self.base_word + "_" + self.base_word_pos
        self.multi_page = self.determine_if_multi_page()
        self.num_pages_for_word = self.page_tracker()[1]
        self.example_sents = []
        if self.should_skip_because_multi_page():
            return False
        self.text_entries = self.setup_and_concat_pages()
        self.text_entries_stripped = self.strip_text_entries()
        if len(self.text_entries_stripped) < 30:
            return False
        self.definitions = self.get_definitions()
        self.definition_chunks = self.split_into_definition_chunks() #all str below a definition
        self.sets_per_definition_chunk = self.get_all_sets_for_chunks()
        self.base_template = self.return_template_with_head_and_definition_chunks()
        self.collocation_by_def_chunks = self.get_collocations_per_definition_chunks()
        return True

    def view_all_coll_in_chunks(self):
        return self.all_coll_chunks

    def get_set_cats_from_chunks(self):
        def_sets = []
        for def_set in self.sets_per_definition_chunk:
            set_sets = []
            for set_set in def_set:
                head_type = ""
                if set_set[0].isupper():
                    head_type += set_set[0]
                else:
                    raise ValueError("coll header/rule is bad")
                if set_set[1].isupper() or set_set[1] == "+":
                    head_type = head_type + " " + set_set[1]
                else:
                    set_sets.append(head_type)
                    continue
                if set_set[2].isupper() or set_set[2] == "+":
                    head_type = head_type + " " + set_set[2]
                else:
                    set_sets.append(head_type)
                    continue
                if set_set[3].isupper():
                    head_type = head_type + " " + set_set[3]
                set_sets.append(head_type)
            def_sets.append(set_sets)
        return def_sets


    def fill_template(self):
        template = self.base_template[self.base_word_with_pos] #means temps wont have base-word-pos keys available...
        set_cats = self.get_set_cats_from_chunks()
        #examples = filter(lambda x: x != [], self.example_sents) #lets keep fine grain structure for now
        examples = self.example_sents
        if len(self.collocation_by_def_chunks) != len(template['sets']):
            raise ValueError('lens are bad')
        for i,coll_set in enumerate(self.collocation_by_def_chunks): #guarantee this fits def order
            template['sets'][i+1]['collocations'] = coll_set
            template['sets'][i+1]['set_cats'] = set_cats[i]
            template['sets'][i+1]['examples'] =  examples
        self.current_template = template
        return template

    # MAIN ITER MAINITER mainiter
    def iter_all_for_template(self):
        for n in range(222, 9095):
            if n in self.total_skip_list:
                continue
            try:
                self.current_page = n
                print(n)
                if self.__mine_collocations_for_word():
                    template = self.fill_template()
                    self.all_templates.append(template)
                else:
                    self.skipped_multi_page.append(n)
                    continue
            except:
                e = traceback.print_exc()
                print('exception page', n, e)
                self.exceptions_in_iter.append([n, e])
                pdb.set_trace()
        return self



    def special_logic(self, tokens, i):
        special1 = self.base_word == "A%20level" and tokens[i] == "A" and tokens[i+1] == "LEVEL" and tokens[i+2] == "+"
        #special2 = tokens[i] == "RAM"
        return special1 #or special2

    # could consider find/replacing text upfront on pages instead of this
    def special_logic_for_rare_formats_i(self, i):
        if self.base_word == "acknowledge" and i == 2:
            return 3
        if self.base_word == "beat" and self.base_word_pos == "verb" and i == 3:
            return 4
        if self.base_word == "beat" and self.base_word_pos == "verb" and i == 4:
            return 5
        return i

    def show_all_collocations_for_template(self, template=None):
        colls = []
        for i in range(0, len(template['sets'])):
            colls.append(template['sets'][i+1]['collocations'])
        return colls

    def show_all_collocations_for_template_flat(self, template=None):
        colls = []
        collsflat = []
        for i in range(0, len(template['sets'])):
            colls.append(template['sets'][i+1]['collocations'])
        for coll1 in colls:
            if type(coll1) is list:
                for coll2 in coll1:
                    if type(coll2) is list:
                        for coll3 in coll2:
                            if type(coll3) is list:
                                for coll4 in coll3:
                                    collsflat.append(coll4)
                            else:
                                collsflat.append(coll3)
                    else:
                        collsflat.append(coll2)
            else:
                collsflat.append(coll1)
        return collsflat


    def show_all_collocations_for_range(self, upto_range):
        temps = self.all_templates[0:upto_range]
        cols = []
        for t in temps:
            cols.append(self.show_all_collocations_for_template(t))
        return cols

    def get_all_c(self, templates=None):
        return self.get_all_collocations_flat(templates)

    #flesh_out_colls_flat()
    def get_all_collocations_flat(self, templates=None):
        # be more careful with this... lots of 1 word collocs...
        if not templates:
            templates = self.all_templates
        cols = []
        for t in templates:
            cols.append(self.show_all_collocations_for_template_flat(t))
        cols = [y for x in cols for y in x]
        return cols

    def get_all_collocs_minus_phrases(self, templates=None):
        all_collocs = []
        if not templates:
            templates = self.all_templates
        if templates:
            for template in templates:
                for i in range(0, len(template['sets'])):
                    phrase_indexes = []
                    pp = template['pp']
                    set_cats = template['sets'][i+1]['set_cats']
                    if 'PHRASES' in set_cats:
                        phrase_indexes = [i2 for i2,x in enumerate(set_cats) if x == "PHRASES"]
                        #print('phrase indexes', phrase_indexes, pp)
                    else:
                        for colloc_set in template['sets'][i+1]['collocations']:
                            all_collocs.append(colloc_set)
                        continue
                    collocs = template['sets'][i+1]['collocations']
                    for j, colloc_set in enumerate(collocs):
                        if j in phrase_indexes:
                            continue
                        else:
                            all_collocs.append(colloc_set)
        return all_collocs

    def inspect_all_phrase_collocs(self,templates=None):
        all_phrase_collocs = []
        if not templates:
            templates = self.all_templates
        if templates:
            for template in templates:
                for i in range(0, len(template['sets'])):
                    pp = template['pp']
                    set_cats = template['sets'][i+1]['set_cats']
                    if 'PHRASES' in set_cats:
                        phrase_indexes = [i2 for i2,x in enumerate(set_cats) if x == "PHRASES"]
                    else:
                        continue
                    collocs = template['sets'][i+1]['collocations']
                    for i3 in phrase_indexes:
                        all_phrase_collocs.append(collocs[i3])
        return all_phrase_collocs


    def inspect_cats_vs_coll_sets(self,templates=None):
        if not templates:
            templates = self.all_templates
        if templates:
            for template in templates:
                print('temp', template)
                for i in range(0, len(template['sets'])):
                    l_cats = len(template['sets'][i+1]['set_cats'])
                    l_collocs = len(template['sets'][i+1]['collocations'])
                    print("COMPARING ---- ",l_cats, l_collocs)

    def all_collocs_fleshed_out(self):
        pass

    def all_are_upper(self, word):
        if filter(lambda x: not x.isupper(), list(word)):
            return False
        else:
            return True

    def compare_url_base_first_word_base(self):
        bads = []
        for n in range(222,9095): #6107 a problem
            if n in self.total_skip_list:
                continue
            print(n)
            self.current_page = n
            self.__mine_collocations_for_word()
            base = self.base_word
            text = self.text_entries_stripped
            first_word_text = self.text_entries_stripped.split(" ")[0]
            second_word_text = self.text_entries_stripped.split(" ")[2]
            print(base, first_word_text)
            if not base == first_word_text:
                print("PROBELM WITH URL pp", n)
                print(base, first_word_text, second_word_text)
                bads.append([n,base,first_word_text])
        print('fin')
        return bads

    def confusing_base_word_pages(self):
        return [222, 306, 407, 580, 768, 817, 916, 936, 948, 988, 989, 990, 1023, 1076, 1077, 1081, 1111, 1175, 1176, 1187, 1222, 1293, 1341, 1342, 1349, 1350, 1369, 1384, 1438, 1468, 1485, 1486, 1487, 1576, 1606, 1677, 1678, 1859, 1990, 2004, 2018, 2053, 2084, 2088, 2089, 2114, 2457, 2702, 2754, 2802, 2881, 3168, 3177, 3254, 3287, 3288, 3293, 3296, 3299, 3388, 3403, 3468, 3499, 3695, 3707, 3722, 3745, 3803, 3909, 3917, 3931, 3994, 4002, 4103, 4132, 4308, 4491, 4560, 4582, 4596, 4657, 4685, 4692, 4711, 4728, 4742, 4746, 4747, 4748, 4749, 4750, 4842, 4913, 4941, 4982, 4989, 5056, 5158, 5159, 5305, 5351, 5362, 5414, 5447, 5562, 5568, 5569, 5571, 5576, 5695, 5850, 5943, 6024, 6047, 6088, 6096, 6176, 6199, 6375, 6539, 6879, 6880, 6939, 7067, 7073, 7104, 7105, 7106, 7107, 7108, 7109, 7110, 7111, 7114, 7115, 7116, 7173, 7186, 7241, 7290, 7481, 7482, 7572, 7590, 7613, 7686, 7701, 7712, 7723, 7743, 7830, 7984, 8077, 8104, 8105, 8106, 8177, 8270, 8335, 8339, 8348, 8349, 8466, 8486, 8488, 8516, 8579, 8623, 8644, 8665, 8775, 8828, 8829, 8861, 8863, 8918, 8954, 9005, 9066]

    def example_detection_exceptions(self, token, tokens, i):
        # GO BACK AND FIX THESE DAMMIT
        if self.current_page == 306:
            if token == "act":
                return True
        if self.current_page == 368:
            if token == "advise" and tokens[i+1] == "sb/sth":
                return True
        if self.current_page == 534:
            if token == "antiques":
                return True
        if self.current_page == 1186:
            if token == "build":
                return True
        if self.current_page == 2178:
            if i+1 < len(tokens)-1:
                if ["dance", ",", "do"] == [token, tokens[i+1], tokens[i+2]]:
                    return True
        if self.current_page == 2685:
            if ["dream", ",", "have"] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 2693:
            if ["drink", ",", "have"] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 3224:
            if i+1 < len(tokens)-1:
                if ['feel', ',', 'get']== [token, tokens[i+1], tokens[i+2]]:
                    return True
        if self.current_page == 3286:
            if token == "finally":
                return True
        if self.current_page == 3285:
            if token == "fine":
                return True
        if self.current_page == 5366:
            if ["name", ",", "pass"] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 5721:
            if token == "paint":
                return True
        if self.current_page == 6391:
            if token == "quotable":
                return True
        if self.current_page == 6499:
            if token == "receive":
                return True
        if self.current_page == 6583:
            if token == "regional" or token == "register":
                return True
        if self.current_page == 7394:
            if [u'sleep', u',', u'snatch'] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 7434:
            if [u'smile', u'|', u'manage'] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 8051:
            if [ u'tall', u',', u'unlikely'] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 8245:
            if [u'tie', u'|', u'loosen'] == [token, tokens[i+1], tokens[i+2]]:
                return True
        if self.current_page == 8656:
            if token == "usually":
                return True
        if self.current_page == 8773:
            if token == 'virulent':
                return True
        if self.current_page == 9018:
            if token == 'work':
                return True
        return False

    def rare_example_removal(self, sent):
        #e.g. commas in partial example phrases are pernicious, but rare
        if self.current_page == 585:
            self.example_sents.append("examples of life thousands of years ago, unearthed by archaeologists")
            sent = sent.replace("examples of life thousands of years ago , unearthed by archaeologists", '')
        if self.current_page == 1243:
            self.example_sents.append("a rich, moist fruit cake")
            sent = sent.replace("a rich, moist fruit cake", '')
        if self.current_page == 1571:
            self.example_sents.append("to work against the clock (= to work fast in order to finish before a particular time)")
            #self.example_sents.append("(= all day and all night) to work around the clock")
            sent = sent.replace("to work against the clock (= to work fast in order to finish before a particular time)", '')
        if self.current_page == 2420:
            self.example_sents.append("the diagnosis of the disease a diagnosis of cancer")
            sent = sent.replace("the diagnosis of the disease a diagnosis of cancer", '')
        if self.current_page == 5283:
            self.example_sents.append("the slopes leading down from the moor")
            sent = sent.replace("the slopes leading down from the moor", '')
        if self.current_page == 5974:
            self.example_sents.append("the lawyer appearing on behalf of the plaintiff")
            sent = sent.replace("the lawyer appearing on behalf of the plaintiff", '')
        if self.current_page == 6845:
            self.example_sents.append("(figurative) to be on the road to recovery/success")
            sent = sent.replace("(figurative) to be on the road to recovery/success", '')
            #sent = sent.replace(("(figurative) to be on the road to recovery/success", ''))
        if self.current_page == 7120:
            self.example_sents.append("the former US Senator, James Hurley")
            sent = sent.replace("the former US Senator , James Hurley", '')
        if self.current_page == 7357:
            self.example_sents.append("the increase in the size of the population")
            sent = sent.replace("the increase in the size of the population", '')
        return sent

    def flesh_out_colls_flat(self, colls=None):
        colls_final = []
        if not colls:
            colls = self.get_all_collocations_flat()
        for collocation in colls:
            if "/" in collocation:
                finds = collocation.split("/")
                if len(finds) > 2:
                    left_col = finds[0]
                    right_col = finds[-1]
                    newphrase1 = " ".join(left_col.split(" ") + right_col.split(" ")[1:])
                    newphrase2 = " ".join(left_col.split(" ")[:-1] + right_col.split(" "))
                    colls_final.append(newphrase1)
                    colls_final.append(newphrase2)
                    for i2 in range(0,len(finds)-2):
                        newphrase = " ".join(left_col.split(" ")[:-1] + [finds[i2+1]] + right_col.split(" ")[1:])
                        colls_final.append(newphrase)
                else:
                    left_col = finds[0]
                    right_col = finds[1]
                    newphrase1 = " ".join(left_col.split(" ") + right_col.split(" ")[1:])
                    newphrase2 = " ".join(left_col.split(" ")[:-1] + right_col.split(" "))
                    colls_final.append(newphrase1)
                    colls_final.append(newphrase2)
            else:
                colls_final.append(collocation)
        return colls_final

    def flesh_out_collocations_in_templates(self, templates=None):
        # /, multi /, sb, sth (Todo), ~ subbing
        # better ~ subbing before or repeat words...
        if not templates:
            templates = self.all_templates
        else:
            for template in templates:
                for i in range(0, len(template['sets'])):
                    def_set_collocs = template['sets'][i+1]['collocations']
                    def_set_collocs_fleshed_out = []
                    for coll_set in def_set_collocs:
                        coll_set_collocs_fleshed_out = []
                        for collocation in coll_set:
                            collocation = collocation.strip()
                            collocation = collocation.replace("|", '')
                            #collocation = collocation.replace("~", template['base_word'])
                            #collocation = collocation.replace("sb", "[PERSON]")
                            #collocation = collocation.replace("sth", "[THING]")
                            if "/" in collocation:
                                finds = collocation.split("/")
                                left_col = finds[0]
                                right_col = finds[1]
                                newphrase1 = " ".join(left_col.split(" ") + right_col.split(" ")[1:])
                                newphrase2 = " ".join(left_col.split(" ")[:-1] + right_col.split(" "))
                                coll_set_collocs_fleshed_out.append(newphrase1)
                                coll_set_collocs_fleshed_out.append(newphrase2)
                                if len(finds) > 2:
                                    try:
                                        for i2 in range(0,len(finds)-2):
                                            newphrase = " ".join(left_col.split(" ")[:-1] + finds[i2+1] + right_col.split(" ")[1:])
                                            coll_set_collocs_fleshed_out.append(new_phrase)
                                    except:
                                        pdb.set_trace()
                            else:
                                coll_set_collocs_fleshed_out.append(collocation)
                        def_set_collocs_fleshed_out.append(coll_set_collocs_fleshed_out)
                    template['sets'][i+1]['collocations'] = def_set_collocs_fleshed_out



    ######## FRAME PRODUCTION ######

    # for colloc lookup, reducing to base defintion
    def get_collocs_by_def(self, templates=None):
        # may need to first run...
        # self.iter_all_for_template()
        # self.flesh_out_collocations_in_templates
        if not templates:
            templates = self.all_templates
        colls_by_def = []
        for t in templates:
            len_sents = len(t['sets'])
            base_word = t['base_word']
            for i in range(1, len_sents+1):
                the_set = t['sets'][i]
                set_cats = the_set['set_cats']
                definition = the_set['definition']
                if definition == "SELF":
                    definition = base_word
                collocs_f = []
                collocs = the_set['collocations']
                for i2, colloc_set in enumerate(collocs):
                    if not set_cats[i2] == "PHRASES":
                        collocs_f.append(colloc_set)
                collocs_f = [y for x in collocs_f for y in x]
                colls_by_def.append([definition, base_word, collocs_f])
        self.collocs_by_def = colls_by_def
        #return colls_by_def

    def all_collocs_for_verb_base(self):
        pass
    def all_colocs_for_adj_base(self):
        pass
    def all_collocs_for_noun_base(self, templates=None):
        noun_temps = self.all_noun_base_templates(templates)
        return self.get_all_collocations_flat(noun_temps)

    def all_noun_base_templates(self, templates=None):
        noun_temps = []
        if not templates:
            templates = self.all_templates
            for temp in templates:
                if temp['pos'] == "noun":
                    noun_temps.append(temp)
        return noun_temps
    def all_verb_base_templates(self, templates=None):
        verb_temps = []
        if not templates:
            templates = self.all_templates
            for temp in templates:
                if temp['pos'] == "verb":
                    verb_temps.append(temp)
        return verb_temps

    #only run if no templates yet
    def get_all_vp_based_frames(self):
        self.iter_all_for_template()
        return self.make_frames_from_nps()
    def make_frames_from_vps(self, templates=None):
        pass

    #only run if no templates yet
    def get_all_np_based_frames(self):
        self.iter_all_for_template()
        return self.make_frames_from_nps()
    def make_frames_from_nps(self, templates=None):
        all_frames = []
        noun_temps = self.all_noun_base_templates(templates)
        for template in noun_temps:
            base_word = template['base_word'].replace("%20", " ")
            for i in range(0,len(template['sets'])):
                set_cats = template['sets'][i+1]['set_cats']
                collocation_sets = template['sets'][i+1]['collocations']
                for j, coll_set in enumerate(collocation_sets):
                    if set_cats[j] in ["QUANT", "PHRASES"] or "NOUN" in set_cats[j]:
                        continue
                        #either skip (phrases), or just use as <X > only key, no rel
                    elif set_cats[j] == "ADJ":
                        for collocation in coll_set:
                            collocation = collocation.replace("%20", " ")
                            x_key = base_word
                            rel_key = collocation.replace(base_word, '')
                            fr = "<X {}><rel can be {}>".format(x_key, rel_key)
                            all_frames.append(fr)
                    elif set_cats[j] == "PREP":
                        continue #need to figure out custom ~ rules...
                        for collocation in coll_set:
                            collocation = collocation.replace("%20", " ")
                            rel_key = collocation.replace(base_word, '')
                            y_key = base_word
                            fr = "<rel {}><Y {}>".format(rel_key, y_key)
                            all_frames.append(fr)
                    elif "VERB +" in set_cats[j]:
                        for collocation in coll_set:
                            collocation = collocation.replace("%20", " ")
                            rel_key = collocation.replace(base_word, '')
                            y_key = base_word
                            fr = "<rel {}><Y {}>".format(rel_key, y_key)
                            all_frames.append(fr)
                    elif "+ VERB" in set_cats[j]:
                        for collocation in coll_set:
                            collocation = collocation.replace("%20", " ")
                            x_key = base_word
                            rel_key = collocation.replace(base_word, '')
                            fr = "<X {}><rel {}>".format(x_key, rel_key)
                            all_frames.append(fr)
        return all_frames
