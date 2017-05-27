#Full text annotation... may help https://framenet.icsi.berkeley.edu/fndrupal/fulltextIndex


import collections
from collections import defaultdict
import re
import time
from os import listdir
from os.path import isfile, join
from pprint import pprint as pp
import json

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


class FramenetMiner():

    def __init__(self, parser=None, frames_path=None):
        if not frames_path:
            frames_path = "../assets/framenet-frames/"
        if not parser:
            parser = None#English()
        self.frames_path = frames_path
        self.parser = parser
        self.lu_pat = re.compile("([a-zA-Z\s\d\-\(\)]+)\.")
        self.file_name_list = [f for f in listdir(self.frames_path) if isfile(join(self.frames_path, f)) and f[-3:] == "xml"]
        self.all_files_parsed = self.parse_all_files() # len 1221
        self.all_templates = self.build_all_templates()


    def pp_template(self, template):
        pp(json.loads(json.dumps(template)))

    def parse_all_files(self):
        parsed = []
        for fname in self.file_name_list:
            parsed.append(ET.parse(self.frames_path + fname))
        return parsed

    def build_all_templates(self):
        completed_templates = []
        for parsedf in self.all_files_parsed:
            completed_templates.append(self.fill_base_template(parsedf))
        return completed_templates

    def fill_base_template(self, parsedf):
        root = parsedf.getroot()
        frame_name = root.attrib['name'].replace("_", " ").lower()
        all_els = root.getchildren()
        def_raw = filter(lambda x: 'definition' in str(x), all_els)[0].text
        all_lex = filter(lambda x: 'lexunit' in str(x), all_els)
        all_lex_word_pos = []
        for lex in all_lex:
            pos = lex.attrib['pos']
            name = lex.attrib['name'].replace("]", '').replace("[",'')
            find = self.lu_pat.findall(name)
            if find:
                find = find[0].lower()
                all_lex_word_pos.append([find, pos])
        base_t = defaultdict(str,{
            'f_name': frame_name,
            'def_raw': def_raw,
            'lus': all_lex_word_pos
        })
        return base_t


    def get_all_frame_elements(self):
        fes = []
        for content in self.all_files_parsed:
            fes = content.findAll('fe')

    def get_frequency_of_fe(self, fe_name):
        counter = collections.Counter(a)
        return counter[fe_name]
        #counter.most_common(30) etc

    def if_should_ignore_frame_relation(self, frame):
        pass

    def is_frame_probably_useless(self, frame):
        pass

    def get_list_of_probably_useless_frames(self):
       pass

    def get_other_frames_by_fe(self):
        pass

    def get_view_all_peripheral_fes(self):
        pass

    def get_valence_mapping_for_lu(self):
        pass

    def get_data(self):
        r = requests.get("https://framenet2.icsi.berkeley.edu/fnReports/data/frameIndex.xml?mode=frameIndex&frame=&banner=")
        s = BeautifulSoup(r.text, 'html.parser')
        frames = s.findAll('frame')
        names = []

        for frame in frames:
            names.append(frame.get('name'))
        return names # 1221
        frame_data = []
        #[u'Abandonment', u'Abounding_with', u'Absorb_heat', u'Abundance', u'Abusing']
        for name in names:
            print(name)
            r = requests.get("https://framenet2.icsi.berkeley.edu/fnReports/data/frame/{}.xml?banner=".format(name))
            s = BeautifulSoup(r.text, 'html.parser')
            file = open(name+".xml", "wb")
            file.write(str(s))
            file.close()

        # different strategy ... expand
        driver = webdriver.PhantomJS()
        driver.get("https://framenet.icsi.berkeley.edu/fndrupal/index.php?q=frameIndex")
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "myDynamicElement"))
            )
        finally:
            driver.quit()




# Notes
# the lus grouped under a frame gives you another sort of similarity/ generalizaing strategy
    # Boarding a bus and arriving somewhere have no necessary relation to each other. However, the noun bus
    # is a lexical unit in the Vehicle frame and that frame is linked to the Motion frame, which in turn is used by
    # the Arriving frame that includes come. The framal links between bus and come thus provide some evidence
    # that a semantic equivalence may be intended.
