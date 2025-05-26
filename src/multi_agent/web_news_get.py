from serpapi import GoogleSearch
import time

GOOGLE_API_KEY = "your_api_key"
retry_attempt = 10
def google(text):
    params = {
        "engine": "google",
        "q": text,
        "api_key": GOOGLE_API_KEY,
        "num": 10,
    }

    news_list = []
    for i in range(retry_attempt):
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            for doc in organic_results:
                news_list.append('\"'+ doc['title']+ '\\n' + doc["snippet"] +'\"')

            return news_list
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            if i < retry_attempt - 1:
                time.sleep(2)
            else:
                print("All retries failed.")
                return []
        

def merge_news_insert(lists, num=10):
    result = []
    indices = [0] * len(lists)  
    list_count = len(lists)
    element_count = 0  

    while element_count < num:
        for i in range(list_count):
            current_list = lists[i]
            
            if indices[i] < len(current_list):
                result.append(current_list[indices[i]])
                indices[i] += 1
                element_count += 1

            if element_count >= num:
                break

        if all(indices[j] >= len(lists[j]) for j in range(list_count)):
            break

    return result