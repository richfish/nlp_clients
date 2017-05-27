#https://github.com/propbank/propbank-documentation/blob/master/annotation-guidelines/Propbank-Annotation-Guidelines.pdf

from collections import defaultdict
import re
from os import listdir
from os.path import isfile, join
from pprint import pprint as pp
import json
# import spacy
# from spacy.en import English
# parser = English()

import nltk
from nltk.corpus import propbank as pbs
import xml.etree.ElementTree as ET


class PropbankMiner():
    def __init__(self, parser=None, frames_path=None):
        if not frames_path:
            frames_path = "../assets/propbank-frames/frames"
        if not parser:
            parser = None#English()
        self.parser = parser
        self.file_name_list = [f for f in listdir(frames_path) if isfile(join(frames_path, f))]
        self.all_files_parsed = self.parse_all_files() #7,308 xml sets
        #self.current_frame_xml = None
        #self.current_template = None
        self.all_examples = []
        self.all_templates = self.build_all_templates()
        self.all_rolesets = self.get_arr_of_all_rolesets()

    def pp_template(self, template):
        pp(json.loads(json.dumps(template)))

    def get_base_template(self):
        return defaultdict(str, {
            "lemma": "",
            "num_rolesets": 1,
            "rolesets": defaultdict(str,{
                "roleset1": defaultdict(str,{
                    "meta": defaultdict(str, {
                        "alias_txts": [],
                        "framenet_names": [],
                        "verbnet_names": [],
                        "num_roles": 0,
                        "num_examples": 0
                    }),
                    "roles": [], #[n_val, f_val, descrip], [n_val, f_val, descrip]... #different than argtype below
                    "examples": defaultdict(str,{
                        "example1": defaultdict(str, {
                            "name": "", #name tag in <example>
                            "text": "",
                            "args": [] #[argtype, f_val, text], [argtype, f_val, text]... argtype can be arg0, arg1, rel, argm
                        })
                    })
                })
            })
        })

    def parse_all_files(self):
        self.file_name_list.remove('frameset.dtd')
        parsed = []
        for fname in self.file_name_list:
            parsed.append(ET.parse('../assets//propbank-frames/frames/' + fname))
        return parsed

    def build_all_templates(self):
        complete_templates = []
        for parsed_file in self.all_files_parsed:
            complete_templates.append(self.fill_base_template(parsed_file))
        return complete_templates

    def fill_base_template(self, parsed_file=None):
        base_template = self.get_base_template()
        root = parsed_file.getroot()
        rolesets = root.findall('predicate/roleset')
        base_template["lemma"] = root[0].get('lemma')
        if base_template["lemma"] is None:
            base_template["lemma"] = "NONE"
        base_template["num_rolesets"] = len(rolesets)
        for i, r in enumerate(rolesets):
            if i == 0:
                base_r = base_template["rolesets"]["roleset1"]
            else:
                base_template["rolesets"]["roleset"+str(i+1)] = defaultdict(str)
                base_r = base_template["rolesets"]["roleset"+str(i+1)]
                base_r["meta"] = defaultdict(str)
                base_r["examples"] = defaultdict(str)
            examples = r.findall('example')
            role_collections = r.findall('roles')
            if len(role_collections) > 1:
                raise ValueError('More than one role collection') #quirk of data
            roles = role_collections[0]
            # alias/ meta
            aliases = r.findall('aliases')[0].findall('alias')
            base_r["meta"]["alias_txts"] = []
            base_r["meta"]["framenet_names"] = []
            base_r["meta"]["verbnet_names"] = []
            base_r["meta"]["pos"] = []
            base_r["meta"]["name"] = r.get('name')
            base_r["meta"]["lemma"] = base_template["lemma"]
            base_r["meta"]["num_roles"] = len(roles)
            base_r["meta"]["num_examples"] = len(examples)
            for j, alias in enumerate(aliases):
                base_r["meta"]["alias_txts"].append(alias.text)
                base_r["meta"]["framenet_names"].append(alias.get('framenet').split())
                base_r["meta"]["verbnet_names"].append(alias.get('verbnet').split())
                base_r["meta"]["pos"].append(alias.get('pos'))
            # roles
            roles_collected = []
            for role in roles:
                n_val = role.get('n')
                f_val = role.get('f')
                description = role.get('descr')
                roles_collected.append([n_val, f_val, description])
            base_r["roles"] = roles_collected
            # examples
            for i2, example in enumerate(examples):
                if i == 0 and i2 == 0:
                    ex = base_r["examples"]["example1"]
                else:
                    base_r["examples"]["example"+str(i2+1)] = defaultdict(str)
                    ex = base_r["examples"]["example"+str(i2+1)]
                ex["name"] = example.get("name")
                ex["text"] = example.find('text').text
                args_collected = []
                for child in example:
                    if child.tag == "text":
                        continue
                    argtype = child.tag
                    if child.get('n'):
                        argtype += child.get('n')
                    f_val = child.get('f')
                    text = child.text
                    args_collected.append([argtype, f_val, text])
                ex["args"] = args_collected
        return base_template

    def get_arr_of_all_rolesets(self):
        allrolesets = []
        for t in self.all_templates:
            for i in range(1,int(t['num_rolesets'])+1):
                allrolesets.append(t['rolesets']['roleset'+str(i)])
        return allrolesets


    def get_role_types_per_template(self, template): #[a,b], [a,b]... for all 7k+ frames
        rolses_for_t = []
        for k,v in template['rolesets'].iteritems():
            roles = v['roles']
            for i, role in enumerate(roles):
                rolses_for_t.append([role[0], role[1], template['lemma']+str(i+1)])
        return rolses_for_t

    def get_all_role_types(self):
        all_roles = []
        for template in self.all_templates:
            all_roles.append(self.get_role_types_per_template(template))
        return [y for x in all_roles for y in x]

    def get_all_example_text(self):
        for template in self.all_templates:
            for i in range(0, template['num_rolesets']):
                print('ERE', template)
                examples = template['rolesets']['roleset'+str(i+1)]['examples']
                for _,v in examples.iteritems():
                    self.all_examples.append(v['text'])
        return True


    def basic_arg0_arg1_frames(self):
        frames = []
        rolesets = filter(lambda x: ['j'] !=  x['meta']['pos'] and len(x['roles']) > 1, self.all_rolesets)
        for roleset in rolesets:
            r = roleset['roles']
            if r[0][0] == None:
                del r[0]
            if len(r) > 1:
                if r[0][0] in ["0", "1"]: #treat same for now, ideally would just be 0
                    arg0_txt = r[0][-1]
                    rel_txt1 = roleset['meta']['lemma'] #either lemma or roleset name
                    rel_txt2 = roleset['meta']["name"]
                    arg1_txt = r[1][-1]
                    frame = unicode("<X {}><rel {}><Y {}>").format(arg0_txt, rel_txt1, arg1_txt)
                    frames.append(frame)
                    frame = unicode("<X {}><rel {}><Y {}>").format(arg0_txt, rel_txt2, arg1_txt)
                    frames.append(frame)
                    if len(r) > 2: #DIR and what not
                        dirobj = filter(lambda x: x[0] == "2" and x[1].lower() == "dir", r)
                        if dirobj:
                            dirobj_txt = dirobj[-1]
                            frame = unicode("<X {}><rel {}><Y {}>").format(arg0_txt, rel_txt2, dirobj_txt) #use roleset name
                            frames.append(frame)
        return frames

    def basic_example_baesd_frames(self):
        pass

    def make_frames_from_examples(self):
        pass
        # just the arg0,arg1, rel constructs, actual examples are too lengthy

    def make_abstract_frames_from_role_rules(self):
        pass
