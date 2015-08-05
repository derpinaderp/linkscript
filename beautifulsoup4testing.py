__author__ = 'sosman2'

from bs4 import BeautifulSoup
import requests, time, mimetypes #, csv
from urllib.parse import urlparse, urljoin

def same_host(url1, url2):
    host1=urlparse(url1)
    host2=urlparse(url2)
    #print("+++{}=={}:{}".format(url1, url2, host1.netloc==host2.netloc))
    return host1.netloc==host2.netloc

if __name__=="__main__":
    currentpage='http://www.bestworkplaces.org/'
    homepage = 'http://www.bestworkplaces.org/'

    # define the currently empty sets for visited and to_visit
    to_visit=set()
    visited=set()

    to_visit.add(currentpage)  # which should be the homepage at this point

    while len(to_visit) > 0:
        # sleep for a second before requesting the page
        time.sleep(1)

        with open('log.txt', mode='a') as logfile:
            if urlparse(currentpage).scheme == 'javascript':
                currentpage=to_visit.pop()
            try:
                r=requests.request(method='GET', url=currentpage).content
            except TimeoutError as e:
                print(e)
                continue
            except requests.exceptions.InvalidSchema as e:
                print(e)
                continue
            except Exception as e:
                print(e)
                continue

            visited.add(currentpage)

            for link in BeautifulSoup(r).find_all('a'):

                if link.get('href') is not None:
                    LUNK = link.get('href').strip()
                else:
                    #print('LUNK is None: skipping...')
                    continue

                sortingHat = mimetypes.guess_type(LUNK)[0]

                if 'livemeeting.com' in urlparse(LUNK).netloc:
                    logfile.write(str(link.string) + ',' + LUNK + ',' + currentpage + '\n')
                    print(LUNK + '\t\t\t' + currentpage)

                elif urlparse(LUNK).netloc=='':
                    #print('inside the IF statement that should attach the homepage hostname to links without hostnames')
                    if sortingHat != 'text/html' and sortingHat is not None:
                        #print('same host but type is not html or unknown: not adding to to_visit set')
                        pass
                    elif urlparse(LUNK).scheme == 'mailto':
                        #print('mailto scheme, not adding to to_visit')
                        pass
                    else:
                        to_visit.add(urljoin(currentpage, LUNK))
                        #print('still inside the if statement. here\'s the to_visit set: ' + str(to_visit))

                elif same_host(homepage, LUNK):
                    #if link.get('href') not in to_visit:
                    if sortingHat != 'text/html' and sortingHat is not None:
                        #print('same host but type is not html or None: not adding to to_visit set')
                        pass
                    elif urlparse(LUNK).scheme == 'mailto':
                        #print('mailto scheme, not adding to to_visit')
                        pass
                    else:
                        to_visit.add(LUNK)
                        #print('same hosts- adding to to_visit')

                else:
                    #print('different hosts, not adding to to_visit')
                    pass

        #check which items are in both visited and to_visit. remove those items from to_visit
        for lonk in to_visit.intersection(visited):
           #print('cleaning up')
            to_visit.remove(lonk)

        #set currentpage to one of the links in the to_visit
        currentpage=to_visit.pop() #remove and return an arbitrary element in to_visit
        print('new currentpage: ' + currentpage) #for mailto links, the mimetype is unknown
        #print(mimetypes.guess_type(currentpage))