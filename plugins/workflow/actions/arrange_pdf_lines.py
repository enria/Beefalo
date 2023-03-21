import sys

def remove_redundancy_enter(text):
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        if line.endswith("-"):
            new_lines.append(line[:-1])
        else:
            new_lines.append(line+" ")
    return "".join(new_lines)


if __name__ == "__main__":
    text = sys.argv[1]
    print(remove_redundancy_enter(text),end="")