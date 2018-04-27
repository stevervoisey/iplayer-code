import mutagen
from mutagen.easyid3 import EasyID3
#class mutagen.mp4.MP4Info

from mutagen import Metadata
from mutagen._util import DictMixin, dict_match
from mutagen.mp4 import MP4, MP4Tags, error, delete
from mutagen.mp3 import MP3
####from mutagen.id3 import EasyID3


import os
import re
from datetime import datetime
import shutil

class TagSort(object):
    """A class to represent SETUP RTSP-transaction.


        TSSE    Lavf53.6.0
        TIT2    A Point of View: Will Self: A right loyal toast
        TALB    A Point of View
        TCON    Podcast,
        TPE1    BBC Radio 4

        fiction
        non-fiction
        music
        comedy

    """


    error = 0
    file_dict = {}
    file_list = []
    title_list = []
    duplicates = {}
    duplicates["album_title"] = {}
    duplicates["file_name"] = {}
    duplicate_files = {}
    album_title_dict = {}
    file_name_dict = {}


    def __init__(self,
                 ext,
                 file,
                 root):
        #  "": TagSort._regx,

        self.author_dict = {}
        self.category_dict = {}
        self.series_dict = {}
        self.filter_series_list = []

        self.found_author = False
        self.format = ext
        self.file = file
        self.root = root
        self.album = ""
        self.title = ""
        self.album_title = ""
        self.genre = ""
        self.text = ""
        self.folder = ""
        self.new_path_list = []
        self.new_file_path = ""

        self.file_duplicate = False

        self.album_title = ""


        self.process_file(file)
        self.build_folder()


    def add_path(self, path):
        path = re.sub(r'\s+', '_', path.lower())
        if path not in self.new_path_list:
            self.new_path_list.append(path)

    def build_folder(self):
        """
        genres:
        ['Drama', 'Factual', 'Readings', 'Music', 'Comedy', 'Podcast', 'Sport',
         'Magazines & Reviews', 'Religion & Ethics', 'Entertainment', 'Raymond Chandler']

          [ 'Music', 'Comedy', 'Podcast', 'Sport',
          'Entertainment', 'Raymond Chandler']
         fiction = ['Drama', 'Readings']
         thought = ['Factual', 'Magazines & Reviews', 'Religion & Ethics',]
        :return:
        """

        music_flag = False
        comedy_flag = False
        non_fiction_flag = False
        fiction_flag = False

        head, tail = os.path.split(self.root)

        self.folder = re.sub(r'[\s/]', '_', self.album)
        self.folder = re.sub(r'[:\(\)\'\,\?]', '', self.folder)

        if self.folder == "":
            match_obj = re.match(r'(.*)_-_', self.file)
            if match_obj:
                self.folder = match_obj.group(1) + "_NEW"
            else:
                self.folder = "UNKNOWN"
        # self.category_dict[genre_key] = True
        # self.filter_category_list.append(genre_key)

        
    def process_file(self, file):

        """
        if self.album_title not in TagSort.album_title_dict.keys():
            TagSort.album_title_dict[self.album_title] = os.path.join(self.root, self.file)
            TagSort.album_title_dict = { self.album_title: [ os.path.join(self.root, self.file)] }


        file_name_dict[file] -> /fullPath/file.mp3 String

        duplicates["file_name"][file]["original"]   -> /fullPath/file.mp3    String ( from file_name_dict[file] )
        duplicates["file_name"][file]["duplicates"] -> [/fullPath/file.mp3]  List
                                                       [/fullPath/file.mp3]
                                     ["album_title"] -> [self.album_title]
        """
        #log("xxx {}".format(self.album_title))
        self.file = file

        if self.file not in TagSort.file_name_dict.keys():
            TagSort.file_name_dict[self.file] = os.path.join(self.root, self.file)
        else:
            if self.file in TagSort.duplicates["file_name"]:
                if os.path.join(self.root, self.file) == TagSort.file_name_dict[self.file]:
                    log("ERROR: File duplicate processing, == original {}".format(os.path.join(self.root, self.file)))
                    TagSort.error += 1
                    return
                if os.path.join(self.root, self.file) in TagSort.duplicates["file_name"][self.file]['duplicates']:
                    log("ERROR: File duplicate processing, in duplicates {}".format(os.path.join(self.root, self.file)))
                    TagSort.error += 1
                    return
                TagSort.duplicates["file_name"][self.file]['duplicates'].append(os.path.join(self.root, self.file))
                TagSort.duplicates["file_name"][self.file]['album_title'].append(self.album_title)
            else:
                TagSort.duplicates["file_name"][self.file] = {
                    'duplicates': [os.path.join(self.root, self.file)],
                    'original': TagSort.file_name_dict[self.file],
                    'album_title': [self.album_title]
                }

            self.file_duplicate = True
        #return

        if file not in TagSort.file_list:
            TagSort.file_list.append(file)
        else:
            log("\nDUPLICATE!: {} {}".format(file, TagSort.file_dict[file]))


        if file not in TagSort.file_dict.keys():
            TagSort.file_dict[file] = self.album_title
        else:
            ### log("************ >>> duplicate  file  !!!!")
            self.file_duplicate = True
            if file not in TagSort.duplicate_files.keys():
                TagSort.duplicate_files[file] = {"album_title": [TagSort.file_dict[file]]}
                TagSort.duplicate_files[file]["album_title"].append(self.album_title)
            else:
                TagSort.duplicate_files[file]["album_title"].append(self.album_title)

            #log("File duplicate: [{}]".format(file))
        pass

        """
        if self.album_title not in TagSort.album_title_dict.keys():
            TagSort.album_title_dict[self.album_title] = os.path.join(self.root, self.file)
        else:
            if self.album_title in TagSort.duplicates["album_title"]:
                TagSort.duplicates["album_title"][self.album_title]['duplicates'].append(os.path.join(self.root, self.file))
            else:
                TagSort.duplicates["album_title"][self.album_title] = {
                    'duplicates': [os.path.join(self.root, self.file)],
                    'original': TagSort.album_title_dict[self.album_title]
                }

            self.album_title_duplicate = True
        """

    def process_album(self, this_tag):
        self.album = ""
        if self.format == "m4a":
            self.album = ",".join(this_tag)
        if self.format == "mp3":
            self.album = str(this_tag)

    def process_title(self, this_tag):
        self.title = ""
        self.album_title = ""
        if self.format == "m4a":
            self.title = ",".join(this_tag)
        if self.format == "mp3":
            self.title = str(this_tag)
        if self.album:
            if not self.album == self.title:
                self.album_title = "{} {}".format(self.album, self.title)
            else:
                self.album_title = self.title
        else:
            self.album_title = self.title

        """
        album_title_dict[album_title] -> /fullPath/file.mp3 String

        duplicates["album_title"][album_title]["original"]   -> /fullPath/file.mp3    String ( from album_title_dict[album_title] )
        duplicates["album_title"][album_title]["duplicates"] -> [/fullPath/file.mp3]  List
                                                                [/fullPath/file.mp3]
        """
        #log("title:  {}\nAtitle: {}".format(self.title, self.album_title))
        # Do we have an entry for current 'album_title' in 'album_title_dict'?

        if self.album_title not in TagSort.album_title_dict.keys():
            TagSort.album_title_dict[self.album_title] = os.path.join(self.root, self.file)
        else:
            if os.path.join(self.root, self.file) == TagSort.album_title_dict[self.album_title]:
                log("ERROR: Title duplicate processing, == original {}".format(os.path.join(self.root, self.file)))
                TagSort.error += 1
                return
            #log("duplicate album_title {}\n{}".format(self.album_title, os.path.join(self.root, self.file)))
            if self.album_title in TagSort.duplicates["album_title"]:
                TagSort.duplicates["album_title"][self.album_title]['duplicates'].append(os.path.join(self.root, self.file))
            else:
                TagSort.duplicates["album_title"][self.album_title] = {
                    'duplicates': [os.path.join(self.root, self.file)],
                    'original': TagSort.album_title_dict[self.album_title]
                }

            self.album_title_duplicate = True





