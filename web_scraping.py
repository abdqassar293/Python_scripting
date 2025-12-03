import sys
import requests
from bs4 import BeautifulSoup

def get_h1_tags():
    url='https://books.toscrape.com/'
    resp = requests.get(url,timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    desired_tag = soup.find_all("h3")
    return [tag.get_text(strip=True) for tag in desired_tag]

def get_articles_score(score): #get articles with score greater than or equal to the given score
    url='https://news.ycombinator.com/'
    resp = requests.get(url,timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    votes = soup.select(".score") #Score is the CSS class for the votes of each article

    articles=[]
    for tag in votes:
        if int(tag.get_text(strip=True).split()[0]) >= score:
            article_id=str(tag["id"]).replace("score_","")
            article_score=tag.get_text(strip=True)
            article_link = None
            
            #extracting the linke of the article with id
            article_row = soup.find("tr", {"id": article_id}) # Find the article row by ID
            if article_row:
                titleline = article_row.find("span", class_="titleline")
                if titleline:
                    link_tag = titleline.find("a")
                    if link_tag:
                        article_link = link_tag.get("href")
                        
            article={
                "article_id": article_id, 
                "article_score": article_score,
                "article_link": article_link
                }
            articles.append(article)
            
    articles.sort(key=lambda x: x["article_score"], reverse=True)
    return articles

if __name__ == "__main__":
    # for i, text in enumerate(get_h1_tags(), start=1):
    #     print(f"H3 #{i}: {text}")
    for i, score in enumerate(get_articles_score(int (sys.argv[1])), start=1):
        print(f"Article Score #{i}: {score.get('article_score')} with ID: {score.get('article_id')} with Link: {score.get('article_link')} ")