__author__ = 'sosman2'

from bs4 import BeautifulSoup
import requests, time, mimetypes #, csv
from urllib.parse import urlparse, urljoin

import logging
logging.basicConfig(level=logging.WARNING)

def same_host(url1, url2):
    host1=urlparse(url1)
    host2=urlparse(url2)
    logging.debug("+++{}=={}:{}".format(url1, url2, host1.netloc==host2.netloc))
    return host1.netloc==host2.netloc

if __name__=="__main__":
    currentpage='http://floridartap.org/'
    homepage = 'http://floridartap.org/'

    # define the currently empty sets for visited and to_visit
    to_visit=set()
    visited=set()

    to_visit.add(currentpage)  # which should be the homepage at this point

    while len(to_visit) > 0:
        # sleep for a second before requesting the page
        time.sleep(1)

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

            visited.add(currentpage)

            for link in BeautifulSoup(r).find_all('a'):

                if link.get('href') is not None:
                    LUNK = link.get('href').strip()
                else:
                    logging.info('LUNK is None: skipping...')
                    continue

                sortingHat = mimetypes.guess_type(LUNK)[0]

                if 'livemeeting.com' in urlparse(LUNK).netloc:
                    logfile.write(str(link.string) + ',' + LUNK + ',' + currentpage + '\n')
                    logging.info('found a livemeeting lunk! {}\t\t\t{}'.format(LUNK, currentpage))

                elif urlparse(LUNK).netloc=='':
                    logging.debug('inside the IF statement that should attach the homepage hostname to links without hostnames')
                    if sortingHat != 'text/html' and sortingHat is not None:
                        logging.debug('same host but type is not html or unknown: not adding to to_visit set')
                        pass
                    elif urlparse(LUNK).scheme == 'mailto':
                        logging.debug('mailto scheme, not adding to to_visit')
                        pass
                    else:
                        to_visit.add(urljoin(currentpage, LUNK))
                        logging.debug('still inside the if statement. here\'s the to_visit set: ' + str(to_visit))

                elif same_host(homepage, LUNK):
                    #if link.get('href') not in to_visit:
                    if sortingHat != 'text/html' and sortingHat is not None:
                        logging.info('same host but type is not html or None: not adding to to_visit set')
                        pass
                    elif urlparse(LUNK).scheme == 'mailto':
                        logging.info('mailto scheme, not adding to to_visit')
                        pass
                    else:
                        to_visit.add(LUNK)
                        logging.info('same hosts- adding to to_visit')

                else:
                    logging.info('different hosts, not adding to to_visit')
                    pass

        #check which items are in both visited and to_visit. remove those items from to_visit
        for lonk in to_visit.intersection(visited):
            logging.debug('cleaning up')
            to_visit.remove(lonk)

        #set currentpage to one of the links in the to_visit
        currentpage=to_visit.pop() #remove and return an arbitrary element in to_visit
        logging.info('new currentpage: ' + currentpage) #for mailto links, the mimetype is unknown
        logging.debug(mimetypes.guess_type(currentpage))
