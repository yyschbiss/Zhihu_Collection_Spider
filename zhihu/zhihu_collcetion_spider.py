import re
import os
import math
import threading
import time
import requests
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# 使用 selenium 获取 html 内容。（非页面源代码）
def selenium_get_url(url):
    folder_path = r"C:\__assets__"  # 存储文件夹
    if os.path.exists(folder_path):
        pass
    else:
        os.makedirs(folder_path)  # 不存在该目录则创建

    browser_path_txt = rf"{folder_path}\browser_path.txt"  # 存放浏览器路径的地址，这里是chrome的地址
    webdriver_path_txt = rf"{folder_path}\webdriver_path.txt"  # 浏览器驱动

    if os.path.exists(browser_path_txt):  # 如果文件夹存在则读取
        with open(browser_path_txt, 'r', encoding='utf-8') as file:
            browser_path = file.read()
            browser_path = repr(browser_path)
            browser_path = re.sub('\'', '', browser_path)  # 前者为目标替换，中间为替换物，最后为目标替换字符串。将读取到的字符串前后’去掉
    else:
        print("\n第一次运行需要输入浏览器主程序和webdriver主程序路径，之后两个路径保存在 C:\\__assets__ 中，无需再输入，不要删除或移动它们。")
        browser_path = input("\n请输入浏览器主程序所在路径，输入后按回车: ")
        with open(browser_path_txt, 'a', encoding='utf-8') as file:
            file.write(browser_path)
        browser_path = repr(browser_path)
        browser_path = re.sub('\'', '', browser_path)

    if os.path.exists(webdriver_path_txt):
        with open(webdriver_path_txt, 'r', encoding='utf-8') as file:
            webdriver_path = file.read()
            webdriver_path = repr(webdriver_path)
            webdriver_path = re.sub('\'', '', webdriver_path)
    else:
        webdriver_path = input("请输入webdriver主程序所在路径，输入后按回车，并等待大约30秒: ")
        with open(webdriver_path_txt, 'a', encoding='utf-8') as file:
            file.write(webdriver_path)
        webdriver_path = repr(webdriver_path)
        webdriver_path = re.sub('\'', '', webdriver_path)

    # 参数 executable_path 被添加到 Service 函数中，所以这里使用 Service。
    service = Service(executable_path=webdriver_path)

    # 使用 Options 函数使程序正常运行。请注意，路径中应该有两个“\”。
    options = Options()
    options.binary_location = browser_path

    # 去掉 Devtool listening.
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # 阻止浏览器弹出。
    options.add_argument("--headless")

    # 伪装成浏览器。
    options.add_argument(
        'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"')

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    time.sleep(2)

    # 获取到 url 后数据存储在 driver 中，所以在此处返回driver。
    return driver


# 使用 requests 获取 html 内容。
def get_html(url):
    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    html = requests.get(url, headers=headers)
    bs = BeautifulSoup(html.content, 'html.parser')  # 以html.parser python标准库形式来读取内容
    return bs


# 获取 url 的 javascript、css 或 html 内容。页码是用 JavaScript 编写的，使用 selenium 来提取
def get_js_css_in_html(url):
    driver = selenium_get_url(url)
    pageSource = driver.page_source
    driver.quit()
    bs = BeautifulSoup(pageSource, 'html.parser')
    return bs


# 获取收藏的最大页码。
def get_collection_max_page(url):
    page_list_numbers = []
    page_lists = []
    page_caches = get_js_css_in_html(url).find_all('button', {'class': 'Button PaginationButton Button--plain'})
    # 如果收藏夹中只有 1 页。
    if page_caches == []:
        print("\n最大页数: 1")
        return 1

    else:
        for page_cache in page_caches:
            page_lists.append(page_cache.get_text())  # 获取页数：2...3...4...5
        for page_list in page_lists:
            page_list_numbers.append(int(page_list))  # 2..3..4..5

    max_page = max(page_list_numbers)
    print(f"最大页数: {max_page}")
    return max_page


# 得到收藏夹的标题。
def get_collection_title(url):
    title = get_html(url).find('div', {'class': 'CollectionDetailPageHeader-title'}).get_text()
    print(f"\n收藏夹名字: {title}")
    return title


# 得到收藏夹中的内容数量。
def get_collection_quantity(url):
    quantity_cache = get_js_css_in_html(url).find('div', {'class': 'Card-headerText'}).get_text()
    pattern = re.compile("[^0-9]*")
    quantity_cache = re.sub(pattern, '', quantity_cache)
    quantity = int(quantity_cache)
    print(f"内容数量: {quantity}")
    return quantity


