import requests
from bs4 import BeautifulSoup
import re
import ray
import csv


def get_blog(URL) :   # 블로그에서 내용 긁어오는 함수 

  # h = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}
  tmp = URL.split('/')
  res = requests.get(URL)
  soup = BeautifulSoup(res.text, 'html.parser')

  response = requests.get(f'https://blog.naver.com/PostView.naver?blogId={tmp[-2]}&logNo={tmp[-1]}')
  blog = BeautifulSoup(response.text, 'html.parser')

  if blog.select_one('div.se-title-text') :   # 네이버1
    title = blog.select_one('div.se-title-text').text.strip()
    category = blog.select_one('div.blog2_series > a').text
    author = blog.select_one('span.nick > a').text
    date = blog.select_one('span.se_publishDate').text
    contents = blog.select_one('div.se-main-container').text.replace('\n',' ')

  elif blog.select_one('div.se_component_wrap') :   # 네이버2
    title = blog.select_one('h3.se_textarea').text.strip()
    category = blog.select_one('div.blog2_series > a').text
    author = blog.select_one('span.nick > a').text
    date = blog.select_one('span.se_publishDate').text
    contents = blog.select('div.se_component_wrap')[1].text.strip().replace('\n','')

  elif soup.select_one('div.hgroup > h1') :  # 기타1
    title = soup.select_one('div.hgroup > h1').text
    category = soup.select_one('div.hgroup > div.category').text
    author = soup.select_one('span.author').text
    date = soup.select_one('span.date').text.strip()
    contents = soup.select_one('div.contents_style').text.replace('\n','').strip()

  elif soup.select('div.titlebox > h2 > a') :   # 기타 2
    title = soup.select('div.titlebox > h2 > a')[1].text
    category = soup.select_one('a.category').text
    author = soup.select_one('div.owner > span').text
    date = re.search('[0-9]{4}-.+:[0-9]{2}', soup.select_one('div.date > div.fr > h4').text).group()
    contents = soup.select_one('div.article').text.replace('\n', '').strip()

  elif soup.select_one('div.titleWrap > h2') :  # 기타 3
    title = soup.select_one('div.titleWrap > h2').text
    category = soup.select_one('div.another_category > h4 > a').text
    _posted = str(soup.select_one('div.author'))
    author = re.sub('<.+>', '', _posted).strip()
    _text = soup.select_one('meta[property="article:published_time"]')['content']
    date = re.sub('[A-Z]', ' ', re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}.[0-9]{2}:[0-9]{2}', _text).group())
    contents = soup.select_one('div.contents_style').text.replace('\n','').strip()

  elif soup.select_one('h1.entry-title') :  # 기타 4
    title = soup.select_one('h1.entry-title').text
    category = soup.select_one('div#primary-menu > ul > li > a').text
    author = re.search('[A-Za-z0-9]+(?=@)', soup.select_one('div.copyright-bar').text).group()
    _text = soup.select_one('span.posted-on > time')['datetime']
    date = re.sub('[A-Z]', ' ', re.search('[0-9]{4}-[0-9]{2}-[0-9]{2}.[0-9]{2}:[0-9]{2}', _text).group())
    contents = soup.select_one('div.entry-content').text.replace('\n', '').strip()

  elif soup.select_one('h2,title-article') :  # 기타 5
    title = soup.select_one('h2,title-article').text
    category = soup.select_one('p.category').text
    author = soup.select_one('span.writer').text
    date = soup.select_one('span.date').text
    contents = soup.select_one('div.contents_style').text.replace('\n', '').strip()

  else :
    print('오류')

  return (title, category, author, date, contents, URL)



ray.init()

