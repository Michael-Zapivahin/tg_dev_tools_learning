
import httpx


def get_json():
    response = httpx.get('https://www.example.org/')
    print(response.status_code)


def post_json():
    data = {'key1': ['value1', 'value2']}
    response = httpx.post("https://httpbin.org/post", data=data)
    print(response.text)



get_json()
post_json()