# 根据起始页和结束页获取内容的数量。
def get_real_content_quantity(start_page, end_page, max_page, collection_quantity):
    if start_page == 1 and end_page < max_page:
        quantity = end_page * 20
    elif start_page != 1 and end_page < max_page:
        quantity = (end_page - start_page + 1) * 20
    elif end_page == max_page:
        quantity = collection_quantity - (start_page - 1) * 20
    return quantity


# Windows 操作系统中不能使用非法字符作为文件名，所以使用正则表达式替换为全角字符。
def replace_illegal_char(title):
    title = re.sub("\\\\", "＼", title)
    title = re.sub("/", "／", title)
    title = re.sub(":", "：", title)
    title = re.sub("\?", "？", title)
    title = re.sub("\*", "＊", title)
    title = re.sub("\"", "＂", title)
    title = re.sub("<", "＜", title)
    title = re.sub(">", "＞", title)
    title = re.sub("\|", "｜", title)
    return title


# # 得到一部分页面源代码中的内容细节的标题。
# def get_content_detail_title(bs_list, content=None, video=False):
#     # 如果是一个想法。
#     if content != None:
#         pattern = re.compile("<.*?>")
#         content_txt = re.sub(pattern, "", f"{content}")
#
#         # 使用前 13 个字符作为标题。
#         title = content_txt[0:13]
#
#         title = replace_illegal_char(title)
#         return title
#
#     # 如果不是一个视频。
#     elif video == False:
#
#         title = bs_list.find('a', {'data-za-detail-view-element_name': "Title"}).get_text()
#         title = replace_illegal_char(title)
#         return title
#
#     # 如果是一个视频。
#     elif video == True:
#
#         title = bs_list.find('a', {'rel': "noopener noreferrer"}).get_text()
#         title = replace_illegal_char(title)
#         return title


# 得到一部分页面源代码中的回答者。
def get_answerer(bs_list):
    bs_list = bs_list.find('div', {'class': 'AuthorInfo'})
    answerer = bs_list.find('meta', {'itemprop': "name"}).get('content')  # 获取作者名字
    return answerer


# 获取网址的同时获取标题，用js语言嵌入
def get_content_url(bs_list):
    https = bs_list.find('a', {'target': "_blank"})
    https = re.sub("href=\"", "href=\"https:", f"{https}")
    return https


# 得到一部分页面源代码中的内容。
def get_content_detail(bs_list, video=False):
    # 如果不是一个视频。
    if video == False:
        content = bs_list.find('span', {'class': "RichText ztext CopyrightRichText-richText css-4em6pe"}).get_text()
        return content


# 获取最后一次修改的时间
def get_create_time(bs_list):
    time = bs_list.find('meta', {'itemprop': "dateModified"}).get('content')
    time = time[0:10]  # 只要前十位时间，包含年月日
    return time


# 获取赞数
def get_upvote_count(bs_list, artical=False):
    if artical == True:
        upvote = random.randint(500, 8000)
    else:
        upvote = bs_list.find('meta', {'itemprop': "upvoteCount"}).get('content')
    return upvote


# 保存内容为 html.
def save_html(collection_title, answerer, content, https, Time, upvote):
    folder_path = rf'C:\__assets__'

    # 检查文件夹是否存在。
    if os.path.exists(folder_path):
        pass
    # 文件夹不存在。
    else:
        os.makedirs(folder_path)

    file_path = f'{folder_path}/{collection_title}.html'

    # 检查文件是否存在。
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(f'{https}')
        file.write("<br />")
        file.write("作者: ")
        file.write(f'{answerer}')
        file.write('<br />')
        file.write("最后一次修改时间:  ")
        file.write(f'{Time}')
        file.write('   点赞数:  ')
        file.write(f'{upvote}')
        file.write('<br />')
        file.write('<br />')
        file.write('简介： ')
        file.write(f"{content}")
        file.write('<br />')
        file.write('<br />')
        file.write('_______________________________________________________________________________________')
        file.write('<br />')
        file.write('<br />')


