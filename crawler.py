import requests
import csv
import sys
from datetime import datetime
import codecs
import time

columnsName = ['crawledDateTime', 'id', 'trendingCount', 'title', 'createdDateTime', 'commentCount', 'followerCount', 'answerCount']
url = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.45 Safari/537.36 Edg/79.0.309.30',
    'accept-language': 'zh-Hans-GB,zh-CN;q=0.9,zh;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5,zh-TW;q=0.4',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}

def getData():
    ret = []

    req = requests.get(url, headers=headers)
    reqJson = req.json()

    dataJson = reqJson['data']

    now = datetime.utcnow().isoformat()

    for d in dataJson:
        t = []

        t.append(now)
        t.append(d['target']['id'])
        t.append(int(d['detail_text'].split()[0]))
        t.append(d['target']['title'])
        t.append(datetime.utcfromtimestamp(d['target']['created']).isoformat())
        t.append(d['target']['comment_count'])
        t.append(d['target']['follower_count'])
        t.append(d['target']['answer_count'])

        ret.append(t)
    
    return ret


def start(fileName, sleepTime):
    with codecs.open(fileName, 'a+', 'utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        csv_writer = csv.writer(csv_file)

        if (csv_reader.line_num == 0):
            csv_writer.writerow(columnsName)

        while True:

            rt = getData()
            csv_writer.writerows(rt)
            csv_file.flush()
            time.sleep(sleepTime)


if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Output file name required", file=sys.stderr)
        sys.exit(1)



    fileName = sys.argv[1]
    sleepTime = sys.argv[2] if len(sys.argv) == 3 else 60
    start(fileName, sleepTime)