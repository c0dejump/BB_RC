import requests
import sys, os
import argparse
import traceback
from googlesearch import search
from bs4 import BeautifulSoup
import csv

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def get_report_title_h1(req_url_found, soup):
    #print(req_url_found.text)
    try:
        meta_desc = soup.find("meta", {"name":"description"})
        content = meta_desc.get("content")
        for c in content.splitlines():
            if c != "":
                if "##" in c or c in ["description", "Description", "Reproducing", "Fix", "Impact", "Details"] :
                    print("     \033[36m[{}]\033[0m".format(c.replace("##","")))
                else:
                    print("     {}".format(c))
        if not "@Hacker0x01" in content and "hackerone.com/reports/" in req_url_found.text:
            for link in soup.findAll('a'):
                if "hackerone.com/reports/" in link.get('href'):
                    print("  [?] Potential report found: {}".format(link.get('href')))
    except:
        pass


def check_csv(keyword):
    print(" \033[35m\u251c Check on CSV database:\033[0m")
    with open('raw_data/data.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for r in reader:
            if keyword.casefold() in r['title'].casefold():
                print("     \033[36m{}\033[0m :: {}".format(r['link'], r['title']))


def pentesterland(keyword):
    req_p = requests.get("https://pentester.land/list-of-bug-bounty-writeups.html", verify=False, timeout=5)
    soup = BeautifulSoup(req_p.text, "html.parser")
    titles = soup.findAll("a")
    for t in titles:
        if keyword.casefold() in t.text.casefold():
            print("   \033[36m{}\033[0m :: {}".format(t.get("href"), t.text))


def openbugbounty(keyword):
    print("   In progress...")

def check_othersites(keyword):
    """
    https://pentester.land/list-of-bug-bounty-writeups.html
    https://www.openbugbounty.org/blog/
    https://www.openbugbounty.org/blog/page/x
    """
    sites = ["pentesterland", "openbugbounty"]
    for site in sites:
        print(" \033[35m\u251c Check on {}:\033[0m".format(site))
        eval(site)(keyword)



def google_search(keyword):
    queries = ["{} hackerone".format(keyword), "{} bugcrowd crowdstream".format(keyword)]

    other_links = []

    found_report = False

    for query in queries:
        print(" \033[35m\u251c Query: {}\033[0m".format(query))
        try:
            for j in search(query, tld="com", num=10, stop=10, pause=2.6):
                try:
                    req_url_found = requests.get(j, verify=False, timeout=5)
                    if req_url_found.status_code not in [404, 408, 503, 405, 428, 412, 429, 403, 401]:
                        soup = BeautifulSoup(req_url_found.text, "html.parser")
                        if "hackerone.com/reports/" in j:
                            found_report = True
                            print("   \033[32m[{}]\033[0m {}".format(req_url_found.status_code, j))
                            get_report_title_h1(req_url_found, soup)
                        elif "bugcrowd.com/disclosures/" in j:
                            print("   \033[32m[{}]\033[0m {}".format(req_url_found.status_code, j))
                        else:
                            other_links.append("  {} {}".format(req_url_found.status_code, j))
                    elif req_url_found.status_code in [403, 401]:
                        other_links.append("  {} {}".format(req_url_found.status_code, j))
                    else:
                        other_links.append("  {} {}".format(req_url_found.status_code, j))
                except:
                    #traceback.print_exc() #DEBUG
                    print(" ! Error with URL {}".format(j))
            print("")
        except:
            print("  ! Google captcha seem to be activated, try it later...\n")
            pass
    if not found_report:
        print(" \u251c Seem not report found, other links:")
        for ol in other_links:
            print("\033[33m{}\033[0m".format(ol))
    check_csv(keyword)
    check_othersites(keyword)



if __name__ == '__main__':
    #arguments
    parser = argparse.ArgumentParser(add_help = True)
    parser = argparse.ArgumentParser(description='\033[32mVersion ß | contact: https://twitter.com/c0dejump\033[0m')
    
    parser.add_argument("-k", help="Keyword report Search [Ex: -k \"BBE Theme\"; -k \"Stream plugin\"] \033[31m[required]\033[0m\n", dest='keyword', required=True)

    results = parser.parse_args()

    keyword = results.keyword
    
    google_search(keyword)
