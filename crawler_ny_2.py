

import requests
import re
from lxml import html
import os

waiting_links = set()
crawled_links = set()
story_links = set()

def start_links(current_url):
    source = requests.get(current_url)
    tree = html.fromstring(source.content)
    links = tree.xpath('//@href')
    for link in links:
        match = re.match('https://www.nytimes.com/\S+', link) # extract urls under the domain of NewYorkTimes
        if match:
            waiting_links.add(link)
            crawled_links.add(current_url)
    return waiting_links
                        

def page_links():   
    for wlink in waiting_links.copy():
        if wlink not in crawled_links:
            source_c = requests.get(wlink)
            tree_c = html.fromstring(source_c.content)
            crawled_links.add(wlink)
            waiting_links.update(start_links(wlink))
            match = re.search('https://www.nytimes.com/\d+/\d+/\d+/', wlink) # extract article urls
            if match:
                story_links.add(wlink)
                waiting_links.remove(wlink)
            if not match:
                waiting_links.remove(wlink)
    if len(story_links) < 3000:
        return page_links()
    else:
        return story_links

              
def get_text():
    articles_dir = '/Users/zulipiye/Desktop/zulpiya/articles'
    if not os.path.exists(articles_dir):
        os.makedirs(articles_dir)
    topics= ['world', 'us', 'nyregion', 'technology', 'science', 'business', 'sports', 'opinion', 'arts', 'travel']
    for topic in topics:
        with open(os.path.join(articles_dir, topic + '.txt'), 'w', encoding='utf-8') as fout:
            story_id = 0
            pattern = 'https://www.nytimes.com/\d+/\d+/\d+/' + topic + '/\S+' # extract urls which match the selected topic
            for url in story_links:
                match = re.match(pattern, url)
                if match:
                    source_story = requests.get(url)
                    tree_story = html.fromstring(source_story.content)
                    story_title = tree_story.xpath('/html/head/title/text()')
                    author = tree_story.xpath('//*[@id="story"]/header/div[2]/div/div/div/p[@itemprop="author creator"]//text()')
                    time = tree_story.xpath('//*[@id="story"]/header/div[2]/div/ul/li[1]/time/text()')
                    story_text = tree_story.xpath('//div[@class="css-18sbwfn StoryBodyCompanionColumn"]//text()')
                    if story_text != []:
                        story_id += 1
                        if story_id <= 100: 
                            fout.write('<STORY_ID>' + str(story_id) + '</STORY_ID>' + '\n')
                            for title in story_title:
                                fout.write('<TITLE>' + title + '</TITLE>' + '\n')
                            fout.write('<LINK> ' + url + ' </LINK>' + '\n')
                            auth = ''.join(author[2:])
                            fout.write('<AUTHOR>' + auth + '</AUTHOR>' + '\n')
                            for t in time:
                                fout.write('<TIME>' + t + '</TIME>' + '\n')
                            fout.write('<TEXT>' + '\n')
                            for paragraph in story_text:
                                fout.write(paragraph + '\n')
                            fout.write('</TEXT>' + '\n')
                            fout.write('\n')
                        else:
                            fout.close()

def store_in_file():
    with open('/Users/zulipiye/Desktop/zulpiya/waiting_links.txt', 'w', encoding='utf-8') as f1:
        for link in sorted(waiting_links):
            f1.write(link + '\n')

    with open('/Users/zulipiye/Desktop/zulpiya/crawled_links.txt', 'w', encoding='utf-8') as f2:
        for link in sorted(crawled_links):
            f2.write(link +'\n')

    with open('/Users/zulipiye/Desktop/zulpiya/story_links.txt', 'w', encoding='utf-8') as f3:
        for link in sorted(story_links):
            f3.write(link +'\n')

                       
start_links("https://www.nytimes.com/")
page_links()
get_text()
store_in_file()
print(len(story_links))
print(len(crawled_links))
print(len(waiting_links))


    

        
