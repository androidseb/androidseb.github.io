import os

DISPLAY_CLASSES_PREFIX = 'class="devices_'
DISPLAY_CLASSES = [
    'devices_android',
    'devices_ios',
    'devices_web',
]
HTML_TOC_TAGS = ['h1', 'h2']
HTML_TAGS_HIERARCHY_ROOT = {
    'root': {
        'h1': {
            'h2': {
                'p': None,
                'ul': {'li': None},
                'ol': {'li': None},
            },
            'p': None,
            'ul': {'li': None},
            'ol': {'li': None},
        }
    }
}


def copy_file_lines_to(source_file_path, dest_file):
    if not os.path.exists(source_file_path):
        return
    with open(source_file_path) as f:
        for line in f.readlines():
            dest_file.write(line)


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
        write_tag_lines(toc_lines, content_lines, display_class, current_html_lines, HTML_TAGS_HIERARCHY_ROOT, 'root')
        for line in toc_lines:
            dest_file.write(line)
        for line in content_lines:
            dest_file.write(line)
        dest_file.write('\t\t\t</div>\n')


def write_tag_lines(toc_lines, content_lines, display_class, current_html_lines, current_html_hierarchy, current_html_key):
    if len(current_html_lines) == 0:
        return

    if current_html_key == None or current_html_hierarchy[current_html_key] == None:
        for line in current_html_lines:
            if is_toc_line(line):
                toc_lines.append(create_toc_line_source(display_class, line))
                content_lines.append(create_toc_line_dest(display_class, line))
            else:
                content_lines.append(line)
        return

    current_html_hierarchy = current_html_hierarchy[current_html_key]

    current_tag_children_names = []
    for child_name in current_html_hierarchy:
        current_tag_children_names.append(child_name)

    current_child_name = get_matching_child_name_for_line(current_tag_children_names, current_html_lines[0])
    current_child_lines = []
    currently_blocked_child_name = None

    for line in current_html_lines:
        matching_child_name = get_matching_child_name_for_line(current_tag_children_names, line)
        if currently_blocked_child_name != None:
            if matching_child_name != currently_blocked_child_name:
                continue
            else:
                currently_blocked_child_name = None
        if DISPLAY_CLASSES_PREFIX in line:
            if not display_class in line:
                currently_blocked_child_name = matching_child_name
                continue
        if matching_child_name != current_child_name and matching_child_name in current_tag_children_names:
            html_key = current_child_name
            if html_key == None:
                html_key = matching_child_name
            write_tag_lines(toc_lines, content_lines, display_class, current_child_lines, current_html_hierarchy, html_key)
            current_child_lines = []
            current_child_name = matching_child_name
        current_child_lines.append(line)
    write_tag_lines(toc_lines, content_lines, display_class, current_child_lines, current_html_hierarchy, current_child_name)


def is_toc_line(line):
    for tog_tag in HTML_TOC_TAGS:
        if '<' + tog_tag in line:
            return True
    return False


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
    res = '<a href="#' + link_name + '">' + res + '</a><br>'
    if indented_text:
        res = '&nbsp&nbsp&nbsp' + res
    return res


def create_toc_line_dest(display_class, line):
    tag_text_start_index = line.find('>') + 1
    tag_text_end_index = line.rfind('<')
    if tag_text_start_index < 1 or tag_text_end_index < tag_text_end_index:
        return line
    link_text = line[tag_text_start_index:tag_text_end_index]
    link_name = display_class + '_' + link_text.replace(' ', '_')
    return '<a name="' + link_name + '"></a>' + line


def get_matching_child_name_for_line(child_names_list, line):
    matching_child_name = None
    for child_name in child_names_list:
        if '<' + child_name in line:
            matching_child_name = child_name
            break
    return matching_child_name


if __name__ == "__main__":
    with open('../index.html', 'w') as f:
        copy_file_lines_to('./index_header.txt', f)
        generate_filecontent('./index_content.txt', f)
        copy_file_lines_to('./index_footer.txt', f)
