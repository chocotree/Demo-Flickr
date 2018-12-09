## 這是用來下載 Flickr相簿中的圖片

### 使用需知 :
| 必要       | 為什麼?                    | 主程式
| :---------: | :--------:            | :------:
| Python3.6以上  | 因為使用了 f-string | download_flickr.py


## 特色 :
- 可以下載到相簿中圖片的原始尺寸
- 沒有使用 [Flickr API](https://www.flickr.com/services/api/)，僅僅使用簡單網頁請求邏輯完成的
- 有些相簿不提供觀賞者直接下載，此程式依樣可以下載到高畫質原始圖檔


## 影片演示 :
- [Youtube 連結](https://www.youtube.com/watch?v=I80UWifE7fM)


## 使用方式 :
```
flickr = Flickr()
```
```
flickr.download('圖片資料夾', '相簿id', reqId='請求rest服務所需要的id')
```

***

## 遇到的問題 :
- 分析相簿網址的 html文件無法獲取所有圖片的資訊

## 如何解決 :
- 觀察ajax加載的資訊發現 restful服務網址
- 透過此 restful服務，加以利用就能順利取得所要的資源了
