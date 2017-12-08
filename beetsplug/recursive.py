import os
import sys

MPD_MUSIC_DIRECTORY = os.path.normpath('/media/nastynas/music/library-test')


def generate_directory_blocks(directory_path,\
                              directory_filter=lambda d: d,\
                              song_filter=lambda s: not s.endswith('.jpg')):
    directory_block = str()

    if not directory_path == MPD_MUSIC_DIRECTORY:
        directory_block += "directory: {0}\n".format(
                                            os.path.basename(directory_path))
        directory_block += "mtime: 0\n"
        directory_block += "begin: {0}\n".format(directory_path.split(
                                            MPD_MUSIC_DIRECTORY)[1].\
                                            lstrip(os.path.sep))
    for dir_entry in filter(directory_filter, os.scandir(directory_path)):
        if dir_entry.is_dir():
            directory_block += generate_directory_blocks(dir_entry.path)
        else:
            if song_filter(dir_entry.path):
                directory_block += generate_song_block(dir_entry.path)

    directory_block += "end: {0}\n".format(directory_path.split(
                                      MPD_MUSIC_DIRECTORY)[1].\
                                      lstrip(os.path.sep))

    return directory_block


def generate_song_block(song_path):

    song_block = str()
    song_block += "song_begin: {0}\n".format(os.path.basename(song_path))
    song_block += "field: {0}\n".format("Test")
    song_block += "song_end\n"

    return song_block
    

if __name__ == "__main__":
    print(
        generate_directory_blocks(MPD_MUSIC_DIRECTORY)
    )
