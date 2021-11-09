import os
from PIL import Image
import regex


def pix(data, w, h, use_alpha=False):
    if use_alpha:
        for i in range(w*h):
            if data[i][3] != 0:
                yield (i, *data[i])
    else:
        for i in range(w*h):
            if data[i][0] != 0 or data[i][1] != 0 or data[i][2] != 0:
                yield (i, *data[i])


def mux_H_part_in(scene, replaced, replacement, use_alpha=False, ratio=1.0, x_offset=0, y_offset=0):
    scene_img = Image.open(scene)
    replaced_img = Image.open(replaced)
    replacement_img = Image.open(replacement)
    scene_size = scene_img.size
    replaced_size = replaced_img.size
    replacement_size = replacement_img.size
    if scene_size[0] == replaced_size[0] == replacement_size[0] and scene_size[1] == replacement_size[1] == replacement_size[1]:
        if use_alpha:
            scene_img.paste(replacement_img, None, replacement_img)
        else:
            replacement_data = tuple(pix(replacement_img.getdata(), *replacement_size))
            for i in range(len(replacement_data)):
                offset = replacement_data[i][0] - replacement_data[0][0]
                x = offset % scene_size[0]
                y = int(offset / scene_size[0])
                scene_img.putpixel((x, y), (replacement_data[i][1], replacement_data[i][2], replacement_data[i][3]))
    else:
        scene_data = scene_img.getdata()
        replaced_data = tuple(pix(replaced_img.getdata(), *replaced_size, use_alpha))
        start_pos = 0
        for i in range(scene_size[0]*scene_size[1]):
            for j in range(int(len(replaced_data)*ratio)):
                offset = (replaced_data[j][0] - replaced_data[0][0]) \
                         + int(replaced_data[j][0]/replaced_size[0]) * (scene_size[0] - replaced_size[0])
                if scene_data[i+offset][0] != replaced_data[j][1] \
                        or scene_data[i+offset][1] != replaced_data[j][2] \
                        or scene_data[i+offset][2] != replaced_data[j][3]:
                    break
            else:
                start_pos = i
                break

        if use_alpha:
            x = (start_pos-replaced_data[0][0]) % scene_size[0] + x_offset
            y = int((start_pos-replaced_data[0][0]) / scene_size[0]) + y_offset
            scene_img.paste(replacement_img, (x, y), replacement_img)
        else:
            replacement_data = tuple(pix(replacement_img.getdata(), *replacement_size))
            for i in range(len(replacement_data)):
                offset = (replacement_data[i][0] - replacement_data[0][0]) \
                         + int(replacement_data[i][0]/replacement_size[0]) * (scene_size[0] - replacement_size[0])
                x = (start_pos+offset) % scene_size[0] + x_offset
                y = int((start_pos+offset) / scene_size[0]) + y_offset
                scene_img.putpixel((x, y), (replacement_data[i][1], replacement_data[i][2], replacement_data[i][3]))

    scene_img.save(scene)


print("Don't forget to escape the . in the extension")
print(f"EVERY {os.path.sep} IN THE PATTERNS WILL BE CONSIDERED A BACKSLASH") #.replace(os.path.sep, "\\")
while True:
    scene_pattern = input("Scene pattern: (use {num} to indicate a numbering for use with other parts)\n>")
    replaced_pattern = input("Part to be replaced name: (use {scene_match} for replacement with part of the scene name and {num} for the numbering)\n>")
    replacement_pattern = input("Replacement part name: (use {scene_match} for replacement with part of the scene name and {num} for the numbering)\n>")
    if not ("{num}" in scene_pattern and "{num}" in replaced_pattern and "{num}" in replacement_pattern) and ("{num}" in scene_pattern or "{num}" in replaced_pattern or "{num}" in replacement_pattern):
        print("if {num} is provided, provide it in all three. otherwise, don't provide it at all.")
        continue
    if "{num}" in scene_pattern:
        num_pattern = scene_pattern.replace("{num}", r"\K(\d+)(?=") + ")"
        scene_pattern = scene_pattern.replace("{num}", r"\d+")
    else:
        num_pattern = ""
    if "{scene_match}" in replaced_pattern or "{scene_match}" in replacement_pattern:
        scene_match_pattern = input("{scene_match} pattern:\n>")
    else:
        scene_match_pattern = ""
    ratio = input("Ratio of pixels in the part to be replaced that have to equate to a scene part for the scene part to be replaced: (leave empty for 1)\n"
                  "ONLY USE VALUES BETWEEN 0 AND 1 (1 included)\n>")
    ratio = float(1 if ratio == "" else ratio)
    use_alpha = bool(input("Use alpha? (input anything for y, nothing for n)\n>"))
    x_offset = input("x-axis offset: (use when replacement part is offset from the replaced part. leave empty for 0)\n>")
    x_offset = int(0 if x_offset == "" else x_offset)
    y_offset = input("y-axis offset: (use when replacement part is offset from the replaced part. leave empty for 0)\n>")
    y_offset = int(0 if y_offset == "" else y_offset)
    files = list(next(os.walk("."))[2])

    for scene in files:
        if regex.fullmatch(scene_pattern, scene):
            cur_replaced_pattern = replaced_pattern.format(scene_match=regex.search(scene_match_pattern, scene)[0], num=regex.search(num_pattern, scene)[0])
            for replaced in files:
                if regex.fullmatch(cur_replaced_pattern, replaced):
                    cur_replacement_pattern = replacement_pattern.format(scene_match=regex.search(scene_match_pattern, scene)[0], num=regex.search(num_pattern, scene)[0])
                    for replacement in files:
                        if regex.fullmatch(cur_replacement_pattern, replacement):
                            mux_H_part_in(scene, replaced, replacement, use_alpha, ratio, x_offset, y_offset)
                            break
                    break
    print()
