__author__ = 'sosman2'

from bs4 import BeautifulSoup
import requests, time, mimetypes #, csv
from urllib.parse import urlparse, urljoin

import logging
logging.basicConfig(level=logging.INFO)


def same_host(url1, url2):
    """Returns True if URLs have the same host, or if one of them is relative"""
    host1 = urlparse(url1)
    host2 = urlparse(url2)
    if host1.netloc == host2.netloc:
        return True
    elif url_is_relative(url1) or url_is_relative(url2):
        logging.debug("One of the URLs is relative. Treating as same host: {} {}".format(url1, url2))
        return True
    else:
        logging.debug("Different hosts: {} {}".format(url1, url2))
        return False


def allowed_mime_type(url, allowed_mime_types):
    sortingHat = mimetypes.guess_type(url)[0]
    if sortingHat in allowed_mime_types:
        return True
    else:
        logging.debug("Invalid mime: {} ({})".format(sortingHat, url))
        return False


def allowed_url_scheme(url, allowed_url_schemes):
    url_obj = urlparse(url)
    if url_obj.scheme in allowed_url_schemes:
        return True
    else:
        logging.debug("Invalid scheme: {} ({})".format(url_obj.scheme, url))


def url_is_relative(url):
    return urlparse(url).netloc == ''


if __name__=="__main__":
    currentpage='http://floridartap.org/'
    homepage = 'http://floridartap.org/'

    # define the currently empty sets for visited and to_visit
    to_visit=set()
    visited=set()

    to_visit.add(currentpage)  # which should be the homepage at this point

    valid_url_schemes = ['http', 'https', '']
    valid_mime_types = ['text/html', None]

    while len(to_visit) > 0:
        # sleep for a second before requesting the page
        time.sleep(1)

        #set currentpage to one of the links in the to_visit
        currentpage=to_visit.pop()
        logging.debug("Visiting: {}".format(currentpage))

        with open('log.txt', mode='a') as logfile:
            if urlparse(currentpage).scheme == 'javascript' or urlparse(currentpage).scheme == 'file' or urlparse(currentpage).scheme == 'mhtml' or urlparse(currentpage).scheme == 'tel':
                visited.add(currentpage)
                try:
                    currentpage=to_visit.pop()
                    continue
                except KeyError:
                    continue
            if urlparse(currentpage).fragment == 'top' or 'comment' in urlparse(currentpage).fragment or 'respond' in urlparse(currentpage).fragment:
                visited.add(currentpage)
                try:
                    currentpage=to_visit.pop()
                    continue
                except KeyError:
                    continue

            try:
                r=requests.request(method='GET', url=currentpage).content
            except TimeoutError as e:
                logging.error(e)
                continue
            except requests.exceptions.InvalidSchema as e:
                logging.error(e)
                continue
            except Exception as e:
                logging.error(e)
                continue



            for link in BeautifulSoup(r).find_all('a'):

                if link.get('href') is not None:
                    LUNK = link.get('href').strip()
                else:
                    logging.info('LUNK is None: skipping...')
                    continue

                if 'livemeeting.com' in urlparse(LUNK).netloc:
                    logfile.write(str(link.string) + ',' + LUNK + ',' + currentpage + '\n')
                    logging.info('found a livemeeting lunk! {}\t\t\t{}'.format(LUNK, currentpage))

                # Ignore URL if the scheme or mime type is not white-listed, or if it's on a different domain
                if allowed_url_scheme(LUNK, valid_url_schemes) and allowed_mime_type(LUNK, valid_mime_types) and \
                        same_host(homepage, LUNK):
                    if url_is_relative(LUNK):
                        link_to_visit = urljoin(currentpage, LUNK)
                    else:
                        link_to_visit = LUNK
                    to_visit.add(link_to_visit)
                else:
                    logging.info("Skipping URL: {} (Ignored mime type, scheme, or domain)".format(LUNK))

        visited.add(currentpage)

        #check which items are in both visited and to_visit. remove those items from to_visit
        for lonk in to_visit.intersection(visited):
            logging.debug('cleaning up')
            to_visit.remove(lonk)