def check_duplicate_album_title():
    tmp_duplicate_file_list = []
    for album_title in TagSort.duplicates["album_title"]:
        log("\ntitle: {}\nOriginal file:   {}".format(album_title,
                                                        TagSort.duplicates["album_title"][album_title]["original"]))
        for file in TagSort.duplicates["album_title"][album_title]["duplicates"]:
            log("Duplicate files: {}".format(file))
            # head, tail = os.path.split("/tmp/d/a.dat")
            head, tail = os.path.split(file)
            tmp_duplicate_file_list.append(tail)

def check_duplicate_files(move=False, log_size=False):
    log("\n\n")
    duplicate_folder = "F:\\DUPLICATES\\radio"
    duplicate_instances = 0
    duplicate_files = 0
    different_size_count = 0

    try:
        os.makedirs(duplicate_folder);  ## it creates the destination folder
    except:
        log("Folder already exists {}".format(duplicate_folder))

    for file_name in TagSort.duplicates["file_name"]:
        # if file_name not in tmp_duplicate_file_list:
        duplicate_instances += 1
        if 1:
            original_bytes = os.path.getsize(TagSort.duplicates["file_name"][file_name]["original"])
            if log_size:
                log("\nfile: {}\n{} Original path:   {}".format(file_name,
                                                                original_bytes,
                                                           TagSort.duplicates["file_name"][file_name]["original"]))
            else:
                log("\nfile: {}\nOriginal path:   {}".format(file_name,
                                                             TagSort.duplicates["file_name"][file_name]["original"]))

            same_size = True
            local_duplicate_files = -1
            for file in TagSort.duplicates["file_name"][file_name]["duplicates"]:
                duplicate_files += 1
                local_duplicate_files += 1
                duplicate_bytes = os.path.getsize(file)
                if log_size:
                    log("{} Duplicate files: {}".format(duplicate_bytes, file))
                else:
                    log("Duplicate files: {}".format(file))
                if not original_bytes == duplicate_bytes:
                    same_size = False
                    different_size_count +=1
                    log("Different size from original! {} {}".format(original_bytes, duplicate_bytes))
                else:
                    log("Same size {} {}".format(original_bytes, duplicate_bytes))
                #if move and same_size:
                if move:
                    head, tail = os.path.split(file)
                    #if local_duplicate_files > 0:
                    if not os.path.isfile("{}\\{}".format(duplicate_folder,tail)):
                        move_file(file, duplicate_folder)
                    else:

                        count = 0
                        copy_found = True
                        while copy_found:
                            count += 1
                            destination = "{}\\duplicate_{}_{}".format(duplicate_folder, count, tail)
                            if not os.path.isfile(destination):
                                copy_found = False
                                move_file(file, destination)






            for album_title in TagSort.duplicates["file_name"][file_name]["album_title"]:
                log("Album Title: {}".format(album_title))

    log("\nduplicate_instances {} duplicate_files {} check {} size diff {}".format(duplicate_instances,
                                                                            duplicate_files,
                                                                            len(TagSort.duplicates["file_name"]),
                                                                            different_size_count))


