import requests
from bs4 import BeautifulSoup
import json
import re
def dfs_search(tag, tagName=None, className=None, role=None):
    """
    this function will do a dfs on the html to find the tag that we are looking for , 
    this function will only find first 2 tag with the corresponding class and role ,
    becuase we only want to have product and essentials
    it will return a list of 2 tags that each of them is eigther list of products or list of essentials
    """
    results=[]
    if (tagName is None or tag.name == tagName) and \
       (className is None or set(className.split()).issubset(set(tag.get('class', [])))) and \
       (role is None or tag.get('role') == role):
        results.append(tag)
        return results
    for child in tag.children:
        if child.name:  
            results.extend(dfs_search(child, tagName, className, role))
            if (len(results)==2) : 
                return results
    
    return results
def actualEmail(initEmail): # using regex to filter emails out 
    return re.findall(":(.+@.+com)",initEmail)[0]

def get_html(url): # function for geting the html using request
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, "html.parser")
    else:
        print(f"Failed to fetch {url}")
        return None

def scrapeContact(baseUrl): 
    """
        this function will go trough Contact and extract names and email from it 
        input = url of the main page 
        return = dictionary contain names and emails  
    """
    data={}
    contactUrl = f"{baseUrl}/team#contact/"
    soup = get_html(contactUrl)
    if not soup:
        return None
    section=soup.find("div", id="w-node-ca11194c-6591-2629-47d7-20c091395d83-4481d0c6") # finding support part in the html
    nameClass="text-size-regular text-color-dark-blue" # used for finding each name from the customer support list
    curName=section.findChild("h3") 
    h3Name=curName.contents[0]
    data[h3Name]={} # making node

    # Customer Support Section

    while (curName.findNextSibling("div",nameClass)):
        curName=curName.findNextSibling("div",nameClass) 
        curEmail=curName.findNextSibling()
        if (curEmail.find('a')) : 
            data[h3Name][curName.contents[0]]=actualEmail(curEmail.find("a").get("href"))
        else : 
            data[h3Name][curName.contents[0]]=actualEmail(curEmail.get("href"))
    
    # Other Sections 

    section=section.findNextSibling("div",class_="contact_item")
    nameClass="margin-bottom margin-medium"
    while (section):
        curName=section.findChild("h3")
        h3Name=curName.contents[0]
        data[h3Name]={}
        curName=curName.findNextSibling("div",nameClass) 
        curEmail=curName.findNextSibling(href=True)
        data[h3Name][curName.findChild().contents[0]]=actualEmail(curEmail.get("href"))
        section=section.findNextSibling("div",class_="contact_item")
    return data
def findProductList(baseUrl):
    soup = get_html(baseUrl) # soup will act as html object
    productList = dfs_search(soup, tagName='div', className='nav_dropdown-link-grid w-dyn-items', role="list")
    dict={}
    dict["Products"]={}
    dict["Essentials"]={}
    for tag in productList[0].contents :
        dict["Products"][tag.find('a').contents[0]]=baseUrl+tag.find('a').get("href")
    for tag in productList[1].contents :
        dict["Essentials"][tag.find('a').contents[0]]=baseUrl+tag.find('a').get("href")
    return dict
def main():
    baseUrl = "https://reviewpro.shijigroup.com/"

    
    data=scrapeContact(baseUrl)
    with open('scraped_contact.json', 'w') as file:
        json.dump(data, file, indent=4)

    #####################################################

    data=findProductList(baseUrl=baseUrl)
    with open('scraped_product.json', 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    main()


