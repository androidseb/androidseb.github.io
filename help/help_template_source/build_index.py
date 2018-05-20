import os
import re

DISPLAY_CLASSES_PREFIX = 'class="devices_'
DISPLAY_CLASSES = [
    'devices_android',
    'devices_ios',
    'devices_web',
]
HTML_TAGS_HIERARCHY_LEVELS = {
    'h1': 1,
    'h2': 2,
    'p': 5,
    'ul': 3,
    'ol': 3,
    'li': 4,
}
TOC_MAX_HIERARCHY_LEVEL = 2


def copy_file_lines_to(source_file_path, dest_file):
    if not os.path.exists(source_file_path):
        return
    with open(source_file_path) as f:
        for line in f.readlines():
            dest_file.write(line)


def filter_line_device_class(line):
    strings_to_eliminate = []
    for dc in DISPLAY_CLASSES:
        strings_to_eliminate.append(' class="' + dc + '"')
    for str_to_eliminate in strings_to_eliminate:
        line = line.replace(str_to_eliminate, '')
    return line


def generate_filecontent(source_file_path, dest_file):
    if not os.path.exists(source_file_path):
        return
    current_html_lines = []
    with open(source_file_path) as f:
        for line in f.readlines():
            current_html_lines.append(line)
    for display_class in DISPLAY_CLASSES:
        dest_file.write('\t\t\t<div class="' + display_class + '">\n')
        toc_lines = []
        content_lines = []
        write_tag_lines(toc_lines, content_lines, display_class, current_html_lines)
        for line in toc_lines:
            dest_file.write(filter_line_device_class(line))
        for line in content_lines:
            dest_file.write(filter_line_device_class(line))
        dest_file.write('\t\t\t</div>\n')


def write_tag_lines(toc_lines, content_lines, display_class, html_lines):
    current_hierarchy_level_lock = None
    for line in html_lines:
        if current_hierarchy_level_lock != None:
            line_hierarchy_level = get_line_hierarchy_level(line)
            if line_hierarchy_level != None and line_hierarchy_level <= current_hierarchy_level_lock:
                current_hierarchy_level_lock = None
            else:
                continue

        if is_line_blocking(display_class, line):
            current_hierarchy_level_lock = get_line_hierarchy_level(line)
            continue

        if is_toc_line(line):
            toc_lines.append(create_toc_line_source(display_class, line))
            content_lines.append(create_toc_line_dest(display_class, line))
        else:
            content_lines.append(line)


def get_line_hierarchy_level(line):
    for html_tag in HTML_TAGS_HIERARCHY_LEVELS:
        if ('<' + html_tag in line) or ('</' + html_tag + '>' in line):
            return HTML_TAGS_HIERARCHY_LEVELS[html_tag]
    return None


def is_line_blocking(display_class, line):
    if DISPLAY_CLASSES_PREFIX in line:
        if not display_class in line:
            return True
    return False


def is_toc_line(line):
    line_hierarchy_level = get_line_hierarchy_level(line)
    return line_hierarchy_level != None and line_hierarchy_level <= TOC_MAX_HIERARCHY_LEVEL


def create_toc_line_source(display_class, line):
    bold_text = False
    indented_text = True
    if '<h1' in line:
        bold_text = True
        indented_text = False
    tag_text_start_index = line.find('>') + 1
    tag_text_end_index = line.rfind('<')
    if tag_text_start_index < 1 or tag_text_end_index < tag_text_end_index:
        return line
    link_text = line[tag_text_start_index:tag_text_end_index]
    link_name = display_class + '_' + link_text.replace(' ', '_')
    res = link_text
    if bold_text:
        res = '<b>' + res + '</b>'
    if indented_text:
        atag = '<a style="display:inline-block; margin-left: 16px;" '
    else:
        atag = '<a style="display:inline-block;" '
    res = atag + 'href="#' + escape_link_name(link_name) + '">' + res + '</a><br>'
    return '\t\t\t\t' + res + '\n'


def create_toc_line_dest(display_class, line):
    tag_text_start_index = line.find('>') + 1
    tag_text_end_index = line.rfind('<')
    if tag_text_start_index < 1 or tag_text_end_index < tag_text_end_index:
        return line
    link_text = line[tag_text_start_index:tag_text_end_index]
    link_name = display_class + '_' + link_text.replace(' ', '_')
    return '\t\t\t\t<a name="' + escape_link_name(link_name) + '"></a>\n' + line


def escape_link_name(link_name):
    return re.sub('[^0-9a-zA-Z_]+', '', link_name)


if __name__ == "__main__":
    with open('../index.html', 'w') as f:
        copy_file_lines_to('./index_header.txt', f)
        generate_filecontent('./index_content.txt', f)
        copy_file_lines_to('./index_footer.txt', f)
