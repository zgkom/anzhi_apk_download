import os
import requests
from bs4 import BeautifulSoup
import json


# 把所有分类页面内的app全部返回，限制100页
def getSoftItems(url):
    num = 1
    items = list()
    old = '_1_hot'
    session = requests.session()
    try:
        while True:
            new = '_'+str(num)+'_hot'
            url = url.replace(old, new)
            # print(url)
            html = session.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            app_names = soup.select('span.app_name>a')
            if not app_names or num >= 100:  # 最多获取100页
                break
            links = [item['href'] for item in app_names if item and 'href'in item.attrs]
            items.extend(['http://www.anzhi.com' + i for i in links])
            num = num + 1
            old = new
    except Exception as e:
        print(e)
    print("{},获取到{}连接。".format(url,len(items)))
    return items


# http://www.anzhi.com//sort_45_3_hot.html
# 获取所有分类信息，并找到所有分类的url
def getCatURL():
    url = 'http://www.anzhi.com/widgetcatetag_1.html'
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    cats = soup.select('a')
    cat_list = [i['href'] for i in cats if 'tsort' not in i['href']]
    newCat = ["http://www.anzhi.com" + i for i in cat_list]
    return newCat


# 根据 软件详情url 获得 对应的信息 json 文件
def getSoftJson(url):
    global number
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select('div.detail_line > h3')[0].text
        infos = soup.select('#detail_line_ul > li')
        soft_id = soup.select('div.detail_down > a')[0]['onclick'][9:-2]
        js = {}
        js['name'] = title
        js['cat'] = infos[0].text.split('：')[-1]
        js['download_cnt'] = infos[1].text.split('：')[-1]
        js['time'] = infos[2].text.split('：')[-1]
        js['size'] = infos[3].text.split('：')[-1]
        js['sys'] = infos[4].text.split('：')[-1]
        js['download'] = f"http://www.anzhi.com/dl_app.php?s={soft_id}&n=5"
        return js
    except Exception as e:
        print("提取json出现错误：{}".format(e))
    return None


# 返回 所有分类下的软件链接详情页面
def SaveApkToJSON(json_root_dir):
    # params: json_root_dir json文件保存根目录
    cats = getCatURL()  # 获取安智市场APK分类

    for index1, i in enumerate(cats):
        if index1 <= 7:
            continue
        all_links = getSoftItems(i)
        all_json = list()
        for index2, link in enumerate(all_links):
            print("连接下标：{}，连接：{}".format(index2, link))
            js = getSoftJson(link)
            if js:
                all_json.append(js)
        file_path = json_root_dir + "/apk_link_" + str(index1) + ".json"
        print("保存json路径，", file_path)
        with open(file_path, mode='w+') as f:
            json.dump(all_json, f, indent=4)

        print("下标{}，json保存完毕".format(index1))


# 将安智市场中的apk下载链接保存到json中
if __name__ == "__main__":
    json_root_dir = os.path.abspath(r"./json")
    if not os.path.exists(json_root_dir):
        os.makedirs(json_root_dir)
    SaveApkToJSON(json_root_dir)

