import unittest
from gazette_processor.gazette import Gazette
import os


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.gp = Gazette('test/test_file.txt' , city="?", date="?")


    def test_get_list_of_pages(self):
        result = self.gp.get_list_of_pages()
        len_result = len(result)
        self.assertEqual(3, len_result, "A quantidade de paginas não retornou o valor correto")

    def test_if_it_is_consistently_failing(self):
        result = self.gp.linear_text
        output_file = 'test/test_output.txt'
        with open(output_file, 'r') as f:
                expected = f.read()

        self.assertEqual(result, expected, "Something changed")




if __name__ == '__main__':
    unittest.main()