# 병렬처리 연습

import multiprocessing as mp
from joblib import Parallel, delayed

num_core = min(mp.cpu_count(), 2)
print(num_core)

def square(i) :
    return i*i

#병렬처리 방법
with Parallel(n_jobs=num_core) as parallel :    # with 구문을 이용하여 Parallel 클래스 인스턴스를 만들어준다. 이때 코어수(n_jobs)를 정해준다
    results = parallel(delayed(square)(i) for i in range(10))   # Parallel 클래스 인스턴스에 병렬처리할 작업을 넣어준다. list comprehension 같은 형태
# 각 loop를 돌면서 delayed가 각 코어에 작업을 할당해주면 parallel이 받아서 하나로 다시 합쳐주는 것과 같다

print(results)


# 인자가 다수
from tqdm import tqdm

def square_two(i, j, k) :
    return (i+j)*(i+j) - k


with Parallel(n_jobs=2) as parallel : 
    results = parallel(delayed(square_two)(i, j=2, k=1) for i in tqdm(range(10000)))

print(results[:10])


