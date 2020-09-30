import sys
import os
from gazette import Gazette

input_file = sys.argv[1]
output_file = sys.argv[2]

g = Gazette(input_file, city="?", date="?" )

print(f"Parsing {input_file}")
with open(output_file, 'w') as f:
    f.write(g.linear_text)
