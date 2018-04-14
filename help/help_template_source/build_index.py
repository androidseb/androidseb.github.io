import os

DISPLAY_CLASSES_PREFIX = 'class="devices_'
DISPLAY_CLASSES = [
    'devices_android',
    'devices_ios',
    'devices_web',
]
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
        write_tag_lines(dest_file, display_class, current_html_lines, HTML_TAGS_HIERARCHY_ROOT, 'root')
        dest_file.write('\t\t\t</div>\n')


def write_tag_lines(dest_file, display_class, current_html_lines, current_html_hierarchy, current_html_key):
    if len(current_html_lines) == 0:
        return

    if current_html_key == None or current_html_hierarchy[current_html_key] == None:
        for line in current_html_lines:
            dest_file.write(line)
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
            write_tag_lines(dest_file, display_class, current_child_lines, current_html_hierarchy, html_key)
            current_child_lines = []
            current_child_name = matching_child_name
        current_child_lines.append(line)
    write_tag_lines(dest_file, display_class, current_child_lines, current_html_hierarchy, current_child_name)


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