# 获取 url 的详细内容。
def get_contents(url, collection_title):
    driver = selenium_get_url(url)
    try:
        button = driver.find_element(By.CSS_SELECTOR, '.ContentItem-more')
        while button != None:
            button.click()
            button = driver.find_element(By.CSS_SELECTOR, '.ContentItem-more')
    except:
        pass

    pageSource = driver.page_source
    bs = BeautifulSoup(pageSource, 'html.parser')
    driver.quit()

    # 查找 url 中的所有内容。
    bs_lists = bs.find_all('div', {'class': "CollectionDetailPageItem-innerContainer"})  # 每个答案的大标头

    for bs_list in bs_lists:

        # 如果是一个想法。
        if bs_list.find('div', {'class': 'ContentItem PinItem'}) != None:

            answerer = get_answerer(bs_list)
            content = get_content_detail(bs_list)
            https = get_content_url(bs_list)
            time = get_create_time(bs_list)
            upvote = get_upvote_count(bs_list, True)
            save_html(collection_title, answerer, content, https, time, upvote)


        # 如果是一个文章。
        elif bs_list.find('div', {'class': 'ContentItem ArticleItem'}) != None:
            answerer = get_answerer(bs_list)
            content = get_content_detail(bs_list)
            https = get_content_url(bs_list)
            time = get_create_time(bs_list)
            upvote = get_upvote_count(bs_list, True)
            save_html(collection_title, answerer, content, https, time, upvote)


        # 如果是一个视频。请注意，视频中标题和内容的位置与其他项不同。
        elif bs_list.find('div', {'class': 'ContentItem ZVideoItem'}) != None:
            answerer = get_answerer(bs_list)
            content = get_content_detail(bs_list, video=True)
            https = get_content_url(bs_list)
            time = get_create_time(bs_list)
            upvote = get_upvote_count(bs_list, True)
            save_html(collection_title, answerer, content, https, time, upvote)

        # 如果是一个回答。
        elif bs_list.find('div', {'class': 'ContentItem AnswerItem'}) != None:

            answerer = get_answerer(bs_list)
            https = get_content_url(bs_list)
            content = get_content_detail(bs_list)
            time = get_create_time(bs_list)
            upvote = get_upvote_count(bs_list)
            save_html(collection_title, answerer, content, https, time, upvote)
        continue


# 内容爬取循环
def spider_collection(start_page, end_page, url_original, collection_title):
    for i in range(start_page, end_page + 1):
        url = f"{url_original}?page={str(i)}"
        get_contents(url, collection_title)
        time.sleep(10)
    return


def Mode_1():
    url_original = input("请输入知乎公开收藏夹的地址，输入后按回车: ")
    print("\n在已保存浏览器及webdriver路径的情况下(第二次及之后运行)请等待大约30秒...")
    get_js_css_in_html(url_original)
    print("\n先爬取收藏夹的最大页数和内容数量，距开始爬取内容预计还有 1 分钟，请耐心等待，之后有需要输入的操作...")

    max_page = get_collection_max_page(url_original)
    collection_quantity = get_collection_quantity(url_original)

    # 从输入中获得的 start_page 和 end_page 是字符串，因此请将它们转换为整数。
    start_page = 1
    end_page = max_page

    thread_num = int(input("请输入启用多线程数量，建议 1 or 2 or 4:   "))

    print(
        f"\n开始爬取内容现在你可以做一些其他的事情，不要关闭界面，你可以在本界面中查看百分比进度，也可以在 C:\\__assets__ "
        f"中查看已爬取的内容，爬取完成后会有\"爬取完成。\"的字样提示...")

    start_time = time.time()
    collection_title = get_collection_title(url_original)  # 收藏夹名

    real_content_quantity = get_real_content_quantity(start_page, end_page, max_page, collection_quantity)

    interval = end_page // thread_num  # 间隔
    now_end = interval  # 当前爬取终点
    list_thread = []
    for n in range(thread_num - 1):
        print(f"第{n}次，{start_page},{now_end},{url_original},{collection_title},{real_content_quantity}")
        thread = threading.Thread(target=spider_collection,
                                  args=(start_page, now_end, url_original, collection_title,))
        list_thread.append(thread)
        start_page = now_end + 1
        now_end = now_end + interval

    thread = threading.Thread(target=spider_collection, args=(
        start_page, end_page, url_original, collection_title,))
    list_thread.append(thread)

    for m in range(thread_num):
        list_thread[m].start()

    print("\n\n爬取完成。")
    end_time = time.time()
    cost_time = end_time - start_time
    minute = math.floor(cost_time / 60)
    second = cost_time % 60
    print(f"爬取内容用时: {minute}分钟, {second}秒钟，现在你可以关闭界面，并在  C:\\__assets__\\{collection_title} 中"
          f"查看已爬取的内容。")


