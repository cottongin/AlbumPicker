###
# Copyright (c) 2022, cottongin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import random

from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('AlbumPicker')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class AlbumPicker(callbacks.Plugin):
    """AlbumPicker"""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(AlbumPicker, self)
        self.__parent.__init__(irc)
        self.current_albums = {}

    def die(self):
        del self.current_albums
        super().die()

    # TODO sanity check input
    @wrap([optional("text")])
    def loadchanger(self, irc, msg, args, albums):
        """Load up the disc changer"""
        if self.current_albums:
            irc.reply("I already have some albums loaded!")
            return
        if not albums:
            irc.reply("I need a list of albums (ex: 1t13 2t12t11)")
            return
        albums = albums.lower()
        albums = albums.split()

        for playlist_idx, album in enumerate(albums, start=1):
            # [INDEX]t[NUMBER OF TRACKS]t[NUMBER OF TRACKS]
            tmp = {}
            for discnum, disc in enumerate(album.split("t")[1:], start=1):
                # create a temporary track list of each disc for tracking
                # whether the track has been played
                # tmp.append(list(range(1, int(disc)+1)))
                tmp[discnum] = list(range(1, int(disc)+1))
            self.current_albums[playlist_idx] = tmp
        
        irc.replySuccess()
        return

    # TODO make this voice/op/admin only?
    @wrap
    def clearchanger(self, irc, msg, args):
        """clear the CD changer out"""
        self.current_albums = {}
        return irc.replySuccess()

    @wrap
    def pickasong(self, irc, msg, args):
        """Pick an album, any album"""
        if not self.current_albums:
            irc.reply("No albums loaded in the changer!")
            return

        # # remove empties
        for alb in self.current_albums:
            self.current_albums[alb] = {k: v for k, v in self.current_albums[alb].items() if v}
        temp_albums = {*self.current_albums}
        for alb in temp_albums:
            try:
                if not self.current_albums[alb]:
                    self.current_albums.pop(alb)
            except:
                continue
        # self.current_albums = list(filter(None, self.current_albums))

        if not self.current_albums:
            irc.reply("I've run out of songs, load some more")
            return

        # first pick an album
        album_index, album_choice = random.choice(list(filter(None, self.current_albums.items())))
        if not album_choice:
            irc.reply("Sorry, I couldn't pick an album")
            return

        # number_of_discs = len(self.current_albums[album_index])

        disc_index, disc_choice = random.choice(list(album_choice.items()))
        if not disc_choice:
            irc.reply("Sorry, I couldn't pick a song")
            return

        # now pick a song and pop it so it doesn't get picked again
        song_choice = self.current_albums[album_index][disc_index].pop(
            random.choice(range(len(disc_choice)))
        )

        reply_string = "{nick} picked {track} from {disc} on {album}"

        reply_string = reply_string.format(
            nick=msg.nick,
            track=ircutils.bold(ircutils.underline("Track #{}".format(song_choice))), 
            disc=ircutils.mircColor(ircutils.bold("Disc/Side {}".format(disc_index)), "blue"),
            album=ircutils.mircColor(ircutils.bold("Album #{}".format(album_index)), "green"),
        )

        irc.reply(reply_string)
        # # remove empties
        # self.current_albums = {k: v for k, v in self.current_albums.items() if v}
        for alb in self.current_albums:
            self.current_albums[alb] = {k: v for k, v in self.current_albums[alb].items() if v}
        return


Class = AlbumPicker


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