@ray.remote
def get_blog_list(keyword, startdate, enddate) :  # 키워드&날짜 넣어서 10페이지까지 블로그 긁어오는 함수
  
  file = open("bloglist.csv",mode="w",encoding="utf-8",newline="")
  writer = csv.writer(file)
  
  start = 1
  URL = 'https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&query={0}&rev=44&start={1}&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so%3Add%2Cp%3Afrom{2}to{3}&nlu_query=%7B%22r_category%22%3A%2233+25%22%7D&dkey=0&source_query=&nx_search_query={0}&spq=0&_callback=viewMoreContents'.format(keyword, start, startdate, enddate)
  h = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36', 'Referer' : 'https://search.naver.com/search.naver?where=news&query=%ED%85%8C%EC%8A%AC%EB%9D%BC&sm=tab_opt&sort=2&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0', 'cookie':'NNB=KXDWSALR5HLWE; ASID=afc28e77000001821bee653700000062; _ga=GA1.2.852833469.1658355403; _ga_7VKFYR6RV1=GS1.1.1663030713.12.1.1663030726.47.0.0; NFS=2; m_loc=8e6c6458de8107ce6b301a2fdcaac47c270f10d32641f9fdfed1b5b1faac3e2c; NV_WETR_LAST_ACCESS_RGN_M="MDIxMzU1NTA="; NV_WETR_LOCATION_RGN_M="MDIxMzU1NTA="; recent_card_list=2936,3397,2717,3977; nx_ssl=2; nid_inf=-1453188587; NID_AUT=3O547E30xwR+LSPJWBh1H0BeJZ8z7w5GcYoFiB1oouz7XPFXgUYyapi0YaIPu/ed; NID_JKL=G/s4QbAdJVVTz69y/dBkR/9g00VQhbM8nxg71ZvVgyE=; NID_SES=AAABoKkgglCWz6aloghoOZ3uiyN2Gx8Ya6M3siOaeQCtWMn7TXgrPkganW/YVI931ONSrWmpB6IIM3p/mCMfueM9ekkTAuzM2mj8PfOoUbrV7BrzerfHGStcNmmb0QkiSuOy8AH1MwneQ7sJCTZBpPEfIbn9HUQ6S62sMy5oLJ0xqXedXxwQ4TsBa4+6Z6FWpVTIfmTzWMFt/M4pfpxYEbYAVBsfhLIsNPCjHLCrkoDdQPeUS949dDM9Xf8zpucBTRJrB6GwKaQDSeVWs+OgXngp1iusiktNnHZ7hEWDO5gyZCXkA7jV9njHKBDw6b58JD2La4eTPDBjq6xzUHaCAt+L7rGlpQ5FWHh1UF8XcyHGLdi2zQRHHSs9giWGIdbJ61akjlPZM/N8vL9zJZcw8qFmko0EY8RNmF1aUNE7qEcfaEyQNu/tlmIsUeYl5kPbZgL8fUiKMssPunn4ciffRsstEIcRbvtkVUdDKvr5QdQdf5J0o167t5vXBvctqzggQXUYOOBv8Cb9G9W5NcGibg9J3OCd7JMZTNGPV6gFAtga/WJL; page_uid=idY26sprvTVssudbzPwssssssI4-486433; _naver_usersession_=SXc2E3wZ6W9q/0SVHj+cMQ=='}
  res = requests.get(URL, headers = h)
  total_page = int(res.text[28:].split('\"')[0])//30+1

  total_page = 10

  for page in range(1, total_page+1) :
    start = 30*(page-1)+1
    URL = 'https://s.search.naver.com/p/blog/search.naver?where=blog&sm=tab_pge&api_type=1&query={0}&rev=44&start={1}&dup_remove=1&post_blogurl=&post_blogurl_without=&nso=so%3Add%2Cp%3Afrom{2}to{3}&nlu_query=%7B%22r_category%22%3A%2233+25%22%7D&dkey=0&source_query=&nx_search_query={0}&spq=0&_callback=viewMoreContents'.format(keyword, start, startdate, enddate)
    res = requests.get(URL, headers = h)
    soup = BeautifulSoup(res.text.replace("\\",""), "html.parser")

    for item in soup.select('li div.total_area > a') :
      try :
        writer.writerow(get_blog(item['href']))
      except :
        writer.writerow('오류', '', '', '', '', item['href'])

  file.close()



tesla = get_blog_list.remote('테슬라', '20230921', '20230921')
result = ray.get(tesla)

ray.shutdown()
