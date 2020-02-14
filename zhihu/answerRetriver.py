import requests
import asyncio
import aiohttp
from datetime import datetime
import time
from bs4 import BeautifulSoup


url = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=20&offset={1}&platform=desktop&sort_by=default'

class AnswerRetriver(object):
    def __init__(self, answerId, cookie, includeContent=False):
        self.includeContent = includeContent
        self.answerId = answerId
        self.cookie = cookie
        self.headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.45 Safari/537.36 Edg/79.0.309.30'
        }

        self.answersCount = self.getAnswersCount()
        self.answers = dict()


    async def fetch(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.json()

    async def fetch_all(self, urls, loop):
        async with aiohttp.ClientSession(loop=loop) as session:
            results = await asyncio.gather(*[self.fetch(session, url) for url in urls], return_exceptions=True)
            return results


    def start(self):
        times = (self.answersCount // 20) + 1
        urls = []

        for i in range(times + 1):
            urls.append(url.format(self.answerId, i * 20))

        urls = [urls[i:i+5] for i in range(0, len(urls), 5)]
        i = 0
        for u in urls:
            loop = asyncio.get_event_loop()
            jsons = loop.run_until_complete(self.fetch_all(u, loop))
            for k in jsons:
                self.extractAnswers(k)
                i += 20
                print(f"Finished {i} answers", len(self.answers))

            



    def getAnswersCount(self):
        req = requests.get(url.format(self.answerId, 0), headers=self.headers)
        reqJson = req.json()

        return int(reqJson['paging']['totals'])



    def extractAnswers(self, jsonResponse):
        
        now = datetime.utcnow().isoformat()

        for a in jsonResponse['data']:
            if a['id'] in self.answers:
                continue

            del a['type']
            a['question_id'] = a['question']['id']
            del a['question']
            del a['author']['avatar_url']
            del a['author']['avatar_url_template']
            del a['author']['url']
            del a['url']
            del a['is_collapsed']
            a['created_time'] = datetime.utcfromtimestamp(a['created_time']).isoformat()
            a['updated_time'] = datetime.utcfromtimestamp(a['updated_time']).isoformat()
            del a['suggest_edit']
            del a['reward_info']
            del a['excerpt']
            a['crawled_time'] = now

            if (self.includeContent):
                soup = BeautifulSoup(a['content'])
                a['content'] = soup.get_text()
            else:
                del a['content']

            self.answers[a['id']] = a



    


if __name__ == "__main__":
    cookie = '_zap=445937d1-de08-4554-b023-27021ef55e52; _xsrf=YSYadCTAczyMyb2k5cswC8xBbk1v5JUn; d_c0="AAAshc4bRRCPTi6_7h2dZDJ1fuXGbezYo3M=|1572295707"; z_c0="2|1:0|10:1572295750|4:z_c0|92:Mi4xUGJzT0F3QUFBQUFBQUN5RnpodEZFQ1lBQUFCZ0FsVk5ScUtrWGdENmIzS204STlYTFNjbl9UTG9wSkhlUjdtTU9R|e197d42673d230693f488079df91f91ce92b2ec8adca3e94369fa47953ea4ff4"; tshl=; q_c1=db990e03be2048fd9bd8ba05bd535f22|1574938406000|1572295781000; tst=h; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1575223528,1575223626,1575238284,1575286697; tgw_l7_route=7f546500f1123d2f6701ac7f30637fd6; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1575288417'
    o = AnswerRetriver(358967893, cookie, True)
    o.start()

    answers = o.answers.values()

    import json
    with open('answers-358967893-12-2-19-42.json', 'w', encoding='utf-8') as f:
        json.dump(list(answers), f, ensure_ascii=False, indent=4)
