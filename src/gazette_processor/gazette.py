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
        pages = []
        page_buff = []


        for line in self.file:
            if page_break in line:
                pages.append(page_buff)
                page_buff = [line.strip(page_break)]
            else:
                page_buff.append(line)

        if len(page_buff) > 0:
            pages.append(page_buff)

        return pages


    def __split_cols(self):
        """
        Splits columns of document into a linear layout
        """

        for i,page in enumerate(self.pages):
            split_lines = self.cols_dividers[i]

            if  self.pages_avg_col[i] >= 1.2 * self.total_avg_col \
                or self.pages_avg_col[i] < 2 \
                or len(self.cols_dividers[i]) >= self.max_allowed_cols\
                or split_lines == []:

                self.linear_text += str("".join(page)) + '\014'
                continue


            lines = []
            for line in page:
                prev = 0
                curr_line = []
                for col_n, _ in split_lines:
                    if len(line) > col_n and line[col_n] != ' ':
                        lines.append([line])
                        prev = -1
                        break

                    curr_line.append(line[prev:col_n])
                    prev = col_n


                a = split_lines[-1][0]
                if len(line) > a and prev != -1: curr_line.append(line[a])

                lines.append(curr_line)

            self.linear_text += self.lines_to_text(lines) + '\014'



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



