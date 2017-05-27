 # https://verbs.colorado.edu/~mpalmer/projects/verbnet.html

from collections import defaultdict
import re
from os import listdir
from os.path import isfile, join
from pprint import pprint as pp
import json

import xml.etree.ElementTree as ET


class Verbnet():
    def __init__(self, parser=None):
        self.files_path = "../assets/verbnet/"
        self.parser = parser #for mining examples
        self.file_name_list = [f for f in listdir(self.files_path) if isfile(join(self.files_path, f)) and f[-3:] == "xml"]
        self.all_files_parsed = self.parse_all_files() #277
        self.all_templates = self.build_all_templates()
        self.all_words_per_group = self.evocation_words_per_main_class()

    def pp_template(self, template):
        pp(json.loads(json.dumps(template)))

    def parse_all_files(self):
        #self.file_name_list.remove('frameset.dtd')
        parsed = []
        for fname in self.file_name_list:
            parsed.append(ET.parse(self.files_path + fname))
        return parsed

    def build_all_templates(self):
        complete_templates = []
        for parsedf in self.all_files_parsed:
            complete_templates.append(self.fill_base_template(parsedf))
        return complete_templates

    def fill_base_template(self, parsedf):
        # all class/subclass -> members, themroles, frames, subclasses
        root = parsedf.getroot()
        subclasses = self.get_all_subclasses_flat(root)
        all_classes = [root] + subclasses
        frames_count = [len(x.find("FRAMES").findall("FRAME")) for x in all_classes]
        base_t = defaultdict(str,{
            "name": root.get("ID"),
            "num_frames": frames_count,
            "num_classes": len(all_classes)
        })
        for i in range(0, len(all_classes)):
            current_c = all_classes[i]
            base_t["class" + str(i+1)] = defaultdict(str)
            c = base_t["class" + str(i+1)]
            # members
            members = current_c.findall("MEMBERS/MEMBER")
            c['members'] = []
            c['member_names'] = []
            for member in members:
                name, wn_g = member.attrib.get('name').replace("_", " "), member.attrib.get('grouping')
                c['members'].append([name,wn_g])
                c['member_names'].append(name)
            #themrole
            c['themroles'] = []
            themroles = current_c.findall("THEMROLES/THEMROLE")
            for themrole in themroles:
                kind = themrole.attrib.get('type')
                selrestrs = themrole.findall("SELRESTRS/SELRESTR")
                if selrestrs:
                    selrestrs = [x.attrib.get('type') for x in selrestrs]
                c['themroles'].append([kind, selrestrs])
            #frames
            frames = current_c.findall("FRAMES/FRAME")
            c['frame_count'] = len(frames)
            c['frames'] = []
            for frame in frames:
                fhash = defaultdict(str)
                dattribs = frame.find('DESCRIPTION').attrib
                fhash['construction'] = [dattribs.get('primary'), dattribs.get('secondary')]
                fhash['examples'] = [x.text for x in frame.findall("EXAMPLES/EXAMPLE")]
                fhash['syntax'] = []
                for el in frame.find('SYNTAX').getchildren():
                    fhash['syntax'].append([el.tag, el.get('value')])
                c['frames'].append(fhash)
        return base_t

    def get_all_subclasses_flat(self,root):
        d1 = root.findall("SUBCLASSES/VNSUBCLASS")
        d2 = root.findall("SUBCLASSES/VNSUBCLASS/SUBCLASSES/VNSUBCLASS")
        d3 = root.findall("SUBCLASSES/VNSUBCLASS/SUBCLASSES/VNSUBCLASS/SUBCLASSES/VNSUBCLASS")
        d4 = root.findall("SUBCLASSES/VNSUBCLASS/SUBCLASSES/VNSUBCLASS/SUBCLASSES/VNSUBCLASS/SUBCLASSES/VNSUBCLASS")
        return d1 + d2 + d3 + d4

    def get_all_members(self):
        members = []
        for t in self.all_templates:
            for i in range(1, int(t['num_classes'])+1):
                members.append([x[0] for x in t['class'+str(i)]['members']])
        return members

    def get_all_constructions_for_word(self):
        pass

    def evocation_words_per_main_class(self): # e.g. not just per subclass
        all_words_per_group = []
        for template in self.all_templates:
            words_per_main_class = []
            num_c = template['num_classes']
            for i in range(1, int(num_c)+1):
                words_per_main_class.append(template["class"+str(i)]['member_names'])
            all_words_per_group.append(words_per_main_class)
        return all_words_per_group
        #return all_words_per_group


#
# Frames
#  description:
#    #primary="NP V NP.stimulus" secondary="NP-PP; Attribute Object, Possessor-PP"
#
# # during event...
# <PRED value="avoid">
#     <ARGS>
#         <ARG type="Event" value="during(E)"/>
#         <ARG type="ThemRole" value="Agent"/>
#         <ARG type="ThemRole" value="Theme"/>
#     </ARGS>
# </PRED>
#
#
# #Location eg. Source Usually introduced by a source prepositional phrase (mostly headed by `from' or `out of')
# <THEMROLE type="Agent">
#     <SELRESTRS logic="or">
#         <SELRESTR Value="+" type="animate"/>
#         <SELRESTR Value="+" type="organization"/>
#     </SELRESTRS>
# </THEMROLE>
# <THEMROLE type="Theme">
#     <SELRESTRS>
#         <SELRESTR Value="+" type="animate"/>
#     </SELRESTRS>
# </THEMROLE>
# <THEMROLE type="Source">
#     <SELRESTRS>
#         <SELRESTR Value="+" type="location"/>
#     </SELRESTRS>
# </THEMROLE>
# <THEMROLE type="Destination">
#     <SELRESTRS>
#         <SELRESTR Value="+" type="location"/>
#         <SELRESTR Value="-" type="region"/>
#     </SELRESTRS>
# </THEMROLE>
#
#
# #The syntax in frame can be important too:
# #** agent should just be person
# <SYNTAX>
#     <NP value="Agent">
#         <SYNRESTRS/>
#     </NP>
#     <VERB/>
#     <NP value="Theme">
#         <SYNRESTRS/>
#     </NP>
#     <PREP value="to">
#         <SELRESTRS/>
#     </PREP>
#     <NP value="Destination">
#         <SYNRESTRS/>
#     </NP>
# </SYNTAX>

# <DESCRIPTION descriptionNumber="0.7" primary="It V" secondary="Intransitive; Expletive Subject" xtag=""/>
# <EXAMPLES>
#     <EXAMPLE>It's raining.</EXAMPLE>
# </EXAMPLES>


#<SELRESTR Value="+" type="human"/>... sometimes good to track
