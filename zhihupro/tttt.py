import requests


def check():
    url = 'http://104.245.188.6:8000/random'
    content = requests.get(url=url).text
    print(content)
    # zhihu = 'https://www.zhihu.com/api/v4/search_v3?t=general&q=%E9%95%BF%E6%8A%95%E5%AD%A6%E5%A0%82&correction=1&offset=0&limit=10'
    zhihu = 'https://www.zhihu.com/search?type=content&q=python'
    proxies = {
        'http': 'http://' + content,
        'https': 'https://' + content,
    }
    headers={
        'User_Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        # 'referer': 'https://www.zhihu.com/search?type=content&q=%E9%95%BF%E6%8A%95%E5%AD%A6%E5%A0%82'
    }
    result = requests.get(url=zhihu, headers=headers, proxies=proxies)
    print(result.text)


if __name__ == '__main__':
    check()
