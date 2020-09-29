# beets-mpdtagcache
Plugin for beets that generates a MPD tag cache file from the beets library database.

This enables MPD tag caching sourced from the beets library database instead of from the audio file tags.

## Motivation
Reasons why this could be desired include:

* It is elegant and practical to have a single, central location where the metadata is stored and maintained. The beets database is an ideal choice, since beets is already a favorable library maintenance tool.
* Sometimes it's preferred to not have the audio files touched, since changing them can result in them no longer being identified by other applications which expect them to have certain contents or a specific checksum.

## Installation
_TODO_.

## How to use
_TODO_.

_Tip_: The plugin outputs the generated MPD tag cache to absolute path provided in the `tagcache_file` setting. It is advised to not make this point to the actual MPD tag cache in use by the daemon, but to copy by hand or script after generation.

## Caveats
* The biggest issue is that as soon as you or some of your MPD clients triggers a database reload, this will regenerate the tag cache using the original audio file tags source. This means that to use this solution stably, you must make sure such a reload never gets triggered.
	- This sounds like a major limitation/issue, but I have easily worked around it for the last few years. The clients I used were ncmpcpp, mpc, and MPDroid.
	- Newer versions of MPD have automatic database updating based on file changes. Because of this limitation, you sadly won't be able to use that.
* The format of the generated tagcache file is not based on any technical specification, but on my reverse engineering of what the file's structure is like. This is not ideal, but I have been using this script for some years now, and it is has never generated a corrupt or faulty file.
* This plugin has been created for personal use only and possibly needs work to perform on other devices and installations.
