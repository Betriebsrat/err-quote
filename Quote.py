import logging
import os
import sqlite3

from errbot import botcmd, BotPlugin


class Quote(BotPlugin):
    """Simple sqlite based quote storage"""

    def activate(self):
        QUOTE_DB = self.plugin_dir + os.sep + 'quote.sqlite'
        if not os.path.exists(QUOTE_DB):
            logging.warning('no database found, creating a new one')
            open(QUOTE_DB, 'a').close()

        self.con = sqlite3.connect('QUOTE_DB', check_same_thread=False)
        self.cur = self.con.cursor()
        self.cur.execute('''create table if not exists quotes (id integer primary key, quote text not null)''')
        self.con.commit()
        super(Quote, self).activate()

    def deactivate(self):
        self.con.close()
        super(Quote, self).deactivate()

    @botcmd()
    def quote(self, msg, args):
        """ Returns random quote, usage: !quote"""
        self.cur.execute('''select * from quotes order by random() limit 1''')
        quote = self.cur.fetchone()
        if quote is None:
            msg = 'No quotes added yet'
        else:
            msg = '[%d] %s' % (quote[0], quote[1])
        self.con.commit()
        return msg

    @botcmd()
    def quote_find(self, msg, args):
        """Searches quotes for strings, usage: !quote find <args>"""
        self.cur.execute('''select * from quotes where quote like ? order by random() limit 1''', ('%' + args + '%',))
        quote = self.cur.fetchone()
        if quote is None:
            ret = 'Did not found anything matching = %s.' % (args)
        else:
            ret = '[%d] %s' % (quote[0], quote[1])
        self.con.commit()
        return ret

    @botcmd()
    def quote_add(self, msg, args):
        """Adds a new quote, usage: !quote add <string> """
        self.cur.execute('''insert into quotes (quote) values (?)''', (args,))
        self.con.commit()

        ret = 'Added: %s.' % (args)
        return ret

    @botcmd()
    def quote_del(self, msg, args):
        """Removes Quote from Database, usage: !quote del <id>"""
        self.cur.execute('''delete from quotes where id = ?''', (args,))
        self.con.commit()

        ret = 'Removed: #%d.' % int(args)
        return ret

    @botcmd()
    def quote_get(self, msg, args):
        """Fetches Quote by ID, usage: !quote get <id>"""
        self.cur.execute('''select * from quotes where id = ?''', (args,))
        quote = self.cur.fetchone()
        if quote is None:
            ret = 'Did not found a quote with id = %d.' % int(args)
        else:
            ret = '[%d] %s' % (quote[0], quote[1])
        self.con.commit()
        return ret
