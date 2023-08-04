import requests
from bs4 import BeautifulSoup
from pathlib import Path
import tkinter as tk
import PIL.Image
import PIL.ImageTk
import glob




# 検索画面から詳細画面のリンクを全て取得し、resultに格納
def readResult(url, result):

    html = requests.get(url)
    content = BeautifulSoup(html.content, "html.parser")

    for element in content.find_all(class_="box"):

        detailUrl = element.find("a").get("href")
        result.add(detailUrl)

    return result

# 詳細URLを引数で１つ受け取り、画像ページのURLを返す
def getImageUrl(detailsUrl):
    # 詳細ページにあるaタグの画像urlをセットで保存
    linkSet = set()

    html = requests.get(detailsUrl)
    content = BeautifulSoup(html.content, "html.parser")
    entry = content.find(class_="entry")

    for a in entry.find_all("a"):
        link = a.get("href")
        # downloadImage関数でlinkにアクセルするためhttps:がついていないリンクにはhttpsをつける
        if not link.startswith("https:"):
            link = "https:" + link

        linkSet.add(link)

    return linkSet

# 引数でgetImage関数から詳細ページから取得した画像ページのurlを取得(linkSetはセット型)
def downloadImage(linkSet):

    for imageURL in linkSet:

        imageData = requests.get(imageURL)

        out_folder = Path("tkImage")
        # フォルダを作成
        out_folder.mkdir(exist_ok=True)
#       ファイル名を指定
        filename = imageURL.split("/")[-1]
        out_path = out_folder.joinpath(filename)

#         画像をダウンロード
        with open(out_path, mode="wb") as f:
            f.write(imageData.content)

# 次へボタンがあるか判断し、なければfalseを返す
def hasNext(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")
    judge = soup.find(id="blog-pager-older-link")

#     次へボタンが存在するか判定
    if judge is None:
        return False
    else:
        return True

# urlを次のページにこうしんする関数
def getNextURL(url):
    html = requests.get(url)
    soup = BeautifulSoup(html.content, "html.parser")

    nextURL = soup.find(id="blog-pager-older-link").find("a").get("href")

    return nextURL

# 画像を検索し、ダウンロードを開始する関数
def start(url):
    # 最終ページになるまで画像をダウンロードし続ける
    while True:

        flag = hasNext(url)

        # 次へボタンがある時
        if flag:

            result = set()

            readResult(url, result)

            for u in result:
                links = getImageUrl(u)
                downloadImage(links)
            url = getNextURL(url)

        else:
            frameChange("homeFrame")
            break

# ラジオボタンで指定した通りに画像を加工する
def arrange():
    file_list = glob.glob("tkImage/*.png")
    match v.get():
        case "グレー":
            for path in file_list:
                newImage = PIL.Image.open(path).convert("L")
                newImage.save(path)
        case "モザイク":
            for path in file_list:
                newImage = PIL.Image.open(path).resize((32,32)).resize((300,300))
                newImage.save(path)
        case _:
            pass
    frameChange("radioFrame")

# フレームを切り替える
def frameChange(flameName):

    match flameName:
        case "homeFrame":
            homeFrame.destroy()

            # ラジオボタン
            nomal = tk.Radiobutton(radioFrame, text="変換なし", variable=v, value="変換なし")
            gray = tk.Radiobutton(radioFrame, text="グレー", variable=v, value="グレー")
            mosaic = tk.Radiobutton(radioFrame, text="モザイク", variable=v, value="モザイク")
            # 決定ボタン
            lock = tk.Button(radioFrame,text="この形式に変換", command=arrange)

            radioFrame.pack()
            nomal.pack()
            gray.pack()
            mosaic.pack()
            lock.pack()

        case "radioFrame":
            radioFrame.destroy()

            label = tk.Label(endFrame,text="完了しました。ご利用ありがとうございました")
            endFrame.pack()
            label.pack()

        case _:
            pass

url = "https://www.irasutoya.com/search?q=%E6%80%92%E3%82%8B"

root = tk.Tk()
root.geometry('500x500')

# ダウンロード用のフレームを用意
homeFrame = tk.Frame(root)
# ラジオボタン用のフレームを用意
radioFrame = tk.Frame(root)
# 終了用のフレームを用意
endFrame = tk.Frame(root)
homeFrame.pack()

# ボタン作成
message = tk.StringVar()
message.set("画像をダウンロード")
btn = tk.Button(homeFrame,textvariable=message, command=lambda:start(url))
btn.pack()

# ラジオボタンのデータ格納先
v = tk.StringVar()
v.set("ダウンロード方法を選択してください")

root.mainloop()