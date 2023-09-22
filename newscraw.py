
# import datetime as dt
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

def get_news(URL) : # 뉴스 내용 긁어오는 함수

  res = requests.get(URL)
  soup = BeautifulSoup(res.text, 'html.parser')

  title = soup.select_one('h2#title_area > span').text
  content = soup.select_one('article#dic_area').text.strip()
  # date = soup.select_one('span._ARTICLE_DATE_TIME').text # 이거보다
  date = soup.select_one('span._ARTICLE_DATE_TIME')['data-date-time'] # 이게 날짜형태로 변환할 수 있어서 더 좋음
  media = soup.select_one('a.media_end_head_top_logo > img')['title']

  return (title, date, media, content, URL)


def get_news_list(keyword, startdate, enddate) : # 뉴스리스트 뽑아서 설정한 값의 모든 뉴스를 출력하는 함수

  file = open("newslist.csv",mode="w",encoding="utf-8",newline="")
  writer = csv.writer(file)

  headers = {
    'Cookie':'NNB=NOAWMWOS2LXGI; nx_ssl=2; _naver_usersession_=U/xBSxXXxIO1prOM6PxioQ==; page_uid=id0GBlp0Jywss7BI5SNssssstuN-197031'
    ,'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    ,'Referer':'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%ED%85%8C%EC%8A%AC%EB%9D%BC&sort=1&photo=0&field=0&pd=3&ds=2023.09.21&de=2023.09.21&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:from20230921to20230921,a:all&start=91'
  }
  # startdate = dt.datetime.strptime(startdate, '%Y.%m.%d')
  # enddate = dt.datetime.strptime(enddate, '%Y.%m.%d')

  # for d in range(0, (enddate - startdate).days + 1) :
  #   nowdate = startdate + dt.timedelta(days=d)
  #   # print(nowdate)
  #   nowdate = str(nowdate.strftime('%Y.%m.%d'))
  #   page = 1

  for nowdate in pd.date_range(startdate, enddate) :   # 이거는 끝값까지 포함함
    nowdate = str(nowdate).replace('-','.')[:10]
    page = 1

    while True :
      start = (page-1)*30 + 1
      URL = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={}&sort=1&photo=0&field=0&pd=3&ds={}&de={}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:from{}to{},a:all&start={}'.format(keyword, nowdate, nowdate, nowdate.replace('.',''), nowdate.replace('.',''),start)
      res = requests.get(URL, headers=headers)
      soup = BeautifulSoup(res.text, 'html.parser')

      if soup.select('ul.list_news') == [] :
        break

      for li in soup.select('ul.list_news > li') :
        if len(li.select('div.info_group > a')) == 2 :
          print(li.select('div.info_group > a')[1]['href'])
          writer.writerow(get_news(li.select('div.info_group > a')[1]['href']))

      page += 1

  file.close()




get_news_list('남양', '2022.09.25', '2022.9.30')