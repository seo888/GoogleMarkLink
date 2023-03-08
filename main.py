"""自动获取谷歌外推链接"""

import linecache
import threading
import random
import httpx
from fatgoose3 import FatGoose


class GoogleMark():
    """自动获取谷歌外推链接"""

    def __init__(self, verify_word):
        self.verify_word = verify_word
        self.targets = [
            "http://tools.ezseo.cn",
            "http://tools1.ezseo.cn",
            "http://tools2.ezseo.cn",
            "http://tools3.ezseo.cn",
            "http://tools4.ezseo.cn",
            "http://tools5.ezseo.cn",
            "http://tools6.ezseo.cn",
            "http://tools7.ezseo.cn",
            "http://tools8.ezseo.cn",
            "http://tools9.ezseo.cn",
        ]
        self.goose = FatGoose()
        self.google_ok_links = []

    def update_ok_links(self):
        """待验证链接进行去重"""
        google_ok_links = [i.strip()
                           for i in linecache.getlines('g_verify.txt')]
        self.google_ok_links = list(set(google_ok_links))

    def verify_link(self, keyword, link_url, tname):
        """验证是否为可以外推链接"""
        headers = {
            "User_Agent": 'Mozilla/5.0 (compatible; Baiduspider/2.0;'
            '+http://www.baidu.com/search/spider.html)'
        }
        resp = httpx.get(link_url, headers=headers, timeout=30)
        news = self.goose.extract(url=link_url, raw_html=resp.text)
        if keyword in news.title:
            print(f"[{tname}] ok", link_url, f"\n{news.title}\n")
            with open('google.txt', 'a', encoding='utf-8') as txt_f:
                txt_f.write(link_url.replace(keyword, '') + '\n')
            return True
        print(f"[{tname}] ❌", link_url,  f"\n{news.title}\n")
        return False

    def filter_link(self, keyword, link):
        """获取待验证链接"""
        f_links = link.split('/')
        link_is_ok = 0
        input_index = 0
        for input_index, i in enumerate(link.split('/')):
            if keyword in i:
                if "=" in i:
                    f_links[input_index] = i.split(
                        "=")[0] + f"={self.verify_word}"
                else:
                    f_links[input_index] = self.verify_word
                link_is_ok = 1
                break
        f_links = f_links[:input_index+1]
        if link_is_ok:
            ok_link = "/".join(f_links)
            print(ok_link)
            with open('g_verify.txt', 'a', encoding='utf-8') as txt_f:
                txt_f.write(ok_link + '\n')

    def get_ok_link(self, kword):
        """主程"""
        target = random.choice(self.targets)
        url = f'{target}/google/ban?q={kword}'
        resp = httpx.get(url)
        result = resp.json()
        # print(result)
        allowed_title = result['allowed_title']
        disallowed_title = result['disallowed_title']
        inner_page_title = result['inner_page_title']
        titles = allowed_title + disallowed_title + inner_page_title
        for i in titles:
            if len(i) == 8:
                self.filter_link(kword, i[-1])

    def thread_go(self, tname, verify_word):
        """线程"""
        while len(self.google_ok_links) > 0:
            # lock.acquire()
            with lock:
                link = self.google_ok_links.pop(0)
            # lock.release()
            try:
                self.verify_link(verify_word, link, tname)
            except Exception as err:
                print(err)


if __name__ == '__main__':
    clear = input('是否清空g_verify.txt 中的待验证的链接 y/n :')
    s = [i.strip() for i in linecache.getlines('keywords.txt')]
    VWORD = '这是一段很长的测试句子-用来测试目标网站的标题是否能正确显示提交的文本'
    GM = GoogleMark(VWORD)

    if clear == 'y':
        with open('g_verify.txt', 'w', encoding='utf-8') as file:
            file.write('')
        print('g_verify.txt 已清空')
    # 扫描符合格式的url
    for index, kw in enumerate(s):
        try:
            print(f"[{index+1}/{len(s)}] {kw}")
            GM.get_ok_link(kw)
        except Exception as e:
            print(e)
    print('\n================开始验证外推链接================\n')
    GM.update_ok_links()
    lock = threading.Lock()
    threads = [threading.Thread(target=GM.thread_go, args=(
        f"t{i}", VWORD)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    google_txt = list(set([i.strip()
                      for i in linecache.getlines('google.txt')]))
    with open('google.txt', 'w', encoding='utf-8')as file:
        file.write("\n".join(google_txt)+"\n")
