#!/usr/bin/env python

"""
  This program implements a basic webcrawler in Python, using various modules to keep the source code readable.
  This crawler starts with a given URL for a web page and processes all URLs that are on that page. Each
  URL is avaluated to see if it is a new URL and if so, is put in a queue. Once the original page has been
  processed, the next URL is fetched from the queue and if it is indeed a web page, is processed and so forth.
  
  This code implements also the use of working with URLs, using logging, and working with command line arguments.
"""

import re
import sys
import time
import logging
import math
import urllib
import urllib.error
import urllib.request
from urllib.parse import urlparse
import optparse
#import hashlib
from html import escape
#from traceback import format_exc
from queue import Queue, Empty as QueueEmpty

from bs4 import BeautifulSoup

__version__ = "0.2"

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__

AGENT = "%s/%s" % (__name__, __version__)

class Link (object):

    def __init__(self, src, dst, link_type):
        self.src = src
        self.dst = dst
        self.link_type = link_type

    def __hash__(self):
        return hash((self.src, self.dst, self.link_type))

    def __eq__(self, other):
        return (self.src == other.src and
                self.dst == other.dst and
                self.link_type == other.link_type)
    
    def __str__(self):
        return self.src + " -> " + self.dst

class Crawler(object):

    def __init__(self, root, depth_limit, confine = None, exclude = [], locked = True, filter_seen = True):
        self.root = root
        self.host = urlparse(root).netloc

        ## Data for filters:
        self.depth_limit = depth_limit        # Max depth (number of hops from root)
        self.confine_prefix = confine         # Limit search to this prefix
        self.exclude_prefixes = exclude;      # URL prefixes NOT to visit
        self.locked = locked;                 # Limit crawl to the same host as the originating URL   

        self.urls_seen = set()                # Used to avoid putting duplicates in queue (all mimetypes)
        self.visited_links = set()            # Used to avoid re-processing a page

        self.urls_remembered = set()          # For reporting to user (page URL for mimetype text/html)
        self.links_remembered = set()         # For reporting to user (page URL -> URL)
        
        self.num_links = 0                    # Links found (and not excluded by filters)
        self.num_followed = 0                 # Links followed.


        # Pre-visit filters:  Only visit a URL if it passes these tests
        self.pre_visit_filters=[self._prefix_ok,
                                self._exclude_ok,
                                self._not_visited,
                                self._valid_url,
                                self._lock_host]

        # Out-url filters: When examining a visited page, only process
        # links where the target matches these filters.        
        if filter_seen:
            self.out_url_filters = [self._prefix_ok,
                                     self._same_host]
        else:
            self.out_url_filters = []

    def _pre_visit_url_condense(self, url):
        
        """ Reduce (condense) URLs into some canonical form before
        visiting.  All occurrences of equivalent URLs are treated as
        identical.

        All this does is strip the \"fragment\" component from URLs,
        so that http://foo.com/blah.html\#baz becomes
        http://foo.com/blah.html """

        base, frag = urllib.parse.urldefrag(url)
        return base

    ## URL Filtering functions.  These all use information from the
    ## state of the Crawler to evaluate whether a given URL should be
    ## used in some context.  Return value of True indicates that the
    ## URL should be used.
    
    def _prefix_ok(self, url):
        """Pass if the URL has the correct prefix, or none is specified"""
        return (self.confine_prefix is None  or
                url.startswith(self.confine_prefix))

    def _exclude_ok(self, url):
        """Pass if the URL does not match any exclude patterns"""
        prefixes_ok = [ not url.startswith(p) for p in self.exclude_prefixes]
        return all(prefixes_ok)
    
    def _not_visited(self, url):
        """Pass if the URL has not already been visited"""
        return (url not in self.visited_links)
    
    def _valid_url(self, url):
        """Pass if the URL is a valid URL"""
        return urlparse(url).netloc != ""
    
    def _same_host(self, url):
        """Pass if the URL is on the same host as the root URL"""
        try:
            host = urlparse(url).netloc
            return (re.match(".*%s" % self.host, host))
        except Exception as e:
            logging.debug("Can't process url '%s' (%s)" % (url, e))
            return False
        
    def _lock_host(self, url):
        """Pass if host is to be locked for crawling purposes"""
        return (self.locked and self._same_host(url)) or not self.locked

    def crawl(self):

        """ Main function in the crawling process.  Core algorithm is:

        q <- starting page
        while q not empty:
           url <- q.get()
           if url is new and suitable:
              page <- fetch(url)   
              q.put(urls found in page)
           else:
              nothing

        new and suitable means that we don't re-visit URLs we've seen
        already fetched, and user-supplied criteria like maximum
        search depth are checked. """
        
        q = Queue()
        q.put((self.root, 0))

        while not q.empty():
            this_url, depth = q.get()
            logging.debug("Got %s from queue to process with depth %d" % (this_url, depth))
            
            #Non-URL-specific filter: Discard anything over depth limit
            if depth > self.depth_limit:
                logging.debug("Will not process any further because depth %d > depth limit %d" % (depth, self.depth_limit))
                break # if there's a chance depth will get less for future links, use continue instead
            
            #Apply URL-based filters.
            do_not_follow = [f for f in self.pre_visit_filters if not f(this_url)]

            #If no filters failed (that is, all passed), process URL
            if do_not_follow == []:
                logging.info("Processing [%d] %s" % (depth, this_url))
                try:
                    self.visited_links.add(this_url)
                        
                    self.num_followed += 1
                    page = Fetcher(this_url)
                    
                    page.fetch()
                    added_links = 0
                    for link_url in [self._pre_visit_url_condense(l) for l in page.out_links()]:
                        if (link_url not in self.urls_seen):
                            q.put((link_url, depth + 1))
                            added_links += 1
                            self.urls_seen.add(link_url)
                            
                        do_not_remember = [f for f in self.out_url_filters if not f(link_url)]
                        if do_not_remember == []:
                            self.num_links += 1
                            self.urls_remembered.add(link_url) # url
                            link = Link(this_url, link_url, "href")
                            if link not in self.links_remembered:
                                self.links_remembered.add(link) # page -> url
                            
                    logging.debug("Added %d links for depth %d" % (added_links, depth + 1))

                except Exception as e:
                    logging.debug("Can't process url '%s' (%s)" % (this_url, e))

            else:
                logging.debug("Will not process because rejected by filters")

