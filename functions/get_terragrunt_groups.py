import re

def get_terragrunt_groups(terragrunt_input_file):
    
    with open(terragrunt_input_file, 'r') as file:
        file_content = file.read()

    groups = {}
    current_group = None

    for line in file_content.split('\n'):
        if "Group " in line:
            current_group = line.split(" ")[1]
            groups[current_group] = []
        elif "- Module " in line:
            module_path = re.search(r'- Module (.+)', line).group(1).strip()
            groups[current_group].append(module_path)

    return groups