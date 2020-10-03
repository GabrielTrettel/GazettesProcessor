import os,sys, re
from math import ceil, floor


class Gazette:
    """

    Loads and parses municipal gazettes.


    Attributes:
        file_path: The string path to a gazette.
        file: The string containing a gazette's content.
        city: A string for the city (or cities) of the gazette.
        date: A string for the date of the gazette.

        minimum_spacing_between_cols: An integer for minimum spacingbetween columns. Defaults to 1.
        min_break_ratio: A float for min_break_ratio. Defaults to 0.75.
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
        self.min_break_ratio = 0.75
        self.max_allowed_cols = 5

        self.pages = self.get_list_of_pages()
        self.linear_text = ""
        self.cols_dividers = [self.vertical_lines_finder(x) for x in self.pages]
        self.pages_avg_col = [len(x)+1 for x in self.cols_dividers]

        #  print(self.pages_avg_col)
        if self.pages_avg_col:
            self.total_avg_col = sum(self.pages_avg_col) / len(self.pages_avg_col)
        else:
            self.total_avg_col = 0

        self.split_cols()

        print(self.total_avg_col)
        #  print(self.linear_text)


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
        page_buffer = []


        for line in self.file:
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
         return [line.strip(page_break)]


    def split_cols(self):
        """

        Splits columns of document into a linear layout

        """

        column_dividers = self.cols_dividers
        average_columns_per_page = self.pages_avg_col

        for page_index, page in enumerate(self.pages):
            page_column_dividers =  column_dividers[page_index]
            page_average_columns = average_columns_per_page[page_index]
            page_n_of_columns    = len(page_column_dividers)

            if self.test_if_page_is_not_splittable(page_average_columns, page_column_dividers, page_n_of_columns):
                page_add_to_linear_text = str("".join(page)) + '\014'
                self.linear_text += page_add_to_linear_text
                continue

            page_lines_in_one_column = self.get_lines_in_one_column(page, page_column_dividers)
            self.linear_text += self.lines_to_text(page_lines_in_one_column)


    def get_lines_in_one_column(self, page, page_column_dividers):
        """

        Args
            page: A list of strings, and each string is a line in the page.
            page_column_dividers: A list of ints that were selected as column dividers.

        Returns: A list of strings, and each string is a line in the new page.

        """

        longest_line_len = max(len(line) for line in page)
        page_column_dividers.append((longest_line_len,0))

        lines_to_return = []
        for line in page:
            column_beginning = 0
            current_line = []
            line_size = len(line)

            for column_divider, _ in page_column_dividers:
                if line_size > column_divider and line[column_divider] != ' ':
                    single_column = [line]
                    lines_to_return.append(single_column)
                    column_beginning = -1
                    break

                current_column = line[column_beginning:column_divider]
                current_line.append(current_column)
                column_beginning = column_divider

            lines_to_return.append(current_line)

        return lines_to_return



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

        return result


    def lines_to_text(self, lines):
        max_cols = max(map(lambda x: len(x), lines))
        txt = ""
        for col_i in range(max_cols):
            page_has_content = False

            for line in lines:
                if len(line) > col_i:
                    if line[col_i] != '' and line[col_i].strip() != '':
                        txt += "".join(line[col_i].strip('\n')) + '\n'
                        page_has_content = True


            if lines != [] and page_has_content:
                txt += "\014\n"

        return txt[:-1]


    def vertical_lines_finder(self, page):
        max_line_size = max(len(line) for line in page)

        vertical_lines = self.get_contiguous_space_heights(max_line_size, page)
        candidate_breakpoints = self.remove_contiguous_vertical_lines(vertical_lines, max_line_size)
        return candidate_breakpoints


    def remove_contiguous_vertical_lines(self, vertical_lines, max_line_size):
        if vertical_lines == []:
            return []

        candidate_breakpoints = [vertical_lines[0]]
        col_ctd = 1
        while col_ctd < max_line_size and col_ctd < len(vertical_lines):
            if self.columns_have_minimum_distance(col_ctd, candidate_breakpoints, vertical_lines):
                if vertical_lines[col_ctd] not in candidate_breakpoints:
                    candidate_breakpoints.append(vertical_lines[col_ctd])

            col_ctd +=1

        return candidate_breakpoints


    def columns_have_minimum_distance(self, col_ctd, candidate_breakpoints, vertical_lines, distance=20):
        return abs(candidate_breakpoints[-1][0] - vertical_lines[col_ctd][0]) >= distance


    def get_contiguous_space_heights(self, max_line_size, page):
        contiguous_space_heights = []

        left_delimiter  = floor(0.2 * max_line_size)
        rigth_delimiter = floor(0.8 * max_line_size)
        parsing_window = range(rigth_delimiter, left_delimiter, -1)

        for col_idx in parsing_window:
            ctd = 1
            max_val = 0

            for line_idx, line in enumerate(page):
                max_val = max(max_val, ctd)

                if len(line) <= col_idx:
                    ctd += 1
                else:
                    if self.col_offset_is_only_spaces(page, line_idx, col_idx):
                        ctd += 1
                    else:
                        ctd = 1

            break_ratio = round(max_val/len(page), 2)

            if break_ratio > self.min_break_ratio:
                contiguous_space_heights.append((col_idx, break_ratio))

        contiguous_space_heights = sorted(contiguous_space_heights, key=lambda x: x[1], reverse=True)

        return contiguous_space_heights


    def get_item_from_list(self, line, col_idx, default=' '):
        """
            Returns an list item if it exists, or ´default´, otherwise
        """
        try:
            return line[col_idx]
        except:
            return default


    def col_offset_is_only_spaces(self, page, line_idx, col_idx, offset=6):
        page_slice = page[line_idx : line_idx+offset]
        col_slice = [self.get_item_from_list(line, col_idx) for line in page_slice]

        return all(i==' ' for i in col_slice)



    @staticmethod
    def load_file(path):
        lines = []
        with open(path, 'r') as f:
            lines = f.readlines()

        return lines


if __name__ == "__main__":
    input_f = sys.argv[1]
    output_f = sys.argv[2]

    #  g = Gazette(input_f, "", "")
    #  g.__split_cols()
    #  print(g.linear_text)

    for file in os.listdir(input_f):
        g = Gazette(input_f + '/' + file,"", "")

        print(f"Parsing {file}")
        with open( output_f + "/" + file, 'w') as f:
            f.write(g.linear_text)



