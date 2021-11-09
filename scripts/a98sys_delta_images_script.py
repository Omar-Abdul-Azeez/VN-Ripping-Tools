import os
import regex

print("Don't forget to escape the . in the extension")
print(f"EVERY {os.path.sep} IN THE PATTERNS WILL BE CONSIDERED A BACKSLASH")
while True:
    source_pattern = input("Source pattern:\n>")#.replace(os.path.sep, "\\")
    delta_pattern = input("Delta pattern: (use {source_match} for replacement with part of the source)\n>")#.replace(os.path.sep, "\\")
    source_match_pattern = None
    if "{source_match}" in delta_pattern:
        source_match_pattern = input("{source_match} pattern:\n>")#.replace(os.path.sep, "\\")
    filter = input("Filter color: (eg. 0000ff for blue)\n>")
    files = list(next(os.walk("."))[2])
    for source in files:
        if regex.fullmatch(source_pattern, source):
            cur_delta_pattern = delta_pattern
            if "{source_match}" in delta_pattern:
                cur_delta_pattern = delta_pattern.format(source_match=regex.search(source_match_pattern, source)[0])
            for delta in files:
                if regex.fullmatch(cur_delta_pattern, delta):
                    print(f"Majiro_mask_me.exe -s {source} -f 0x{filter} -o blend\\ -d {delta}")
                    os.system(f"Majiro_mask_me.exe -s {source} -f 0x{filter} -o blend\\ -d {delta}")
    print()
