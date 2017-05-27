from clients.oxford_collocs import OxCollocations
import pandas as pd

class CollocationsHelper():
	def __init__(self):
		self.oxc = OxCollocations()
		#self.load_collocs()
		#self.all_templates_base = self.oxc.all_templates
		#self.flesh_out_templates()
		#self.all_templates_fleshed = self.oxc.all_templates
		self.collocs_by_def = self.get_collocs_by_def_saved()

	def load_collocs(self):
		#self.oxc.iter_all_for_template()
		pass

	def flesh_out_templates(self):
		#self.oxc.flesh_out_collocations_in_templates() needs to be fixed
		#oxc.flesh_out_colls_flat(colls)
		pass

	def get_collocs_by_def(self):
		cbydef = self.oxc.get_collocs_by_def()
		for cset in cbydef:
			cset[2] = self.oxc.flesh_out_colls_flat(cset[2])
		return cbydef
		# there are still sb/ sth tags no doing anything with.
		# this is main way to 'capture' a colloc, and optionally sub it
		# [definition, base_word, [all the collocs]]

	def get_collocs_by_def_saved(self):
        # after heavy lifing in clients/
		df = pd.read_csv("../assets/processed/collocs_by_def.csv")
		first = df.columns.values.tolist()
		rest = df.values.tolist()
		rest.insert(0, first)
		return rest
