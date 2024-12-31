import requests
import json
import pprint

API_TOKEN = ""
#53616c7465645f5fa2c45f5bfa3cd5882c10689a4e873bd61e718bd2140ad8be7f78f6964783d686bf7e2f02167b14c71d2fc377ea4f529e
if __name__ == "__main__":
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            ## 緯度・軽度を指定する場合
            "lat": "34.917082",
            "lon": "137.141676",

            ## 都市名で取得する場合
            # "q": "tokyo",

            "appid": API_TOKEN,
            "units": "metric",
            "lang": "ja",
        },
    )
    ret = json.loads(response.text)
    pprint.pprint(ret)