def log(message):
    print(message)
    out.write(message + "\n")
    
def move_file(file, destination):
    log("move {} to {}".format(file, destination))
    shutil.move(file, destination)
    ##### os.makedirs(os.path.dirname(destination), exist_ok=True)
    ##### shutil.copy(file, destination)

date_time_stamp = "_" + datetime.now().strftime("%Y-%m-%d-%H%M")
logfile = "duplicates_{}.log".format(date_time_stamp)

out = open(logfile,'w')
#media_root = "F:\\media\\iplayer\\radio\\current"
media_root = "C:\\iPlayer"
#pick_root  = "C:\\me\\iPlayer\\iPlayerPick"

xxsearch_list = [ "C:\\iplayer\\radio",
                "F:\\media\\iplayer\\radio\\current",
                "C:\\Users\\steve\\Desktop\\iPlayer Recordings",
                "C:\\iplayer\\radio",
               "E:\\me\\media\\VIDEO\\iPlayer",
               "E:\\me\\media\\sound\\Radio"]

search_list = [ "C:\\iplayer\\archive",
                "C:\\me\\iPlayer"]

xsearch_list = [media_root + "\\radio\\current"]

#search_list = ["C:\\me\\iPlayer"]

for location in search_list:
    for root, dirs, files in os.walk(location):
        for file in files:
            # log(os.path.join(root, file))
            log("\n\n================= {} ================".format(file))
            if file.endswith(".m4a"):
                x = TagSort(ext = "m4a", file=file, root=root)
                #x.build_folder()
                #x.display_title()
                #log("file: {}\ngenre: {}\nnew file path: {}".format(x.file, x.genre, x.new_file_path))
                #old_file = "{}".format(os.path.join(root, file))
                #new_file = "{}\\archive\\radio\\{}\\{}".format(media_root, x.new_file_path, x.file)

                #log("original: {}".format(old_file))
                #log("new:      {}".format(new_file))
                #move_file(old_file, new_file)

            if file.endswith("mp3"):
                x = TagSort(ext = "mp3", file=file, root=root)


#TagSort.duplicates["album_title"][self.album_title]['duplicates'].append(os.path.join(self.root, self.file))




        # head, tail = os.path.split("/tmp/d/a.dat")
        # head, tail = os.path.split(file)


# TagSort.duplicate_files[file] = {"album_title": [self.album_title]}

# TagSort.duplicates["album_title"][self.album_title]['duplicates']

        #   TagSort.duplicate_files[file]


#check_duplicate_album_title()

check_duplicate_files(move=True, log_size=True)
log("\n\n")
log("error: {}".format(TagSort.error))

 #d = MP4(os.path.join(root, file)).tags.get("genre", [None])[-1]
            #log(str(d))
            #log(tags.items())

            # if mp4map["genre"] in tags:
            #     log("tag {}".format(tags[mp4map["genre"]]))
                #log("file {} tags {}".format(file, tags['aART']))
                #if file.endswith(".m4a"):
                #    log("file: {}".format(file))


"""
for file in TagSort.duplicate_files:
    if file not in tmp_duplicate_file_list:
        log("\nExtra duplicate files: {}".format(file))
        for entry in TagSort.duplicate_files[file]["album_title"]:
            log("Album title: {}".format(entry))
"""