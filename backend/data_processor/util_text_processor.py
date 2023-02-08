import os


def get_text_filenames():
    text_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    return text_files

def write_cleaned_file(source):
    name, ext = os.path.splitext(source)
    dest = name + "_" + "clean." + ext

    with open(os.path.join(directory, source), 'r', encoding='utf-8') as file:
        contents = file.read()

    contents = ' '.join(contents.split())
    contents = contents.encode(encoding='ASCII',errors='ignore').decode()

    with open(os.path.join(directory, dest), 'w') as new_file:
        new_file.write(contents)

directory = 'inputs'
file_list = get_text_filenames()
for file in file_list:
    print(file)
    write_cleaned_file(file)


