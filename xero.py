import requests,re
from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs

def getList(page):
    links,names = [],[]
    r = requests.get('https://www.xero.com/content/xero/uk/advisors/find-advisors/jcr:content/par/advisors_search_6526/advisorsResults.html?type=advisors&orderBy=ADVISOR_RELEVANCE&sort=ASC&pageNumber={0}&view=list'.format(page))
    soup = bs(r.content,'lxml')
    As = soup.find_all('a',{'class':'advisors-result-card-link'})
    h3s = soup.find_all('h3',{'class':'title-3'})
    for a in As:
        links.append(a.attrs['href'])
    for h3 in h3s:
        names.append(h3.get_text().strip())
    return links,names

def getFbEmail(link,s=''):
        if 'http://' not in link[:10] and 'https://' not in link[:10]:
            url = 'https://'+link
        elif '//' == link[:2]:
            url = link[2:]
        else:
            url = link
        
        Link = urlparse(url)
        email = getEmail("https://m.facebook.com/{user}".format(user=Link.path.split('/')[1]),search=s)
        if email:
            return email
        else:
            return ''
        

def getEmail(link,fb='',search=''):
    print(link)
    if 'http://' not in link[:10].lower() and 'https://' in link[:10].lower():
        link = 'http://'+link
    a = urlparse(link)
    aFb = ''
    cPage = ''
    r = requests.get("{s}://{d}".format(s=a.scheme,d=a.netloc),headers={'User-Agent':'Chrome'})
    soup = bs(r.content,'lxml')
    body = soup.find('body')
    [s.extract() for s in body.find_all('script')]
    links = body.find_all('a')
    contactPage = ''
    for link in links:
        try:
            url = link.attrs['href'].lower()
            if 'mailto' in url:
                return url.split(':')[1]
            elif '@' in link.get_text():
                match = re.findall(r'[\w\.-]+@[\w\.-]+', link.get_text())
                if match:
                    return match[0]
            elif 'contact' in url and not search=='fb' and not search=='contact':
                cPage = url 
            elif 'facebook' in url or 'fb' in url:
                aFb = url.split(':')[1]
                    
        except:
            pass
    text = body.get_text()
    match = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    if match:
        return match[0]
    try:
        if '/' in cPage[0] and not search:
            print("\t[=] Visiting Contact Page")
            email = getEmail(link+'/'+cPage,search='contact')
            if email:
                return email
        elif ('http://' in cPage[:10] or 'https://' in cPage[:10]) and not search:
            print("\t[=] Visiting Contact Page")
            email = getEmail(cPage,search='contact')
            if email:
                return email
    except:
        pass
    if fb and not search:
        print(fb)
        print("\t[=] Visiting Facebook Page")
        
        email = getFbEmail(fb,'fb')
        if email:
            return email
        else:
            return 'NULL'
    elif aFb and search:
        print(aFb)
        print("\t[=] Visiting Facebook Page")
        email = getFbEmail(fb,'aFb')
        if email:
            return email
        else:
            return 'NULL'
    return 'NULL'

def getData(link,name):
    print("[=] Scraping Company:",name)
    r = requests.get(link)
    fb = ''
    soup = bs(r.content,'lxml')

    # WEBSITE
    web = soup.find('a',class_='advisors-profile-hero-detailed-contact-website').attrs['href']
    # WEBSITE
    
    # PHONE NUMBER
    phone = soup.find('a',class_='advisors-profile-hero-detailed-contact-phone').attrs['data-phone']
    # PHONE NUMBER
    
    # PARTNER STATUS
    divs = soup.find_all('div',class_='jTrtdh')
    for div in divs:
        if 'partner status' in div.get_text().lower():
            pStatus = div.find('h6').get_text().replace('&nbsp;','')
    # PARTNER STATUS

    # FACEBOOK PROFILE
    try:
        socials = soup.find_all('a',class_='advisor-profile-practice-social-link')
        for social in socials:
            if 'facebook' in social.get_text().lower():
                fb = social.attrs['href']
    except:
        pass
    # FACEBOOK PROFILE
    
    # INDUSTRIES SERVED
    indServed = []        
    industries = soup.find_all('div',class_='TagContent')
    for industry in industries:
        if 'industries served' in industry.get_text().lower():
            List = industry.find_all('li')
            for item in List:
                indServed.append(item.get_text().strip())
            break
    # INDUSTRIES SERVED
        
    # CONNECTED APPS
    conApps = []
    List = soup.find('ul',class_='advisors-profile-experience-list').find_all('li')
    for item in List:
        conApps.append(item.a.img.attrs['alt'])
    # CONNECTED APPS

    # DISPLAYING DATA
    print('\t[+] Phone Number:',phone)
    print('\t[+] Website:',web)
    print('\t[+] Partner Status:',pStatus)
    if fb:
        print('\t[+] Facebook:',fb)
    if indServed:
        print('\t[+] Industry Served:',', '.join(indServed))
    if conApps:
        print("\t[+] Connected Apps:",', '.join(conApps))
    # DISPLAYING DATA

    # EMAIL
    print("\n\t[=] Getting Email from website")
    email= getEmail(web,fb)      
    if not email == 'NULL':
        print("\t[+] Email:",email)
    else:
        print("\t[-] Email Not Found")
    # EMAIL
    
    print("[=] Scraping Completed for Company:",name)


print("------------- XERO SCRAPER ------------\n")
try:
    for i in range(1,249):
        print("[=] Getting Companies on Page",i)
        links,names = getList(i)
        print("[+] {} Companies Retrieved\n".format(len(links)))
        for link,name in zip(links,names):
            data = getData(link,name)
            print('\n')
            
except KeyboardInterrupt:
    print("\n[-] Program Stopped")
except Exception as e:
    print(e)
    