class OpaqueDataException (Exception):
    def __init__(self, message, mimetype, url):
        Exception.__init__(self, message)
        self.mimetype=mimetype
        self.url = url
        

class Fetcher(object):
    
    """The name Fetcher is a slight misnomer: This class retrieves and interprets web pages."""

    def __init__(self, url):
        self.url = url
        self.out_urls = []

    def __getitem__(self, x):
        return self.out_urls[x]

    def out_links(self):
        return self.out_urls

    def _addHeaders(self, request):
        request.add_header("User-Agent", AGENT)

    def _open(self):
        url = self.url
        logging.debug("Attempt to connect to %s" % urlparse(url).netloc)
        try:
            request = urllib.request.Request(url)
            handle = urllib.request.build_opener()
        except IOError:
            logging.debug("Error opening %s" % url)
            return None
        return (request, handle)

    def fetch(self):
        request, handle = self._open()
        self._addHeaders(request)
        if handle:
            try:
                data = handle.open(request)
                logging.debug("Succesfully connected to host")
                mime_type = data.info().get_content_type()
                logging.debug("Mimetype is %s" % mime_type)
                url = data.geturl()

                if mime_type != "text/html":
                    raise OpaqueDataException("Not interested in files of type %s" % mime_type, mime_type, url)
                logging.debug("Fetching page from host")
                content = data.read().decode("utf-8", errors="replace")
                logging.debug("Parsing page")
                soup = BeautifulSoup(content, "html.parser")
                logging.debug("Page has been parsed")
                tags = soup('a')
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    logging.debug("Error 404 while fetching %s" % error.url)
                else:
                    logging.debug("Error %s while fetching" % error)
                tags = []
            except urllib.error.URLError as error:
                logging.debug("Error %s while fetching" % error)
                tags = []
            except OpaqueDataException as error:
                logging.debug("Skipping %s (has mimetype %s)" % (error.url, error.mimetype))
                tags = []

            for tag in tags:
                href = tag.get("href")
                if href is not None:
                    url = urllib.parse.urljoin(self.url, escape(href))
                    if url not in self:
                        self.out_urls.append(url)


def parse_options():
    """parse_options() -> opts, args

    Parse any command-line options given returning both
    the parsed options and arguments.
    """

    parser = optparse.OptionParser(usage=USAGE, version=VERSION)

    parser.add_option("-d", "--depth",
            action="store", type="int", default=3, dest="depth_limit",
            help="Maximum depth to traverse (default is 3)")

    parser.add_option("-c", "--confine",
            action="store", type="string", dest="confine",
            help="Confine crawl to specified prefix")
    
    parser.add_option("-n", "--no-host-lock", action="store_true",
                      dest="unlocked", help="Unlock confinement to first host")

    parser.add_option("-x", "--exclude", action="append", type="string",
            dest="exclude", default=[], help="Exclude URLs by prefix")
    
    parser.add_option("-l", "--show-links", action="store_true", default=False,
                      dest="out_links", help="Output links found")

    parser.add_option("-u", "--show-urls", action="store_true", default=False,
                      dest="out_urls", help="Output URLs found")
    
    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help(sys.stderr)
        raise SystemExit(1)

    if opts.out_links and opts.out_urls:
        parser.print_help(sys.stderr)
        parser.error("options -l and -u are mutually exclusive")

    return opts, args
    

def main():
    logformat = "%(levelname)s: %(asctime)s: %(message)s"
    logging.basicConfig(filename='./crawler.log', level = logging.INFO, format = logformat)
    
    opts, args = parse_options()

    url = args[0]

    depth_limit = opts.depth_limit
    confine_prefix = opts.confine
    exclude = opts.exclude

    sTime = time.time()

    logging.info("Recursive crawling started with maximum traversing depth set to %d" % depth_limit)
    
    crawler = Crawler(url, depth_limit, confine_prefix, exclude, locked=(not opts.unlocked))        
    crawler.crawl()
                          
    if opts.out_urls:
        print("\n".join(crawler.urls_remembered))

    if opts.out_links:
        print("\n".join([str(l) for l in crawler.links_remembered]))

    eTime = time.time()
    tTime = eTime - sTime

    logging.info("Crawling completed with %d links found and %d followed" % (crawler.num_links, crawler.num_followed))
    logging.info("Found %d links per second in %0.2f seconds" % (int(math.ceil(float(crawler.num_links) / tTime)), tTime))

if __name__ == "__main__":
    main()