import requests,re,csv
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
        if '//' == link[:2]:
            url = link[2:]
        elif 'http://' not in link[:10] and 'https://' not in link[:10]:
            url = 'https://'+link
        else:
            url = link
        Link = urlparse(url)
        email = getEmail("https://web.facebook.com/{user}/about".format(user=Link.path.split('/')[1].split('?')[0]),search=s)
        if email:
            return email
        else:
            return ''
        

def getEmail(link,fb='',search=''):
    if 'http://' not in link[:10].lower() and 'https://' not in link[:10].lower():
        link = 'http://'+link
    a = urlparse(link)
    aFb = ''
    cPage = ''
    ses = requests.Session()
    co = {}
    if search in ['fb','aFb']:
        Url = link
    else:
        Url ="{s}://{d}".format(s=a.scheme,d=a.netloc)
    try:
        r = ses.get(Url,headers={'User-Agent':'Chrome'})
    except:
        r = ses.get(Url.replace('http:','https:'),headers={'User-Agent':'Chrome'})
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
            if len(email) > 4:
                return email
        elif ('http://' in cPage[:10] or 'https://' in cPage[:10]) and not search:
            print("\t[=] Visiting Contact Page")
            email = getEmail(cPage,search='contact')
            if len(email)>4:
                return email
    except:
        pass
    if fb and not search:
        print("\t[=] Visiting Facebook Page")
        email = getFbEmail(fb,'fb')
        if len(email)>4:
            return email
        else:
            return 'NULL'
    elif aFb and not search:
        print("\t[=] Visiting Facebook Page")
        email = getFbEmail(aFb,'aFb')
        if len(email)>4:
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
            pStatus = div.find('h6').get_text().replace('&nbsp;','').strip()
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
    email= getEmail(web,fb).split('?')[0]      
    if not email == 'NULL':
        print("\t[+] Email:",email)
    else:
        print("\t[-] Email Not Found")
    # EMAIL
    
    print("[=] Scraping Completed for Company:",name)
    return [name,web,pStatus,', '.join(indServed),', '.join(conApps),'','',phone,email]


print("------------- XERO SCRAPER ------------\n")
try:
    with open('companies.csv','w',newline='',encoding='utf-8') as file:
        cFile = csv.writer(file)
        cFile.writerow(['Company Name','URL','Partner status', 'Industries served', 'Connected Apps', 'Contact person name', 'Contact person position', 'Phone number', 'Email address'])
        for i in range(1,249):
            print("[=] Getting Companies on Page",i)
            links,names = getList(i)
            print("[+] {} Companies Retrieved\n".format(len(links)))
            for link,name in zip(links,names):
                data = getData(link,name)
                cFile.writerow(data)
                print('\n')
                
except KeyboardInterrupt:
    print("\n[-] Program Stopped")
except Exception as e:
    print(e)
    
