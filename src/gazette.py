import os,sys, re
from math import ceil


class Gazette:
    def __init__(self, file_path:str, city:str, date:str):
        self.file = self.load_file(file_path)
        self.city = city
        self.date = date

        self.split_re = r"  +"
        self.pages = self.each_page()
        self.linear_text = ""
        self.pages_avg_col = [self.calc_avg_cols(x) for x in self.pages]
        self.total_avg_col = sum(self.pages_avg_col) / len(self.pages_avg_col)

        self.__split_cols()

    def each_page(self):
        pages = []
        page_buff = [] 

        for line in self.file:
            page_buff.append(line)
            if '\014' in line:
                pages.append(page_buff)
                page_buff = []
        
        if len(page_buff) > 0:
            pages.append(page_buff)

        return pages


    def __split_cols(self):
        """ __split_cols
        Splits doc cols into a linear layout
        """
        for i,page in enumerate(self.pages):
            if self.pages_avg_col[i] >= 1.2 * self.total_avg_col or self.pages_avg_col[i] < 2:
                #  print("\n".join(page))
                #  linear_text += "\n".join(line for line in page) + "\n"
                self.linear_text += str("".join(page))
                continue
            

            page_in_cols = []
            footer = []
            for j,line in enumerate(page):
                line = line.strip()
                #  print(line)
                cols = self.split_line_naive_strategy(line)
                if len(cols) == 1 and self.pages_avg_col[i] >= 2 and j > 0.9*len(page):
                    footer.append(" ".join(cols))
                else:
                    page_in_cols.append(cols)

           
            page_text = ""
            for col in range(max([len(x) for x in page_in_cols])):
                for line in page_in_cols:
                    try:
                        page_text += str(line[col]) + "\n"
                    except:
                        page_text += str(line[0]) + "\n"


            self.linear_text += page_text + "\n"
            self.linear_text += "\n".join(footer) + "\n\014\n"
            

    def split_line_naive_strategy(self, line):
        return list(map(lambda x: x.strip(), re.split(self.split_re, line)))

    def split_line_local_strategy(self, lines):
        pass

    def calc_avg_cols(self, page):
        cols_sum = 0

        for line in page:
            line = line.strip()
            cols_sum += (len(re.findall(self.split_re, line)) + 1) 
        
        return round(cols_sum / len(page))
    

    @staticmethod
    def load_file(path):
        lines = []
        with open(path, 'r') as f:
            lines = f.readlines()

        return lines


    


if __name__ == "__main__":
    file = sys.argv[1]

    print(file)
    with open(file, 'r') as f:
        g = Gazette(file, "sa", "10/0/0")
        print(g.pages_avg_col)
        print(len(g.pages))
        print(g.linear_text)