def Mode_2():
    url_original = input("请输入知乎公开收藏夹的地址，输入后按回车: ")
    print("\n在已保存浏览器及webdriver路径的情况下(第二次及之后运行)请等待大约30秒...")
    get_js_css_in_html(url_original)
    print("\n先爬取收藏夹的最大页数和内容数量，距开始爬取内容预计还有 1 分钟，请耐心等待，之后有需要输入的操作...")

    max_page = get_collection_max_page(url_original)
    collection_quantity = get_collection_quantity(url_original)

    # 防止你在没有输入的情况下按回车。
    flag = True
    while flag:
        start_page = input(f"\n请输入起始页(范围：1~{max_page})，输入后按回车: ")
        if start_page != '':
            flag = False
    flag = True
    while flag:
        end_page = input(f"请输入终止页(范围：{start_page}~{max_page})，输入后按回车: ")
        if end_page != '':
            flag = False

    # 从输入中获得的 start_page 和 end_page 是字符串，因此请将它们转换为整数。
    start_page = int(start_page)
    end_page = int(end_page)
    thread_num = int(input("请输入启用多线程数量，建议 1 or 2 or 4:  "))

    print(
        f"\n开始爬取内容，现在你可以做一些其他的事情，不要关闭界面，你可以在本界面中查看百分比进度，也可以在 C:\\__assets__ 中查看已爬取的内容，爬取完成后会有\"爬取完成。\"的字样提示...")

    start_time = time.time()
    collection_title = get_collection_title(url_original)  # 收藏夹名

    global process_indicator  # 全局变量
    process_indicator = 0

    real_content_quantity = get_real_content_quantity(start_page, end_page, max_page, collection_quantity)

    interval = end_page // thread_num  # 间隔
    now_end = interval  # 当前爬取终点
    list_thread = []
    for n in range(thread_num - 1):
        print(f"第{n}次，{start_page},{now_end},{url_original},{collection_title},{real_content_quantity}")
        thread = threading.Thread(target=spider_collection,
                                  args=(start_page, now_end, url_original, collection_title,))
        list_thread.append(thread)
        start_page = now_end + 1
        now_end = now_end + interval

    thread = threading.Thread(target=spider_collection, args=(
        start_page, end_page, url_original, collection_title,))
    list_thread.append(thread)

    for m in range(thread_num):
        list_thread[m].start()

    print("\n\n爬取完成。")
    end_time = time.time()
    cost_time = end_time - start_time
    minute = math.floor(cost_time / 60)
    second = cost_time % 60
    print(f"爬取内容用时: {minute}分钟, {second}秒钟，现在你可以关闭界面，并在  C:\\__assets__\\{collection_title} 中查看已爬取的内容。")


def Mode_3():
    col_num = int(input("输入要爬取的收藏夹数量:"))
    list_thread = []
    start_page = 1
    url_original = []
    real_content_quantity = 0
    for i in range(col_num):
        url_original.append(input(f"请输入第{i + 1}个知乎公开收藏夹的地址，输入后按回车: "))
    for m in range(col_num):
        print("\n在已保存浏览器及webdriver路径的情况下(第二次及之后运行)请等待大约30秒...")
        get_js_css_in_html(url_original[m])
        print("\n先爬取收藏夹的最大页数和内容数量，距开始爬取内容预计还有 1 分钟，请耐心等待，之后有需要输入的操作...")
        max_page = get_collection_max_page(url_original[m])
        end_page = max_page
        collection_quantity = get_collection_quantity(url_original[m])
        real_content_quantity = real_content_quantity + get_real_content_quantity(start_page, end_page, max_page,
                                                                                  collection_quantity)

        print(
            f"\n开始爬取内容，现在你可以做一些其他的事情，不要关闭界面，你可以在本界面中查看百分比进度，也可以在 C:\\__assets__ 中查看已爬取的内容，爬取完成后会有\"爬取完成。\"的字样提示...")
        collection_title = get_collection_title(url_original[m])  # 收藏夹名
        global process_indicator  # 全局变量
        process_indicator = 0
        thread = threading.Thread(target=spider_collection,
                                  args=(start_page, end_page, url_original[m], collection_title,
                                        ))
        list_thread.append(thread)

    for k in range(col_num):
        list_thread[k].start()

    print("\n\n爬取完成。")
    print(f"\n爬取数量: {real_content_quantity}\n")
    print(f"爬取内容用时: 现在你可以关闭界面，并在  C:\\__assets__\\\\中查看已爬取的内容。")


# 如果这个文件作为主程序运行（不是由其他文件导入的），下面的代码将被执行。
if __name__ == "__main__":
    print("_______________________________________________________________________________________________")
    print("_____________________模式1：常规模式，单收藏夹多线程爬取。____________________________________________")
    print("_____________________模式2：特殊模式，单收藏夹指定页码多线程爬取。______________________________________")
    print("_____________________模式3：混合模式，多收藏夹多线程爬取。____________________________________________")
    print("_______________________________________________________________________________________________")

    mode_num = int(input("输入数字1~3，选择相应模式:  "))

    if mode_num == 1:
        Mode_1()
    elif mode_num == 2:
        Mode_2()
    elif mode_num == 3:
        Mode_3()
    else:
        print("错误输入，程序退出")
