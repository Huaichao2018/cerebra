import unittest
import math
import io
from click.testing import CliRunner
import click
import os
from pathlib import Path

import vcfpy

from cerebra.germline_filter import write_filtered_vcf
from cerebra.utils import GenomePosition, GenomeIntervalTree

class GermlineFilterTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.data_path = Path(
            __file__).parent / "data" / "test_germline_filter"

        self.vcf_path = Path(
            __file__).parent / "data" / "test_germline_filter" / "experimental"
        self.filt_path = Path(
            __file__).parent / "data" / "test_germline_filter" / "gl_out"
        self.germ_path = Path(
            __file__).parent / "data" / "test_germline_filter" / "germline"

    def test_germline_filter(self):
        filtered_cell_vcf_paths = self.filt_path.glob("GF_*.vcf")

        for filtered_cell_vcf_path in filtered_cell_vcf_paths:
            cell_name = filtered_cell_vcf_path.stem.replace("GF_", '')
            cell_vcf_path = self.vcf_path / (cell_name + ".vcf")
            germline_vcf_paths = self.germ_path.glob(cell_name + "_GL*.vcf")

            # Create germline genome tree

            germline_vcf_records = [list(vcfpy.Reader.from_path(path)) for path
                                    in germline_vcf_paths]

            # Flatten records
            germline_vcf_records = sum(germline_vcf_records, [])

            germline_genome_tree = GenomeIntervalTree(
                GenomePosition.from_vcf_record, germline_vcf_records)

            # Test writing VCF

            with io.StringIO() as out_file:
                with open(cell_vcf_path, mode='r') as in_file:
                    write_filtered_vcf(in_file, germline_genome_tree, out_file)

                # Reset the buffer's cursor position
                out_file.seek(0)

                with open(filtered_cell_vcf_path, mode='r') as expected_file:
                    expected_reader = vcfpy.Reader.from_stream(expected_file)
                    out_reader = vcfpy.Reader.from_stream(out_file)

                    expected_records, out_records = list(
                        expected_reader), list(out_reader)

                    self.assertEqual(expected_records, out_records)


    def test_basic(self):
        ''' does germline-filter return w/o error? '''
        from cerebra.germline_filter import germline_filter

        data_path = os.path.abspath(__file__ + '/../' + 'data/test_germline_filter/')
        gl_path = data_path + '/germline/'
        experimental_path = data_path + '/experimental/'
        meta_path = data_path + '/meta.csv'
        out_path = data_path + '/gl_out/'

        runner = CliRunner()
        result = runner.invoke(germline_filter, ["--processes", 1, 
                                            "--germline", gl_path, 
                                            "--cells", experimental_path, 
                                            "--metadata", meta_path, 
                                            "--outdir", out_path])

        assert True == True
        assert result.exit_code == 0
        assert os.path.isfile(out_path + "A1.vcf")

        os.remove(out_path + 'A1.vcf')


if __name__ == "__main__":
    unittest.main()
