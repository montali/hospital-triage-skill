from os.path import isfile, join
import googletrans
import sys
import os


translator = googletrans.Translator()
def_file_src = "it-it"
def_file_dest = "en-us"
def_gtrans = "en"


def translate_file(file, source_file_locale=def_file_src, dest_file_locale=def_file_dest, dest_gtrans=def_gtrans):
    with open(file, "r") as source_file:
        new_file_path = file.replace(source_file_locale, dest_file_locale)
        with open(new_file_path, "w+") as dest_file:
            i = 0
            for phrase in source_file:
                dest_file.write(translator.translate(
                    phrase, dest_gtrans).text+"\n")
    print("Translated "+file+" ✨")


def dir_explorer(path):
    for file in os.listdir(path):
        full_path = join(path, file)
        if isfile(full_path):
            translate_file(full_path)
        else:
            dir_explorer(full_path)


if __name__ == '__main__':
    try:
        if not os.path.exists(sys.argv[1]):
            raise FileNotFoundError
        def_file_src = sys.argv[2]
        def_file_dest = sys.argv[3]
        def_gtrans = sys.argv[4]
    except IndexError:
        print(
            "Please insert the dir and the language codes.\nUSAGE: python3 string_translate [dir] [src-locale-code] [dest-locale-code] [gtrans-dest-code]")
    dir_explorer(sys.argv[1])
