import networkx as networkx
import asyncio
import aiohttp
import requests
from collections import deque
import matplotlib.pyplot as plt

followedUrl = 'https://www.zhihu.com/api/v4/members/{0}/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset={1}&limit=20'

class UserRelations(object):
    def __init__(self, initialUserHandle):
        self.initialUserHandle = initialUserHandle
        self.users = networkx.DiGraph()
        self.users.add_node(initialUserHandle)

        self.headers = {
            'Cookie': '_zap=445937d1-de08-4554-b023-27021ef55e52; _xsrf=YSYadCTAczyMyb2k5cswC8xBbk1v5JUn; d_c0="AAAshc4bRRCPTi6_7h2dZDJ1fuXGbezYo3M=|1572295707"; z_c0="2|1:0|10:1572295750|4:z_c0|92:Mi4xUGJzT0F3QUFBQUFBQUN5RnpodEZFQ1lBQUFCZ0FsVk5ScUtrWGdENmIzS204STlYTFNjbl9UTG9wSkhlUjdtTU9R|e197d42673d230693f488079df91f91ce92b2ec8adca3e94369fa47953ea4ff4"; tshl=; q_c1=db990e03be2048fd9bd8ba05bd535f22|1574938406000|1572295781000; tst=h; tgw_l7_route=18884ea8e9aef06cacc0556da5cb4bf1; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1575286697,1575295134,1575300893,1575323803; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1575324123',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.45 Safari/537.36 Edg/79.0.309.30'
        }

        self.queue = deque()
        self.processed = dict()

    def fetchFollowedCount(self, userHandle):
        req = requests.get(followedUrl.format(userHandle, 0), headers=self.headers)
        data = req.json()
        print(data)

        if ('paging' not in data):
            return -1
        else:
            return data['paging']['totals']

    async def fetchFollowedI(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.json()

    async def fetchFollowedA(self, urls, loop):
        async with aiohttp.ClientSession(loop=loop) as session:
            results = await asyncio.gather(*[self.fetchFollowedI(session, url) for url in urls], return_exceptions=True)
            return results

    def fetchAndAddFollowedAll(self, userHandle):
        followedCount = self.fetchFollowedCount(userHandle)

        if (followedCount == -1):
            return
        times = (followedCount // 20) + 1
        urls = []

        for i in range(times + 1):
            urls.append(followedUrl.format(userHandle, i * 20))

        urls = [urls[i:i+10] for i in range(0, len(urls), 10)]

        i = 0
        for u in urls:
            loop = asyncio.get_event_loop()
            jsons = loop.run_until_complete(self.fetchFollowedA(u, loop))
            for k in jsons:
                self.addRelationsandNodes(userHandle, k)
                i += 20
                print(f"Finished {i} followees for user {userHandle}")


        self.processed[userHandle] = True

    def addRelationsandNodes(self, userHandle, data):
        data = data['data']
        for d in data:
            self.users.add_edge(userHandle, d['url_token'])
            # print(f'added {userHandle} -> {d["url_token"]}')

            if (d['url_token'] not in self.processed):
                self.queue.append(d['url_token'])
    
    def start(self):
        self.queue.append(self.initialUserHandle)

        limit = 200
        i = 0
        while len(self.queue) > 0 and i < limit:
            uH = self.queue.popleft()
            self.fetchAndAddFollowedAll(uH)
            i += 1
        


        networkx.write_graphml(self.users, 'user-relations.xml')
        # networkx.draw(self.users, with_labels=True)
        # plt.show()



if __name__ == "__main__":
    o = UserRelations('wang-rui-en')
    o.start()
