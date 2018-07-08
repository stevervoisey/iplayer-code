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

"""

‘\xa9nam’ – track title
‘\xa9alb’ – album
‘\xa9ART’ – artist
‘aART’ – album artist
‘\xa9wrt’ – composer
‘\xa9day’ – year
‘\xa9cmt’ – comment
‘desc’ – description (usually used in podcasts)

‘\xa9grp’ – grouping
‘\xa9gen’ – genre
‘\xa9lyr’ – lyrics


"""

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

    tag_map = {"m4a": {
        "album": "\xa9alb",  # album
        "title": "\xa9nam",  # track title
        "artist": "\xa9ART",  # artist
        "album artist": "aART",  # album artist
        "composer": "\xa9wrt",  # composer
        "year": "\xa9day",  # year
        "comment": "\xa9cmt",  # comment
        "description": "desc",  # description (usually used in podcasts)
        "grouping": "\xa9grp",  # grouping
        "genre": "\xa9gen",  # genre
        "lyrics": "\xa9lyr"  # lyrics
    },
        "mp3": {
            "album": "TALB",  # title brief
            "title": "TIT2",  # track title
            # "album":        "\xa9alb" , # album
            "artist": "TPE1",  # artist
            # "album artist": "aART" , # album artist
            # "composer":     "\xa9wrt" , # composer
            "year": "TDRC",  # year
            "comment": "COMM::eng",  # comment
            # "description":  "desc" , # description (usually used in podcasts)
            # "grouping":     "\xa9grp" , # grouping
            "genre": "TCON",  # genre
            # "lyrics":       "\xa9lyr"  # lyrics
        }
    }

    file_dict  = {}
    file_list  = []
    title_list = []
    master_genre_list  = []
    album_title_dict = {}
    file_name_dict = {}

    #duplicates["album_title": ''][]["original"] = ""
    #duplicates["album_title"][]["duplicates"] = []

    error = 0
    duplicates = {}
    duplicates["album_title"] = {}
    duplicates["file_name"] = {}
    duplicate_files = {}

    episode_regx = re.compile('^\s*Episode\s*(\d*)\s*$')

    ####dummy_match = "NO MATCH REQUIRED"
    filter_author = {
        "armistead maupin": re.compile('armistead'),
        "agatha christie": re.compile('agatha.*christie|marple|poirot'),
        "boothby graffoe": re.compile('big[\s_]booth'),
        "brian aldiss": re.compile('brian[\s_]aldiss'),
        "chris morris": re.compile('chris[\s_]morris|blue[\s_]jam|day[\s_]today'),
        "david sedaris": re.compile('sedaris'),
        "dominic_holland": False,
        "graham greene": re.compile('greene|harry[\s_]lime'),
        "ian d montfort": False,
        "ian flemming": re.compile('james[\s_]bond'),
        "ian rankin": re.compile('rebus'),
        "james acaster": False,
        "jeremy hardy": False,
        "john le carre": re.compile('le[\s_]carre|delicate.*truth|john[\s_]smiley'),
        "john finimore": re.compile('cabin[\s_]pressure'),
        "john hegley": False,                                # re.compile('hegley'),
        "john mortimer": re.compile('rumpole'),
        "john peel": False,                            # re.compile('john[\s_]peel'),
        "mark watson": False,
        "neil innes": False,
        "neil gaiman": re.compile('neverwhere'),
        "phillip k dick": re.compile('k[\s_]dick'),
        "raymond chandler": re.compile('philip[\s_]marlowe'),
        "ruth rendell": re.compile('rendell'),
        "robert barr": re.compile('robert[\s_]barr'),
        "sean lock": False,
        "sebastian baczkiewicz": re.compile('pilgrim'),
        "simon evans": False,
        "stanislaw lem": re.compile('solaris'),
        "terry pratchett": re.compile('pratchett'),
        "val mcdermid": False,
        "wally k daly": False,
        "william gibson": re.compile('william[\s_]gibson'),
        "will self": re.compile('will[\s_]self')
    }

    crime_pattern = "sherlock|holmes|christie|marple|poirot|rebus|rumpole|robert.*barr|detective|chandler|marlowe|" + \
                    "julie[\s_]enfield|mclevy|gwen[\s_]danbury|inspector|silk[\s_]the[\s_]clerks|detective" + \
                    "inspector|the[\s_]interrogation|father[\s_]brown|mcdermid|murder|stone|falco|rendell"

    sci_fi_pattern = "torchwood|k[\s_]dick|alien|spaceship|triffid|dr who|stanislaw[\s_]lem|ray[\s_]bradbury|jules[\s_]|" + \
                     "verne|william[\s_]gibson"

    filter_category = {
        "classic": re.compile('sherlock|holmes|agatha[\s_]christie|marple|poirot|father[\s_]brown|jules[\s_]verne'),
        "comedy": re.compile('comedy|comic|funny|hilarious'),
        "crime": re.compile(crime_pattern),
        "dangerous visions": re.compile('dangerous[\s_]visions'),
        "drama": re.compile('drama'),
        "economics": re.compile('economics'),
        "entertainment": re.compile('entertainment'),
        "ethic": re.compile('ethic'),
        "europe": re.compile('italy|france|sweden|scandinavian|foreign[\s_]bodies'),
        "factual": re.compile('factual'),
        "fantasy": re.compile('fantasy|pratchett|sebastian[\s_]baczkiewicz|pilgrim|gaiman|titus|heart[\s_]of[\s_]harkun'),
        "horror": re.compile('haunted|supernatural|horror'),
        "law": re.compile('law'),
        "magazine": re.compile('magazine'),
        "music": re.compile('john[\s_]peel'),
        "politics": re.compile('politics'),
        "philosophy": re.compile('philosophy'),
        "psychology": re.compile('psychology'),
        "reading": re.compile('reading'),
        "religion": re.compile('catholic|protestant|islam|buddist'),
        "review": re.compile('review|file[\s_]review|film[\s_]program|front[\s_]row'),
        "sci-fi": re.compile(sci_fi_pattern),
        "sport": re.compile('sport'),
        "spy": re.compile('graham[\s_]greene|james[\s_]bond|carre|smiley'),
        "thought": re.compile('thought'),
        "trump": re.compile('trump'),
        "thriller": re.compile('thriller')
    }

    filter_series = {
        "15 minute drama": False,
        "book of the week": False,
        "book at bedtime": False,
        "afternoon drama": False,
        "clare in the community": False,
        "di gwen danbury": False,
        "falco": False,
        "julie enfield": False,
        "ladies detective agency": False,
        "mclevy": False,
        "news quiz": False,
        "the silent world": False
    }

    filter_ignore = {
        "comedy": re.compile('politics|law|thought|crime'),
        "drama": re.compile('politics|law|thought')
    }
    def __init__(self,
                 ext,
                 file,
                 root):
        #  "": TagSort._regx,

        self.ignore = False
        self.author_dict = {}
        self.category_dict = {}
        self.series_dict = {}
        self.filter_series_list = []

        self.add_path_drama = False

        for key in TagSort.filter_author.keys():
            self.author_dict[key] = False

        for key in TagSort.filter_category.keys():
            self.category_dict[key] = False

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

        # Standard genres
        self.genre_dict  = {
            "comedy": False,
            "drama": False,
            "entertainment": False,
            "ethic": False,
            "factual":  False,
            "magazine": False,
            "music": False,
            "reading":  False,
            "religion": False,
            "review": False,
            "sport":  False,
        }
        self.genre_list = []

        self.filter_category_list = []

        ####self.sub_author_list = []
        # tailored genres

        self.fiction_genre_list = ['drama', 'comedy']
        self.thought_genre_list = ['factual', 'magazines & reviews', 'religion & ethics', ]
        self.music_genre_list   = ['music']
        self.comedy_genre_list  = ['comedy']

        #log("\n {} file: {}".format(ext, file))
        if ext == "m4a":
            tags = MP4(os.path.join(root, file))
        elif ext == "mp3":
            tags = MP3(os.path.join(root, file))
        else:
            log("ERROR: Invalid file extension!")
            return

        self.process_file_name(file)
        # Use tag_map to resove tag name for any file 'ext' [ mp3|m4a ]
        # check current file for each tag in our map
        for tag in TagSort.tag_map[ext].keys():
            if TagSort.tag_map[ext][tag] in tags:
                this_tag = tags[TagSort.tag_map[ext][tag]]
                if tag == "genre":
                    self.process_genre(this_tag)
                if tag == "title":
                    self.process_title(this_tag)
                if tag == "album":
                    self.process_album(this_tag)
                if tag == "lyrics":
                    #self.process_text(this_tag, "lyrics")
                    pass
                if tag == "comment":
                    self.process_text(this_tag, "comment")

        self.process_file(file)
        self.build_folder()

    def look_up_filter_series(self, text):
        text = text.lower()
        for series_key in TagSort.filter_series.keys():
            series_pattern = re.sub(r'\s+', '[\s_]*', series_key.lower())
            if re.search(series_pattern, text):
                log("series: match [{}]".format(series_key))
                self.series_dict[series_key] = True
                self.filter_series_list.append(series_key)
            if TagSort.filter_series[series_key]:
                if TagSort.filter_series[series_key] and TagSort.filter_series[series_key].search(text):
                    if series_key not in self.filter_series_list:
                        self.filter_series_list.append(series_key)


    def look_up_filter_category(self, text):
        text = text.lower()
        #for genre_key in self.category_dict.keys():
        for genre_key in TagSort.filter_category.keys():
            genre_pattern = re.sub(r'\s+', '[\s_]*', genre_key.lower())
            if re.search(genre_pattern, text):
                log("sub genre: match [{}]".format(genre_key))
                self.category_dict[genre_key] = True
                self.filter_category_list.append(genre_key)

        for item in TagSort.filter_category.keys():
            if TagSort.filter_category[item].search(text.lower()):
                self.category_dict[item] = True
                log("OK: search: look_up_filter_category: {} match: {}".format(item, self.text.lower()))
            if TagSort.filter_category[item].match(text.lower()):
                self.category_dict[item] = True
                log("OK: match: look_up_filter_category: {} match: {}".format(item, self.text.lower()))

    def look_up_author(self, text):
        text = text.rstrip()
        text = text.lower()
        for author_key in self.author_dict.keys():
            author_pattern = re.sub(r'\s+', '[\s_]*', author_key.lower())
            if re.search(author_pattern, text):
                log("OK: author: match 01 [{}] [{}]".format(author_key, author_pattern))
                self.author_dict[author_key] = True

        for item in TagSort.filter_author.keys():
            if TagSort.filter_author[item] and TagSort.filter_author[item].search(text):
                self.author_dict[item] = True
                log("OK: author: match 02 {} match: {}".format(item, text))


    def display_title(self):
        """
        self.format = ext
        self.file = file
        self.root = root
        self.album = ""
        self.title = ""
        self.album_title = ""
        self.genre = ""
        self.text = ""
        """

        head, tail = os.path.split(self.root)

        if not tail == self.folder:
        #if 1:
            message = "folder orig: [{}]\nfolder new:  [{}]\n\n".format(tail, self.folder)
            log(message)
            message = "\nroot: [{}] file: [{}]".format(
                self.root,
                self.file)
            log(message)
            message = "title: [{}] album: [{}] album_title: [{}]\ngenre: [{}]\ntext: [{}]".format(
                self.title,
                self.album,
                self.album_title,
                self.genre,
                self.text)
            log(message)

    def is_comedy(self):
        if self.genre.lower() in self.comedy_genre_list:
            return True
        if self.category_dict["comedy"]:
            return True
        return False

    def is_music(self):
        if self.genre.lower() in self.music_genre_list:
            return True
        return False

    def is_thought(self):
        thought = False
        if self.genre.lower() in self.thought_genre_list:
            thought = True

        if self.category_dict["ethic"] or \
            self.category_dict["factual"] or \
            self.category_dict["religion"] or \
            self.category_dict["politics"] or \
            self.category_dict["philosophy"] or \
            self.category_dict["psychology"] or \
            self.category_dict["economics"] or \
            self.category_dict["law"]:
            thought = True
        return thought

    def is_non_fiction(self):
        non_fiction = False

        if self.genre.lower() in self.music_genre_list:
            return False

        if self.genre.lower() in self.fiction_genre_list:
            return False

        if self.category_dict["music"] or \
            self.category_dict["drama"] or \
            self.category_dict["comedy"]:
            return False

        if self.is_thought():
            return True

        return non_fiction

    def add_path(self, path):
        path = re.sub(r'\s+', '_', path.lower())
        # Only add a path that contains drama once.
        #if "drama" in path.lower():
        #    if self.add_path_drama:
        #        return
        #    else:
        #        self.add_path_drama = True

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
        self.ignore_category = False

        head, tail = os.path.split(self.root)

        self.folder = re.sub(r'[\s/]', '_', self.album)
        self.folder = re.sub(r'[:\(\)\'\,\?]', '', self.folder)

        if self.folder == "":
            match_obj = re.match(r'(.*)_-_', self.file)
            if match_obj:
                #self.folder = match_obj.group(1) + "_NEW"
                self.folder = match_obj.group(1)
            else:
                self.folder = "UNKNOWN"
        # self.category_dict[genre_key] = True
        # self.filter_category_list.append(genre_key)

        if self.category_dict["review"]:
             self.add_path("review")
             self.ignore_category = True
        elif self.is_music():
            self.add_path("music")
            music_flag = True
        elif self.is_comedy():
            self.add_path("comedy")
            comedy_flag = True
        elif self.is_non_fiction():
            self.add_path("non_fiction")
            non_fiction_flag = True
        else:
            self.add_path("fiction")
            fiction_flag = True

        if self.is_thought() and not self.ignore_category:
            self.add_path("thought")

        if non_fiction_flag:
            self.genre_dict["drama"] = False
            self.genre_dict["comedy"] = False

        if fiction_flag:
            self.genre_dict["thought"] = False
            self.genre_dict["factual"] = False
            self.genre_dict["politics"] = False
            if not self.ignore_category:
                #if "drama" in self.genre_dict.keys() or "Drama" in self.genre_dict.keys() or self.genre_dict["drama"]:
                if "drama" in self.genre_dict.keys() or self.genre_dict["drama"]:
                    self.add_path("drama")

        if not self.ignore_category:
            for genre_key in self.genre_dict:
                if self.genre_dict[genre_key]:
                    self.add_path(genre_key)


                # def check_drama_type(self, text):
        #if self.category_dict["15 minute drama"] or self.filter_category["15 minute drama"]:
        #    self.add_path("15_minute_drama")
        #if self.category_dict["book of the week"] or self.filter_category["book of the week"]:
        #    self.add_path("book_of_the_week")
        #if self.category_dict["book at bedtime"] or self.filter_category["book at bedtime"]:
        #    self.add_path("book_at_bedtime")

        """
        if self.category_dict["15 minute drama"]:
            self.add_path("15_minute_drama")
        if self.category_dict["book of the week"]:
            self.add_path("book_of_the_week")
        if self.category_dict["book at bedtime"]:
            self.add_path("book_at_bedtime")
        """

        if self.category_dict["trump"]:
             self.add_path("politics")

        for series_key in self.series_dict:
            if self.series_dict[series_key]:
                self.add_path(re.sub(r'[\s]+', '_', series_key))

        if not self.ignore_category:
            for filter_category_key in self.category_dict:
                if filter_category_key not in self.genre_dict.keys() or not self.genre_dict[filter_category_key]:
                    if self.category_dict[filter_category_key]:
                        #if comedy_flag and filter_category_key in self.comedy_ignore:
                        #   next
                        self.add_path(filter_category_key)

        for author_key in self.author_dict:
            if self.author_dict[author_key]:
                # Only want one author
                if not self.found_author:
                    self.add_path(re.sub(r'[\s]+', '_', author_key))
                    # self.found_author = True

        self.process_ignore()
        self.add_path(self.folder)
        self.new_file_path = "\\".join(self.new_path_list)
        log("buid new path: {}".format(self.new_file_path))
        
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

        if TagSort.episode_regx.match(self.title):
            pass
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

    def process_genre(self, this_tag):
        # m4a return a list of genres, so need to convert to a string.
        # example: tag genre type <class 'list'> -> ['Readings']

        if self.format == "m4a":
            self.genre = ",".join(this_tag)
            #log("genre: {}".format(self.genre))
        if self.format == "mp3":
            #log("title: {}".format(self.title))
            # mp3 returns a mutagen object, but str() will extract the string value we need.
            # example: type <class 'mutagen.id3.TCON'> -> Podcast
            #                TCON(encoding=<Encoding.UTF16: 1>, text=['Podcast'])
            # log("type: {}".format(type(this_tag.genres)))
            # Appears to be a list but really not sure if there will ever be more than one.
            # But just in case...
            if len(this_tag.genres) > 1:
                log("multiple genres {}".format(this_tag.genres))
                self.genre = ",".join(this_tag.genres)
            else:
                self.genre = this_tag.genres[0]

        for genre_key in self.genre_dict.keys():
            if genre_key in self.genre.lower():
                log("genre: match [{}]".format(genre_key))
                self.genre_dict[genre_key] = True
                self.genre_list.append(genre_key)

        # Build a list of distinct genres
        if not self.genre in TagSort.master_genre_list :
            # TagSort.genre_dict .append(this_tag_string)
            TagSort.master_genre_list.append(self.genre)
        #

    def process_file_name(self, file, type=None):
        # Check duplication with process_text!!!!

        self.look_up_filter_series(self.file.lower())
        self.look_up_filter_category(self.file.lower())
        self.look_up_author(self.file.lower())

    def process_text(self, this_tag,type=None):
        if self.format == "m4a":
            self.text = ",".join(this_tag)
            log("text: {}".format(self.text.lower()))
            log("file: {}".format(self.file.lower()))

            #self.lyric = this_tag

            ###self.look_up_filter_category(self.file.lower())
            self.look_up_filter_series(self.file.lower())
            self.look_up_filter_category(self.text.lower())

            ###self.look_up_author(self.file.lower())
            self.look_up_author(self.text.lower())

        if self.format == "mp3":
            pass

    def process_ignore(self):
        for ignore_key in self.filter_ignore.keys():
            if ignore_key in self.category_dict.keys():
                self.category_dict[ignore_key] = False



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
    duplicate_folder = "C:\\me\\DUPLICATES"
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
                if move and same_size:
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
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.move(file, destination)
    #os.makedirs(os.path.dirname(destination), exist_ok=True)
    #shutil.copy(file, destination)

