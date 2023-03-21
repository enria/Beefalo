import sys
import re

def validate_filename(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, " - ", title)  # 替换为下划线
    new_title = re.sub("\n", " ", new_title)
    new_title = re.sub("\s{2,}"," ",new_title)
    return new_title.strip()

if __name__ == "__main__":
    text = sys.argv[1]
    print(validate_filename(text),end="")