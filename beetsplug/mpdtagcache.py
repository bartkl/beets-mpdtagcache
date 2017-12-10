from beets.plugins import BeetsPlugin
from beets import config
from beets import util
from beets import library
from beets import logging
from beets import ui
import sqlite3
import os
import time

start_time = time.time()

class MPDTagCache(BeetsPlugin):
    def __init__(self):
        super(MPDTagCache, self).__init__()  # Avoid using ``super()`` to be
                                             # compatible with Python 2.
        self.mpd_music_directory = self.normpath(config['directory'].get())
        self.mpd_mtime = config['mpdtagcache']['mtime'].get()
        self.multiple_genres = config['mpdtagcache']['multiple_genres'].get()
        self.multiple_genre_delimiter = config['mpdtagcache']['multiple_genre_delimiter'].get()
        self.supported_audio_filetypes = tuple(config['mpdtagcache']['supported_audio_filetypes'].get())
        self.mpd_tagcache_file = self.normpath(config['mpdtagcache']['tagcache_file'].get())

    def normpath(self, path):
        return util.normpath(path).decode('utf8')


    def fetch_beets_db(self, lib):
        cache = dict()  # NOTE: ``OrderedDict`` worked, but the order of
                        # writing to the tag cache file is determined by
                        # the order in which the directories are traversed.
        with lib.transaction() as tx:
            cur = tx.db._connection().execute("""
                select
                    items.path,
                    items.length,
                    items.artist,
                    items.album,
                    albums.albumartist,
                    items.title,
                    items.track,
                    albums.genre,
                    albums.year,
                    items.disc,
                    items.composer,
                    items.arranger
                from items

                left join albums
                on items.album_id = albums.id
            """)
            for row in cur:
                cache[row['path']] = row
            cur.close()

            return cache


    def write_tag_cache_to_file(self):
        with open(self.mpd_tagcache_file, "w") as f:
            f.write(self.generate_tag_cache())


    def generate_tag_cache(self):
        info = ("info_begin\n"
                "format: 2\n"
                "mpd_version: 0.19.1\n"
                "fs_charset: UTF-8\n"
                "tag: Artist\n"
                "tag: ArtistSort\n"
                "tag: Album\n"
                "tag: AlbumSort\n"
                "tag: AlbumArtist\n"
                "tag: AlbumArtistSort\n"
                "tag: Title\n"
                "tag: Track\n"
                "tag: Name\n"
                "tag: Genre\n"
                "tag: Date\n"
                "tag: Composer\n"
                "tag: Performer\n"
                "tag: Disc\n"
                "tag: MUSICBRAINZ_ARTISTID\n"
                "tag: MUSICBRAINZ_ALBUMID\n"
                "tag: MUSICBRAINZ_ALBUMARTISTID\n"
                "tag: MUSICBRAINZ_TRACKID\n"
                "tag: MUSICBRAINZ_RELEASETRACKID\n"
                "info_end\n")
        contents = str()
        for dir_entry in os.scandir(self.mpd_music_directory):
            assert os.path.isdir(dir_entry.path), ("There are non-directory "
                                                  "files in the music library "
                                                  "directory. Please clean up.")
            contents += self.generate_directory_blocks(dir_entry)
        return info + contents


    def generate_directory_blocks(self, directory):
        assert directory.path.startswith(self.mpd_music_directory) and\
           not directory.path == self.mpd_music_directory, ("Please supply "
                                                      "subdirectories of the MPD "
                                                      "music directory {}.")\
                                                      .format(self.mpd_music_directory)
        directory_block = str()
        directory_relpath = directory.path.split(self.mpd_music_directory+os.path.sep)[1]
        directory_block = ("directory: {}\n".format(directory.name) +
                           "mtime: {:d}\n".format(self.mpd_mtime)   +
                           "begin: {}\n".format(directory_relpath))
        for dir_entry in os.scandir(directory.path):
            if dir_entry.is_dir():
                directory_block += self.generate_directory_blocks(dir_entry)
            elif dir_entry.path.lower().endswith(self.supported_audio_filetypes):
                try:
                    directory_block += self.generate_song_block(self.beets_db_cache[dir_entry.path.encode('utf8')])
                except KeyError:
                    raise ui.UserError(("File {} has no matching element in the "
                                    "Beets DB cache.").format(dir_entry.path))
        directory_block += "end: {0}\n".format(directory_relpath)
        return directory_block


    def generate_song_block(self, song):
        if self.multiple_genres:
            genres = filter(None, song['genre'].split(self.multiple_genre_delimiter))
            genre_lines = str()
            for genre in genres:
                genre_lines += "Genre: {0}\n".format(genre.strip())
            genre_lines = genre_lines.rstrip("\n")  # No newline for the last one.
            if not genre_lines:
                genre_lines += "Genre: "
        song_filename = os.path.basename(song['path'].decode('utf8'))
        song_block = ("song_begin: {}\n".format(song_filename)        +
                      "Time: {:.6f}\n".format(song['length'])         +
                      "Artist: {}\n".format(song['artist'])           +
                      "Album: {}\n".format(song['album'])             +
                      "AlbumArtist: {}\n".format(song['albumartist']) +
                      "Title: {}\n".format(song['title'])             +
                      "Track: {:02d}\n".format(song['track'])         +
                      "{}\n".format(genre_lines)                      +
                      "Date: {:4d}\n".format(song['year'])            +
                      "Disc: {:2d}\n".format(song['disc'])            +
                      "Composer: {}\n".format(song['composer'])       +
                      "Performer: {}\n".format(song['arranger'])      +
                      "mtime: {:d}\n".format(self.mpd_mtime)          +
                      "song_end\n")
        return song_block


    def generate_mpd_tagcache(self, lib, opts, args):
        self.beets_db_cache = self.fetch_beets_db(lib)
        self._log.info("Writing MPD tag cache to {} ...".format(self.mpd_tagcache_file))
        self.write_tag_cache_to_file()
        end_time = time.time()
        self._log.info(("\nDone.\n"
              "Execution took {:.6f} seconds.").format(end_time - start_time))

    def commands(self):
        mpdtagcache_cmd = ui.Subcommand('mpdtagcache', help='generate mpd tagcache')
        mpdtagcache_cmd.func = self.generate_mpd_tagcache
        return [mpdtagcache_cmd]
