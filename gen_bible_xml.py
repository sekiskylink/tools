#!/usr/bin/env python
#import os
#import sys
import psycopg2
import psycopg2.extras
"""
Read the bible on the command-line
"""

dbname = "church"
dbuser = "postgres"
dbpasswd = "postgres"
dbhost = "localhost"

conn = psycopg2.connect("dbname=" + dbname + " host= " + dbhost + " user=" + dbuser + " password=" + dbpasswd)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("SELECT a.*, b.count FROM books a, book_chapter_number b where a.id=b.book")
res = cur.fetchall()
d = {}
for r in res:
    d[r["id"]] = {
        "book": r["book"],
        "short_title": r["short_title"],
        "lug_title": r["lug_title"],
        "chapters": r["count"]
    }
#print d

cur.execute("SELECT * FROM bookchapter_versenumber")
res = cur.fetchall()
chapter_verses = {}
for r in res:
    if r["book"] not in chapter_verses:
        chapter_verses[r["book"]] = {r["chapter"]: r["verse_number"]}
    else:
        chapter_verses[r["book"]].update({r["chapter"]: r["verse_number"]})

#print chapter_verses
#cur.execute("SELECT book, chapter, verse,text_lug FROM verses")
#res = cur.fetchall()
#for r in res:

_xml = "<bible>\n"
for bookid in range(1, 67):  # coz we have 66 books in the bible
    _xml += """<b n="%s">\n""" % d[bookid]["lug_title"]
    for chapter in range(1, d[bookid]["chapters"] + 1):
        _xml += """<c n="%s">\n""" % chapter
        for verse in range(1, chapter_verses[bookid][chapter] + 1):
            cur.execute("SELECT text_lug FROM verses WHERE book= %s AND chapter=%s AND verse =%s", (bookid, chapter, verse))
            res = cur.fetchone()
            if res:
                text = res["text_lug"]
            else:
                text = ""
            _xml += """<v n="%s">%s</v>\n""" % (verse, text)
        _xml += """</c>\n"""

    _xml += """</b>\n"""
_xml += "</bible>"
print _xml
conn.close()
