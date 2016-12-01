import logging
import os
import sqlite3
from errbot import botcmd, BotPlugin


class Quote(BotPlugin):
    """Sqlite based quote storage for chat channels"""

    def activate(self):
        QUOTE_DB = self.plugin_dir + os.sep + 'quote.sqlite'
        if not os.path.exists(QUOTE_DB):
            logging.warning('no database found, creating a new one')
            open(QUOTE_DB, 'a').close()

        self.con = None
        try:
            self.con = sqlite3.connect(QUOTE_DB, check_same_thread=False)
            self.cur = self.con.cursor()
            self.cur.execute(
                'create table if not exists quotes \
                (id integer primary key, \
                quote text not null, \
                author text default \'unknown\', \
                date text default CURRENT_DATE) ;')
            self.con.commit()
        except sqlite3.Error as e:
            print(e)
        super(Quote, self).activate()

    def deactivate(self):
        self.con.close()
        super(Quote, self).deactivate()

    @botcmd()
    def quote(self, msg, args):
        """ Returns random quote, usage: !quote"""
        self.cur.execute("select * from quotes order by random() limit 1")
        quote = self.cur.fetchone()
        if quote is not None:
            return '[%d] *%s*' % (quote[0], quote[1])
        else:
            return 'Nothing added yet'

    @botcmd()
    def quote_details(self, msg, args):
        """ Returns further details about a quote, usage !quote details <id>"""
        if args.isdigit() == False:
            return 'Usage = !quote details <id>'
        self.cur.execute("select * from quotes where id = ?", (args,))
        quote = self.cur.fetchone()
        if quote is not None:
            return '[%d] *%s*, Author: %s Date: %s' % (quote[0], quote[1], quote[2], quote[3])
        else:
            return 'No matches with id %s' % args

    @botcmd()
    def quote_find(self, msg, args):
        """Searches for strings, usage: !quote find <args>"""
        if args == '':
            return "Usage: !quote find <args>"

        self.cur.execute("select * from quotes where quote like ? order by random() limit 1", ('%' + args + '%',))
        quote = self.cur.fetchone()
        if quote is None:
            return 'Found no matches for: %s.' % args
        else:
            return '[%d] %s' % (quote[0], quote[1])

    @botcmd()
    def quote_get(self, msg, args):
        """Fetches quote by ID or last quote, usage: !quote get <id/last>"""
        if args == 'last':
            self.cur.execute("select * from quotes order by id desc")
        elif args.isdigit() == True:
            self.cur.execute("select * from quotes where id = ?", (args,))
        else:
            return 'Usage: !quote get <id>'
        quote = self.cur.fetchone()
        if quote is None:
            return 'No matches with id = %s.' % args[0]
        else:
            return '[%d] %s' % (quote[0], quote[1])

    @botcmd()
    def quote_new(self, msg, args):
        """Returns the last 3 quotes, usage !quote new"""
        if args != '':
            return 'Usage !quote new'
        self.cur.execute("select * from quotes order by id desc limit 3")
        rows = self.cur.fetchall()
        for row in rows:
            yield '[%d] %s' % (row[0], row[1])

    @botcmd(admin_only=True)
    def quote_add(self, msg, args):
        """Adds a new quote, usage: !quote add <string> """
        if args == '':
            return "Usage: !quote add <args>"
        author = msg.frm.nick
        self.cur.execute("insert into quotes (quote, author) values (?,?)", (args, author))
        self.con.commit()
        return 'Added: %s.' % args

    @botcmd(admin_only=True)
    def quote_del(self, msg, args):
        """Removes quote from database, usage: !quote del <id>"""
        if args == '':
            return "Usage: !quote del <id>"
        self.cur.execute("delete from quotes where id = ?", (args,))
        self.con.commit()
        return 'Removed: %s.' % args
