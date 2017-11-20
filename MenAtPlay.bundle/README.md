# MenAtPlay.bundle

## Description

Plex metadata agent for fetching metadata for Men At Play scenes.

Only limited metadata is available on their free access website and no posters.

By default, this matcher expects files to be named either:

* `MAP - {title}`
* `MenAtPlay - {title}`
* `Men At Play - {title}`

Spaces around the dashes are optional, as is the MAP before the title. This is configurable in the agent settings.

By default, this matcher only runs on items in a directory named "Men At Play".
This is configurable in the agent settings.

## Installation

Copy CockPorn.bundle and MenAtPlay.bundle to the Plex plugins path. See
[How do I find the Plug-Ins folder?][1] for more information.

## Known Issues

- Limited ability to match titles with special characters in the name.

[1]: https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-
