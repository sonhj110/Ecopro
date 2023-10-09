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
input_word = np.array(training_set)

wordlist = []

for w in input_word[:, 0] :
  for i in range(len(w.split(' '))) :
    wordlist.append(w.split(' ')[i])

wordlist = list(set(wordlist))
wordlist.sort()



# 해당 단어를 포함한 메일의 정상빈도 스팸빈도
norm = 0
spam = 0
freq = []

totalSpam = 0
totalNorm = 0

for word in wordlist :
  norm = 0
  spam = 0
  for main in input_word :
    if word in main[0] :
      if main[1] == '1' :
        spam += 1
      else :
        norm += 1
    else :
      pass
  totalSpam += spam
  totalNorm += norm
  freq.append([word, spam, norm])

print(freq)
print(totalSpam, totalNorm)
freq = np.array(freq)



# 라플레이스 스무딩 적용한 확률 구하는 함수 정의
def p(x, y) :
  k = 0.5
  return round((k + x) / (2*k + y) * 100, 4)



# 해당 단어가 포함됐을대 스팸/정상일 조건부 확률 구하기
# P(A|B) = P(A교집합B) / P(B)
wordPlist = []

for wordP in freq :
  # print(wordP)
  wNorm = p(int(wordP[2]), totalNorm)
  wSpam = p(int(wordP[1]), totalSpam)
  wordPlist.append([wordP[0], wSpam, wNorm])



# 로그 적용한 확률 구하는 함수 정의
import math

def logP(x, y) :
  k = 0.5
  result = (k + x) / (2*k + y)
  return round(math.log(result), 4)

logP(1,3)



# 조건부 확률에 로그 적용한 값 구하기
wordPlist = []

for wordP in freq :
  # print(wordP)
  wNorm = p(int(wordP[2]), totalNorm)
  wSpam = p(int(wordP[1]), totalSpam)
  wNormLog = logP(int(wordP[2]), totalNorm)
  wSpamLog = logP(int(wordP[1]), totalSpam)
  wordPlist.append([wordP[0], wSpam, wNorm, wSpamLog, wNormLog])




# 테스트 데이터 실험
free = wordPlist[2]
lottery = wordPlist[4]

_PofNorm = math.exp(free[4]+lottery[4]+logP(totalNorm, totalNorm+totalSpam))*100
_PofSpam = math.exp(free[3]+lottery[3]+logP(totalSpam, totalNorm+totalSpam))*100

PofNorm = round((_PofNorm / _PofNorm + _PofSpam), 2)
PofSpam = round((_PofSpam / _PofNorm + _PofSpam), 2)
print(PofNorm, PofSpam)