import numpy as np

# 학습데이터 훈련데이터 정의
# 1이 스팸, 0이 정상
training_set = [['me free lottery', 1],
                ['free get free you', 1],
                ['you free scholarship', 0],
                ['free to contact me', 0],
                ['you won award', 0],
                ['you ticket lottery', 1]]

test = ['free lottery']



# 훈련데이터 단어 단위로 끊어주기
wordlist = []

for mail in training_set :
  wordlist.extend(mail[0].split(' '))

wordlist = list(set(wordlist))
wordlist.sort()



# 해당 단어를 포함한 메일의 정상빈도 스팸빈도
wordDic = {}
totalNorm = 0
totalSpam = 0

for word in wordlist :
  spam = 0
  norm = 0

  for train in training_set :
    if word in train[0] :
      if train[1] == 1 :
        spam += 1
      else :
        norm += 1
    else :
      pass

  totalNorm += norm
  totalSpam += spam
  wordDic.setdefault(word, [spam, norm])

wordDic



# 해당 단어가 포함됐을대 스팸/정상일 조건부 확률 구하기
# P(A|B) = P(A교집합B) / P(B)
Pdic = {}

for key, val in wordDic.items() :  # .items() 딕셔너리의 키, 값 모두 불러오는 메서드. 이거 없으면 for문으로 불러와지지 않음
  wSpam = (0.5 + val[0]) / (0.5*2 + totalSpam)
  wNorm = (0.5 + val[1]) / (0.5*2 + totalNorm)
  Pdic.setdefault(key, [wSpam, wNorm])

Pdic



# 로그 적용한 확률 구하는 함수 정의
import math

def logP(x, y) :
  k = 0.5   # 라플레이스 스무딩
  return math.log((k + x) / (2*k + y))



# 조건부 확률에 로그 적용한 값 구하기
Pdic = {}

for key, val in wordDic.items() :  # .items() 딕셔너리의 키, 값 모두 불러오는 메서드. 이거 없으면 for문으로 불러와지지 않음
  wSpam = logP(val[0], totalSpam)
  wNorm = logP(val[1], totalNorm)
  Pdic.setdefault(key, [wSpam, wNorm])

Pdic




# 테스트 데이터 분할
testdata = test[0].split(' ')



# 테스트 데이터 실험
logTestSpam = logP(totalSpam, totalSpam + totalNorm)
logTestNorm = logP(totalNorm, totalSpam + totalNorm)

for testword in testdata :   # 테스트 데이터 인풋하기
  logTestSpam += Pdic[testword][0]
  logTestNorm += Pdic[testword][1]

testSpam = math.exp(logTestSpam)*100
testNorm = math.exp(logTestNorm)*100
# print(testSpam, testNorm)



# free와 lottery가 들어간 메일이 스팸일 확률, 정상일 확률
Pspam = round((testSpam / (testSpam + testNorm)), 2)
Pnorm = round((testNorm / (testSpam + testNorm)), 2)
print(Pspam, Pnorm)