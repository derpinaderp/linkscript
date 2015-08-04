__author__ = 'sosman2'

from bs4 import BeautifulSoup
import requests, time, mimetypes, csv
from urllib.parse import urlparse, urljoin

def same_host(url1, url2):
    host1=urlparse(url1)
    host2=urlparse(url2)
    print("+++{}=={}:{}".format(url1, url2, host1.netloc==host2.netloc))
    return host1.netloc==host2.netloc

if __name__=="__main__":
    currentpage='http://www.bestworkplaces.org/'
    homepage = 'http://www.bestworkplaces.org/'

    #define the currently empty sets for visited and to_visit
    to_visit=set()
    visited=set()

    to_visit.add(currentpage) #which should be the homepage at this point

    with open('log.csv', mode='a') as logfile:
        logwriter=csv.writer(logfile,delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)


        while len(to_visit) > 0: #while to_visit is not empty
            #sleep for a second before requesting the page
            time.sleep(1)
            try:
                r=requests.request(method='GET', url=currentpage).content
            except Exception: #requests.exceptions.InvalidSchema as e:
                continue

            #logfile.write(currentpage+'\n')

            visited.add(currentpage)
            #print('visited set: ' + str(visited))
            #print('to_visit set: ' + str(to_visit))

            #with open('links.txt', 'w', newline='') as links:
            for link in BeautifulSoup(r).find_all('a'):
                if link.get('href') is not None:
                    LUNK = link.get('href').strip()
                else:
                    continue

                sortingHat = mimetypes.guess_type(LUNK)[0]

                print('inside the for loop to find all the links \n' \
                      'working with: ' + LUNK \
                      + '\nmimetype: ' + str(sortingHat))

                if urlparse(LUNK).netloc == 'www.livemeeting.com':
                    logwriter.writerow([LUNK, currentpage])
                    print(link.get(LUNK, currentpage)

                if urlparse(LUNK).netloc=='':
                    print('inside the IF statement that should attach the homepage hostname to links without hostnames')
                    if sortingHat != 'text/html' and sortingHat is not None:
                        print('same host but type is not html or unknown: not adding to to_visit set')
                    elif urlparse(LUNK).scheme == 'mailto':
                        print('mailto scheme, not adding to to_visit')
                    else:
                        to_visit.add(urljoin(currentpage, LUNK))
                        #print('still inside the if statement. here\'s the to_visit set: ' + str(to_visit))

                elif same_host(homepage, LUNK):
                    #if link.get('href') not in to_visit:
                    if sortingHat != 'text/html' and sortingHat is not None:
                        print('same host but type is not html or None: not adding to to_visit set')
                    elif urlparse(LUNK).scheme == 'mailto':
                        print('mailto scheme, not adding to to_visit')
                    else:
                        to_visit.add(LUNK)
                        print('same hosts- adding to to_visit')

                else:
                    print('different hosts, not adding to to_visit')

                #links.writelines(link.get('href') + '\n')

            #check which items are in both visited and to_visit. remove those items from to_visit
            for lonk in to_visit.intersection(visited):
                print('cleaning up')
                to_visit.remove(lonk)

            #set currentpage to one of the links in the to_visit
            currentpage=to_visit.pop() #remove and return an arbitrary element in to_visit
            print('new currentpage: ' + currentpage) #for mailto links, the mimetype is unknown
            print(mimetypes.guess_type(currentpage))