media_root = "C:\\iplayer"
#media_root = "F:\\sort"

code_root = "C:\\iplayer_code"
log_root = media_root + "\\logs"
date_time_stamp = "_" + datetime.now().strftime("%Y-%m-%d-%H%M")
logfile = "{}\\metasort_{}.log".format(log_root, date_time_stamp)

out = open(logfile,'w')
#media_root = "F:\\media\\iplayer\\radio\\current"

#pick_root  = "C:\\me\\iPlayer\\iPlayerPick"

xxsearch_list = [ "C:\\Users\\steve\\Desktop\\iPlayer Recordings",
               # "C:\\Users\\steve\\Desktop\\iPlayer-Tv",
               "E:\\me\\media\\VIDEO\\iPlayer",
               "E:\\me\\media\\sound\\Radio"]

xxxx1search_list = [media_root + "\\radio\\current"]

xsearch_list = [media_root + "\\x1archive"]

search_list = [ "G:\\iplayer\\radio" ]
#search_list = [ "F:\\remainingFromHomeLaptop\\iPlayer"]
#search_list = [ "C:\\me\\iPlayer"]
#search_list = ["C:\\me\\iPlayer"]

for location in search_list:
    for root, dirs, files in os.walk(location):
        for file in files:
            # log(os.path.join(root, file))
            log("\n\n================= {} ================\n{}\n".format(file, root))
            if file.endswith(".m4a"):
                x = TagSort(ext = "m4a", file=file, root=root)
                #x.build_folder()
                #x.display_title()
                #log("file: {}\ngenre: {}\nnew file path: {}".format(x.file, x.genre, x.new_file_path))
                old_file = "{}".format(os.path.join(root, file))
                new_file = "{}\\archive\\radio\\{}\\{}".format(media_root, x.new_file_path, x.file)

                log("original: {}".format(old_file))
                log("new:      {}".format(new_file))
                move_file(old_file, new_file)

            if file.endswith("mp3"):
                x = TagSort(ext = "mp3", file=file, root=root)


#TagSort.duplicates["album_title"][self.album_title]['duplicates'].append(os.path.join(self.root, self.file))




        # head, tail = os.path.split("/tmp/d/a.dat")
        # head, tail = os.path.split(file)


# TagSort.duplicate_files[file] = {"album_title": [self.album_title]}

# TagSort.duplicates["album_title"][self.album_title]['duplicates']

        #   TagSort.duplicate_files[file]


#check_duplicate_album_title()

check_duplicate_files(move=False, log_size=True)
log("\n\n")
log("genres: {}".format(TagSort.master_genre_list))
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