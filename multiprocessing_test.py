import multiprocessing
import time

def method1(ar):
    for i in range(10):
        ar.put(i)
        #print("meth"  + str(ar.size()))
        print("method1")
        time.sleep(0.5)
    
def method2(ar):
    for i in range(10):
        time.sleep(1)
        print(ar.get(False))
        print("method2")
        time.sleep(1.5)

def test_multiprocessing():
    queue = multiprocessing.Queue()
    process = []
    
    process.append(multiprocessing.Process(target=method1, args=(queue,)))
    process[0].start()
    process.append(multiprocessing.Process(target=method2, args=(queue,)))
    process[1].start()

    print("start")
        
    for proc in process:
        proc.join()
    # pool = multiprocessing.Pool(processes=2)
    
    # results = [pool.apply_async(method1), pool.apply_async(method2) ]
    # for result in results:
    #     result.get()
    print("test_multiprocessing")
    
    
    
    
if __name__ == "__main__":
    test_multiprocessing()
    print("main")