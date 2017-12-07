# beets-mpdtagcache
Plugin for beets that generates a MPD tag cache file from the beets library database.

Providing MPD with tag caching sourced from the beets library database instead of from the audio file tags.
Reasons why this could be desired include:

1. It is elegant and practical to have a single, central location where the metadata is stored and maintained. The beets database is an ideal choice, since beets is already a favorable library maintenance tool.
2. Sometimes it's preferred to not have the audio files touched, since changing them can result in them no longer being identified by other applications which expect them to have certain contents or a specific checksm.

The plugin outputs the generated MPD tag cache to absolute path provided in the `tagcache_file` setting. It is advised to not make this point to the actual MPD tag cache in use by the daemon, but to copy by hand or script after generation.

*WARNING*: This plugin has been created for my personal use and is possibly of poor quality. The format of the tag cache file I have determined using reverse engineering, and the plugin is not very thoroughly tested.
