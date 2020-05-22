''' very similar tests for find_aa_mutations '''

import shutil 
from click.testing import CliRunner
from itertools import compress
import os
import click
import pandas as pd
import vcfpy
from pyfaidx import Fasta
import unittest

from cerebra.find_aa_mutations import find_aa_mutations
from cerebra.find_aa_mutations import AminoAcidMutationFinder
from cerebra.protein_variant_predictor import ProteinVariantPredictor
from cerebra.find_aa_mutations import AminoAcidMutationFinder
from cerebra.utils import *


class FindAAMutationsTesterAdv(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		''' __init__ method for class obj '''
		data_path = os.path.abspath(__file__ + '/../' + 'data/test_find_aa_mutations/')
		cosmicdb_path =  data_path + '/CosmicGenomeScreensMutantExport.min.tsv'
		annotation_path = data_path + '/gencode.v33.greatestHits.annotation.gtf'
		genomefa_path = data_path + '/GRCh38_limited.fa.gz'

		self.input_path = data_path + '/vcf/'
		self.input_paths = [self.input_path + x for x in os.listdir(self.input_path)]
		
		self.cosmic_df = pd.read_csv(cosmicdb_path, sep='\t')
		self.annotation_df = pd.read_csv(annotation_path, sep='\t', skiprows=5)
		self.genome_faidx = Fasta(genomefa_path)


	def test_aa_mutation_finder_setup(self):
		''' essentially making an AminoAcidMutationFinder object, from scratch '''
		annotation_genome_tree = GenomeIntervalTree(
			lambda feat: feat.pos,
			(GFFFeature(row) for _, row in self.annotation_df.iterrows()))

		protein_variant_predictor = ProteinVariantPredictor(
									annotation_genome_tree, self.genome_faidx)

		assert len(annotation_genome_tree.records) == 885
		assert len(annotation_genome_tree.tree_map) == 4
		assert True == True

		assert len(protein_variant_predictor.transcript_records) == 17
		assert len(protein_variant_predictor.tree.records) == 230
		assert len(protein_variant_predictor.tree.tree_map) == 2
		assert True == True


	def test_cosmic_filter(self):
		''' make a BARE AminoAcidMutationFinder, then setup the cosmic_genome_tree
			obj and evalutate  '''
		aa_mutation_finder_bare = AminoAcidMutationFinder.__new__(AminoAcidMutationFinder)

		# this is what we want to do!
		filtered_cosmic_df = aa_mutation_finder_bare._make_filtered_cosmic_df(self.cosmic_df)

		cosmic_genome_tree = GenomeIntervalTree(
                lambda row: GenomePosition.from_str(
                    str(row["Mutation genome position"])),
                (row for _, row in filtered_cosmic_df.iterrows()))

		assert len(filtered_cosmic_df.index) == 93
		assert len(filtered_cosmic_df.columns) == 34

		assert len(cosmic_genome_tree.records) == 93
		assert len(cosmic_genome_tree.tree_map) == 1

		assert True == True


	def test_genome_position_init(self):
		''' testing genome pos strings to make sure they contain what we've
			placed in the test vcf files '''

		A1_gps = ['7:55191822-55191822', '12:25245351-25245351', '12:25245347-25245347', 
					'7:55191822-55191822']
		A2_gps = ['1:631862-631862', '1:633561-633561', '1:634112-634112', '1:634229-634229',
				 	'1:914949-914949']
		A3_gps = ['1:629906-629906', '1:634112-634112', '1:634229-634229', '1:634244-634244',
				 	'1:1013541-1013541']
		A4_gps = ['1:1010878-1010878', '1:1010892-1010892', '1:1010895-1010895', 
					'1:1010904-1010904', '1:1010905-1010905']
		A5_gps = ['1:630317-630317', '1:633747-633747', '1:633824-633824', 
					'1:1233917-1233917', '1:1816741-1816741']

		for vcf_path in self.input_paths:
			curr_vcf = vcf_path.strip(self.input_path)

			vcf_reader = vcfpy.Reader.from_path(vcf_path)
			curr_gps = []

			for record in vcf_reader:
				record_pos = GenomePosition.from_vcf_record(record)
				curr_gps.append(str(record_pos))

			if curr_vcf == 'A1':
				assert curr_gps == A1_gps
			elif curr_vcf == 'A2':
				assert curr_gps == A2_gps
			elif curr_vcf == 'A3':
				assert curr_gps == A3_gps
			elif curr_vcf == 'A4':
				assert curr_gps == A4_gps
			elif curr_vcf == 'A5':
				assert curr_gps == A5_gps

		assert True == True


	def test_assert(self):
		assert True == True


if __name__ == "__main__":
    unittest.main()