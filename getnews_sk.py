import requests
from bs4 import BeautifulSoup
import datetime as dt
import csv
import time
import re


##### 기사 본문 전처리 함수
def modify(body) :
  # body = BeautifulSoup(re.sub('<em class="img_desc">((?!<\/em>).)*<\/em>', '', str(body))).text
  try :
    result = re.search('(.|\n)*(?=[^a-zA-Z0-9][a-zA-Z0-9]+@[a-zA-Z]+\.(com|kr|co.kr))', body)
    body = result.group()
  except Exception as e :
    pass
    # print('예외발생', e)
  finally :
    body = re.sub('\([가-힣]+\=연합뉴스\)', '', body)
    body = re.sub('[가-힣]{2,4} (기자|특파원|통신원)', '', body)
  return body.replace('\n', ' ').strip()




##### 뉴스 제목 본문 등 크롤링하는 함수
def get_news(URL) :

  res = requests.get(URL)
  soup = BeautifulSoup(res.text, 'html.parser')

  title = soup.select_one('h2#title_area > span').text.strip()
  content = modify(soup.select_one('article#dic_area').text)
  # date = soup.select_one('span._ARTICLE_DATE_TIME').text # 이거보다
  date = soup.select_one('span._ARTICLE_DATE_TIME')['data-date-time'] # 이게 날짜형태로 변환할 수 있어서 더 좋음
  media = soup.select_one('a.media_end_head_top_logo > img')['title']
  return (title, date, media, content, URL)




##### 날짜 옮겨가면서 csv로 저장할 함수
def get_news_value(d, k, s) :

  now = s + dt.timedelta(days=d)   # d값을 일수로 변환해서 날짜 연산
  nowdate = str(now.strftime('%Y.%m.%d'))
  file = open(f"/content/drive/MyDrive/SK하이닉스/뉴스 크롤링 데이터/19.4월/sk_{str(now.strftime('%y%m%d'))}.csv",mode="w",encoding="utf-8",newline="")
  writer = csv.writer(file)

  page = 1

  while True :
    start = (page-1)*10 + 1
    URL = 'https://search.naver.com/search.naver?where=news&sm=tab_pge&query={0}&sort=1&photo=0&field=0&pd=3&ds={1}&de={1}&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:from{2}to{2},a:all&start={3}'.format(k, nowdate, nowdate.replace('.',''), start)
    # print(URL)
    headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    ,'Referer':'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%ED%85%8C%EC%8A%AC%EB%9D%BC&sort=1&photo=0&field=0&pd=3&ds=2023.09.21&de=2023.09.21&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:from20230921to20230921,a:all&start=91'
    }
    res = requests.get(URL, headers=headers)
    print(res)

    soup = BeautifulSoup(res.text, 'html.parser')

    if soup.select('ul.list_news') == [] :
      print('없음')
      print(URL)
      break

    for li in soup.select('ul.list_news > li') :
      if len(li.select('div.info_group > a')) == 2 :
        # print(li.select('div.info_group > a')[1]['href'])
        try :
          writer.writerow(get_news(li.select('div.info_group > a')[1]['href']))
        except :
          pass

    page += 1

  file.close()




##### 키워드, 날짜 입력하면 그 기간동안 모든 뉴스 리스트 뽑는 함수
def get_news_list(keyword, startdate, enddate) :

  headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    ,'Referer':'https://search.naver.com/search.naver?where=news&sm=tab_pge&query=%ED%85%8C%EC%8A%AC%EB%9D%BC&sort=1&photo=0&field=0&pd=3&ds=2023.09.21&de=2023.09.21&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:from20230921to20230921,a:all&start=91'
  }
  startdate = dt.datetime.strptime(startdate, '%Y.%m.%d')   # 문자열을 날짜로 바꾸는 함수
  enddate = dt.datetime.strptime(enddate, '%Y.%m.%d')

  for d in range(0, (enddate - startdate).days + 1) :
    get_news_value(d, keyword, startdate)



##### 실행

start_time = time.time()

get_news_list('SK하이닉스', '2019.04.19', '2019.04.30')

end_time = time.time()

print('소요시간 : ', end_time - start_time)