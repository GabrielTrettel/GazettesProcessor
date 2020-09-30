import os,sys, re
from math import ceil


class Gazette:
    """
    
    Loads and parses municipal gazettes. 


    Attributes:
        file_path: The string path to a gazette.
        file: The string containing a gazette's content.
        city: A string for the city (or cities) of the gazette.
        date: A string for the date of the gazette.

        minimum_spacing_between_cols: An integer for minimum spacingbetween columns. Defaults to 1. 
        min_break_value: A float for min_break_value. Defaults to 0.75.
        max_allowed_cols: An int for the maximum number of columns allowed per page.
        split_re: A regex for splitting
        
        pages: A list of pages, each page is a list of lines.

        cols_dividers: ?
        pages_avg_col: ?
        total_avg_col: ?
    
    
    """
    def __init__(self, file_path:str, city:str, date:str):
        """Inits Gazette with a path, a city and a date."""

        self.file = self.load_file(file_path)
        self.city = city
        self.date = date

        self.minimum_spacing_between_cols = 1
        self.min_break_value = 0.75
        self.max_allowed_cols = 5
        self.split_re = r"  +"

        self.pages = self.get_list_of_pages()
        self.linear_text = ""
        self.cols_dividers = [self.vertical_lines_finder(x) for x in self.pages]

        self.pages_avg_col = [len(x)+1 for x in self.cols_dividers]
        # print(self.pages_avg_col)
        if self.pages_avg_col:
            self.total_avg_col = sum(self.pages_avg_col) / len(self.pages_avg_col)
        else:
            self.total_avg_col = 0
        
        self.__split_cols()

        print(self.linear_text)


    def get_list_of_pages(self, page_break='\014'):
        """ 
        Uses file string in self.file and converts it to  a list of lists. 

        Args:
            page_break (str): A string used to delimit page separation 
            in the target document.

        Returns:
            list: A list of pages, each page is a list of lines.

        """
        file = self.file
        pages = []
        page_buffer = []


        for line in file:
            if page_break not in line:
                page_buffer.append(line)
            else:
                full_page = page_buffer
                pages.append(full_page)
                page_buffer = self.reset_buffer(line, page_break)
        
        # Add last page 
        if len(page_buffer) > 0:
            pages.append(page_buffer)

        return pages


    def reset_buffer(self, line, page_break):
         return([line.strip(page_break)])


    def __split_cols(self):
        """
        
        Splits columns of document into a linear layout
        
        """

        column_dividers = self.cols_dividers
        average_columns_per_page = self.pages_avg_col

        for page_index, page in enumerate(self.pages):

            page_column_dividers =  column_dividers[page_index]

            page_n_of_columns = len(page_column_dividers)
            page_average_columns = average_columns_per_page[page_index]
            
            if  self.test_if_page_is_not_splittable(page_average_columns, page_column_dividers, page_n_of_columns):

                page_add_to_linear_text = str("".join(page)) + '\014'

                self.linear_text += page_add_to_linear_text
                continue


            page_lines_in_one_column = self.get_lines_in_one_column(page, page_column_dividers)

            self.linear_text += self.lines_to_text(page_lines_in_one_column) + '\014'


    def get_lines_in_one_column(self, page, page_column_dividers):
        """
        
        Args
            page: A list of strings, and each string is a line in the page. 

            page_column_dividers: A list of ints that were selected as column dividers.

        Returns: A list of strings, and each string is a line in the new page.
        
        """

        lines = []
        for line in page:
            column_beginning = 0
            current_line = []


            for column_divider, _ in page_column_dividers:

                line_size = len(line)

                if line_size > column_divider:
                    current_breakpoint = line[column_divider]
                else:
                    current_breakpoint = ""

                if line_size > column_divider and current_breakpoint != ' ':

                    single_column = [line]
                    lines.append(single_column)
                    column_beginning = -1
                    break

                current_column = line[column_beginning:column_divider]
                current_line.append(current_column)
                column_beginning = column_divider

            # a is legacy code            
            a = page_column_dividers[-1][0]

            if line_size > a and column_beginning != -1:
                 current_line.append(line[a])

            lines.append(current_line)
        return lines

    def test_if_page_is_not_splittable(self, page_average_columns, page_column_dividers, page_n_of_columns):
        """
        
        Args
            page_average_columns: TODO  
            page_column_dividers: TODO
            page_n_of_columns: TODO

        Returns: boolean
        
        """

        average_columns_in_total = self.total_avg_col
        maximum_of_columns_allowed = self.max_allowed_cols

        too_many_columns = page_n_of_columns >= maximum_of_columns_allowed
        no_dividers  =  page_column_dividers == []

        threshold = 1.2 
        more_pages_than_average = page_average_columns >= (threshold * average_columns_in_total)

        min_columns = 2
        too_few_columns = page_average_columns < min_columns

        result = more_pages_than_average or \
                 too_few_columns  or \
                 too_many_columns  or \
                 no_dividers
        
        return(result)


    def lines_to_text(self, lines):
       max_cols = max(map(lambda x: len(x), lines))
       txt = ""
       for col_i in range(max_cols):
           for line in lines:
               if len(line) > col_i:
                   txt += "".join(line[col_i].strip('\n')) + '\n'

       return txt[:-1]


    def vertical_lines_finder(self, page):
        max_cols = max([len(line) for line in page])

        contiguous_space_lengths = []
        for col_n in range(max_cols-1, -1, -1):
            ctd = 0
            max_val = 0
            for i,line in enumerate(page):
                max_val = max(max_val, ctd)
                if len(line) > col_n:
                    if line[col_n] == ' ':
                        ctd += 1
                    else: #if len(page)>i+1 and len(page[i+1]) > col_n and  page[i+1][col_n] != ' ':
                        ctd = 0

            contiguous_space_lengths.append((col_n, round(max_val/len(page), 2)))

        v_lines = sorted(contiguous_space_lengths, key=lambda x: x[1], reverse=True)

        if len(v_lines) == 0 or v_lines[0][1] < self.min_break_value: return []
        v_lines = [i for i in v_lines if i[1] > self.min_break_value]
        if len(v_lines) == 0: return []
        splits = [v_lines[0]]

        col_ctd = 1

        while col_ctd < max_cols:
            try:
                if abs(splits[-1][0] - v_lines[col_ctd][0]) >= 10:
                    if v_lines[col_ctd] not in splits:
                        splits.append(v_lines[col_ctd])
            except: pass
            col_ctd +=1


        return splits


    @staticmethod
    def load_file(path):
        lines = []
        with open(path, 'r') as f:
            lines = f.readlines()

        return lines


if __name__ == "__main__":
    input_f = sys.argv[1]
    output_f = sys.argv[2]

    for file in os.listdir(input_f):
        g = Gazette(input_f + '/' + file,"", "")

        print(f"Parsing {file}")
        with open( output_f + "/" + file, 'w') as f:
            f.write(g.linear_text)



