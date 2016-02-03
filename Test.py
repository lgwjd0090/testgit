#!/usr/bin/env python
 # -*- coding: utf-8 -*
from sys import argv
from os import sep, makedirs, unlink
from os.path import dirname, exists, isdir, splitext
from string import replace, find, lower
from urlparse import urlparse, urljoin
from urllib import urlretrieve
from htmllib import HTMLParser
from cStringIO import StringIO
from formatter import DumbWriter, AbstractFormatter


class Retriever(object):
    def __init__(self, url):
        self.url = url
        self.file = self.filename(url)
        print self.file
    def filename(self, url, deffile='index.htm'):
        parsedurl = urlparse(url, 'http', 0)
        path = parsedurl[1] + parsedurl[2]
        ext = splitext(path) #分解文件名的扩展名
        print path,ext
        if ext[1] == '':
            if path[-1] == '/':
                path += deffile
            else:
                path += '/' + deffile
        print path
        ldir = dirname(path)
        #应该和操作系统相关 windows下：sep = \
        if sep != '/':
            ldir = replace(ldir, '/', sep)
        print ldir
        if not isdir(ldir):
            if exists(ldir):
                return
            makedirs(ldir)
        return path

    def download(self):
        try:
            retval = urlretrieve(self.url, self.file)
        except IOError:
            retval = ('*** Error URL "%s"' % self.url)
        return retval

    def parseAndGetLinks(self):
        """StringIO是从内存中读取数据 DumbWriter将事件流转换为存文本文档  AbstractFormatter 类进行格式化
        """
        self.parser = HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
        self.parser.feed(open(self.file).read())
        self.parser.close()
        return self.parser.anchorlist
        # pass


class Crawler(object):
    count = 0

    def __init__(self, url):
        self.q = [url]
        self.seen = []
        self.dom = urlparse(url)[1]

    def getPage(self, url):
        r = Retriever(url)
        retval = r.download()
        if retval[0] == '*':
            print retval
            return
        Crawler.count += 1
        self.seen.append(url)

        links = r.parseAndGetLinks()
        print links
        for eachlink in links:
            if eachlink[:4] != 'http' and find(eachlink, '://') == -1:
                eachlink = urljoin(url, eachlink)
            print '* ', eachlink

            if find(lower(eachlink), 'mailto:') != -1:
                print '...discarded, mailto link'
                continue

            if eachlink not in self.seen:
                if find(eachlink, self.dom) == -1:
                    print '...discarded, not in domain'
                else:
                    if eachlink not in self.q:
                        self.q.append(eachlink)
                        print '...new, add to Q'
                    else:
                        print '...discarded, already proccessed'

    def go(self):
        while self.q:
            url = self.q.pop()
            self.getPage(url)


def main():
    if len(argv) > 1:
        url = argv[1]
    else:
        try:
            url = raw_input('Enter starting URL: ')
        except(KeyboardInterrupt, EOFError):
            url = ''
    if not url:
        return
    robot = Crawler(url)
    robot.go()
    # pass


if '__main__' == __name__:
    main()
