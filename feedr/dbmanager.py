import datetime
import sqlite3


USER_SUBSCRIPTIONS_TABLE_NAME = 'user_subscriptions'


class DatabaseManager(object):

    '''
    This class is used to manage a single RSS feed's table in the database.
    It writes new updates to the table, and checks if the latest update from
    the RSS feed already exists in the table (and has thus already been posted).
    '''

    def __init__(self, sqlite_db, feed_dbtable):
        '''
        Checks if it feed's table exists in the DB, creates it if not.
            * Feed table structure: (id integer primary key autoincrement,
                                     sha256_hash text, date text, name text,
                                     url text)
        '''

        self.sqlite_db = sqlite_db
        self.feed_dbtable = feed_dbtable

        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()
        c.execute(
            'SELECT name FROM sqlite_master WHERE type="table" AND name=?',
            (self.feed_dbtable,))
        if c.fetchall() == []:  # table doesn't exist
            # ! WARNING : Vulnerable to SQLi with forged table name
            # Ugly workaround for binding a table name
            if self.feed_dbtable == USER_SUBSCRIPTIONS_TABLE_NAME:
                c.execute(
                    (
                        'CREATE table {}'
                        '(id integer primary key autoincrement, '
                        'user_id text, '
                        'feed_table_name text)'
                    ).format(
                        self.feed_dbtable,
                    )
                )
            else:
                # feed table
                c.execute(
                    (
                        'CREATE table {}'
                        '(id integer primary key autoincrement, '
                        'sha256_hash text, '
                        'date text, '
                        'title text, '
                        'url text)'
                    ).format(
                        self.feed_dbtable,
                    )
                )
        conn.commit()
        conn.close()

    def create_latest_rss_entry(self, update):
        '''
        Receives an entry from TweetUpdate's latest_rss_entry_to_db method,
        then creates an entry in the feed's assigned table in the SQLite3
        database for the update, with the following structure:
            (id, sha256_hash text, date text, title text, url text)
            where id is automatically generated.
        '''

        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()

        table = self.feed_dbtable

        # Set default value of 'date' to utcnow str.
        # This won't affect the sha256_hash, which is used to determinate existing entry in check_for_existing_update()
        if update[1] == '':
            update[1] = str(datetime.datetime.utcnow())

        # ! WARNING : Vulnerable to SQLi with forged table name
        # Ugly workaround for binding a table name
        c.execute(
            'INSERT INTO {}(sha256_hash, date, title, url) VALUES(?, ?, ?, ?)'.
            format(table), update)
        conn.commit()
        conn.close()

    def del_last_table_entry(self):
        '''
        Deletes the last entry in a feed's table using the id column.
        '''

        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()

        table = self.feed_dbtable

        # ! WARNING : Vulnerable to SQLi with forged table name
        # Ugly workaround for binding a table name
        c.execute(
            "DELETE FROM {} WHERE id = (SELECT MAX(id) FROM {})".format(table))
        conn.commit()
        conn.close()

    def get_last_table_entry(self):
        '''
        Returns the last entry in a feed's table using the id column.
        '''

        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()

        table = self.feed_dbtable

        try:
            # ! WARNING : Vulnerable to SQLi with forged table name
            # Ugly workaround for binding a table name
            c.execute(
                "SELECT * FROM {} WHERE id = (SELECT MAX(id) FROM {})".format(table))
            entry = c.fetchone()
        except IndexError:  # empty table
            entry = None

        conn.commit()
        conn.close()

        return entry

    def check_for_existing_update(self, hashval):
        '''
        Checks if an update already exists in the database, i.e. if the hash
        generated from the latest update with TweetUpdate's rss_latest_sha256
        method already exists in the feed's table of the SQLite3 DB.
        This method is used by TweetUpdate's monitor_new_update method, so it
        returns a boolean
        '''

        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()

        table = self.feed_dbtable
        # ! WARNING : Vulnerable to SQLi with forged table name
        # Ugly workaround for binding a table name
        c.execute('SELECT * from {} WHERE sha256_hash=?'.format(table), hashval)

        if c.fetchone():  # unique update hash present in table, update exists
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False

    def get_feed_subscribed_users(self):
        '''
        Return ids of user who subscribed this feed_dbtable.
        '''

        conn = sqlite3.connect(self.sqlite_db)
        c = conn.cursor()

        try:
            # ! WARNING : Vulnerable to SQLi with forged table name
            # Ugly workaround for binding a table name
            c.execute(
                'SELECT user_id FROM {} WHERE feed_table_name=?'.format(
                    USER_SUBSCRIPTIONS_TABLE_NAME
                ),
                (self.feed_dbtable,)
            )

            users = c.fetchall()
        except IndexError:  # empty table
            users = []
        else:
            users = [user_tuple[0] for user_tuple in users]
        finally:
            conn.commit()
            conn.close()

        print('table_name: {}'.format(self.feed_dbtable))
        print('subscribed_users: {}'.format(users))

        return users
