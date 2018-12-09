import requests
from bs4 import BeautifulSoup
import re
import os
import json
import numpy as np


class Flickr():
    '''
        下載flickr相簿中的圖片
    '''

        # 讓對方伺服器知道送出request請求的裝置
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    flag = {}
        # 不下載最大尺寸的圖片 --> 初始為 False
    flag['donot_use_cdn_o'] = False
        # 終止程式 --> 初始為 False
    flag['stop'] = False
        # 所下載的圖片數量
    _img_number = 0
        
        # per_page, page, photoset_id, reqId 都是根據其網頁 Restful服務所命名的
        # 取得圖片網址URL
    def flickr_restful(self, album_name, per_page, page, photoset_id, reqId):
        '''
            從Restful服務中獲取資料
        '''

            # 建立存放圖片的資料夾
        os.makedirs(f'flickr_imgs/{album_name}', exist_ok=True)

            # 這是flickr在網頁相簿中呼叫的rest服務，透過這個網址可以取得 "圖片的URL"
            # 但是 reqId 類似它的api key，會過期，所以要先去flickr網站裡面研究
        url = f'https://api.flickr.com/services/rest?extras=can_addmeta%2Ccan\
_comment%2Ccan_download%2Ccan_share%2Ccontact%2Ccount_comments%2\
Ccount_faves%2Ccount_views%2Cdate_taken%2Cdate_upload%2Cdescription\
%2Cicon_urls_deep%2Cisfavorite%2Cispro%2Clicense%2Cmedia%2Cneeds_\
interstitial%2Cowner_name%2Cowner_datecreate%2Cpath_alias%2Crealname\
%2Crotation%2Csafety_level%2Csecret_k%2Csecret_h%2Curl_c%2Curl_f\
%2Curl_h%2Curl_k%2Curl_l%2Curl_m%2Curl_n%2Curl_o%2Curl_q%2Curl_s\
%2Curl_sq%2Curl_t%2Curl_z%2Cvisibility%2Cvisibility_source%2Co_dims\
%2Cpubliceditability&per_page={per_page}&page={page}&get_user_info=1\
&primary_photo_extras=url_c%2C%20url_h%2C%20url_k%2C%20url_l%2C\
%20url_m%2C%20url_n%2C%20url_o%2C%20url_q%2C%20url_s%2C%20url_sq\
%2C%20url_t%2C%20url_z%2C%20needs_interstitial%2C%20can_share\
&jump_to=&photoset_id={photoset_id}&viewerNSID=&method=flickr.\
photosets.getPhotos&csrf=&api_key=c5ee5beba0b0061d7eaf7975e94b22aa\
&format=json&hermes=1&hermesClient=1&reqId={reqId}&nojsoncallback=1'

            # 把url交給requests處理
        res = requests.get(url, headers=Flickr.headers)
        res.encoding = 'utf-8'

            # 把回傳的資料透過 json來解析 轉成python可處理的 list或 dict格式
        datas = json.loads(res.text)
        try:
                # 取出想要的資訊
            datas = datas['photoset']['photo']
        except KeyError:
            print('\n\tStop the program!\n')
                # 找不到資訊了， (1) 下載圖片完成， (2)或者是 api key有問題
            Flickr.flag['stop'] = True
                # 停止程式
            return 0

            # 用for迴圈 將json格式的資料裡面的圖片URL找出來
        for data in datas:

                # 因為每個相簿裡面的原始圖片資料格式不盡相同，
                # 如果圖片檔案超過 2mb，就不下載 original的尺寸
                # o, k, l, c 等等尺寸定義請研究flickr網站下載圖片的尺寸
            if Flickr.flag['donot_use_cdn_o']:
                img_url = None

                # 如果此相簿找不到大尺寸的圖片，只好下載尺寸較小的圖片
            else :
                img_url = data.get('url_o_cdn')
            if not img_url:
                img_url = data.get('url_k_cdn')
            if not img_url:
                img_url = data.get('url_l_cdn')
            if not img_url:
                img_url = data.get('url_c_cdn')

                # 儲存圖片
            Flickr._img_number += 1
            Flickr.save_img(self, img_url, album_name, original_cdn=data)

        
    def save_img(self, img_url, album_name, original_cdn):
        '''
            得到圖片網址後，將其下載
        '''

            # 從網址中擷取部分文字當作檔名
        name = re.findall(r'_\w+_?', img_url)[0][2:-2]

            # 將圖片網址交給 requests處理
        res = requests.get(img_url, headers=Flickr.headers)
        img_bytes = res.content

            # 將 binary資料轉換成 numpy array 判斷資料大小
        img = np.frombuffer(img_bytes, dtype=np.uint8)

            # 判斷圖片是否大於 2mb，如果超過，不會下載 original尺寸
        if img.shape[0] > 2000000:
            # 不要下載 original尺寸 設為 True
            Flickr.flag['donot_use_cdn_o'] = True
                # 這張圖片再找一下一個尺寸的圖檔
            img_url = original_cdn.get('url_k_cdn')
            res = requests.get(img_url, headers=Flickr.headers)
            img_bytes = res.content

            # 將圖片資訊寫進檔案裡， 並存成 jpg格式
        with open(f'flickr_imgs/{album_name}/{name}.jpg', 'wb') as f:
            f.write(img_bytes)
        print(f'save the img: {Flickr._img_number} name: {name}.jpg')


                    # 新建資料夾名稱   此相簿的id  請求 api的 id
    def download(self, album_name, photoset_id, reqId):
        '''
        根據rest服務，用無限loop 去下載相簿中的圖片，直到相簿被下載完成
        '''
        print(Flickr.__doc__)
        count = 1
        while 1:
            if Flickr.flag['stop']:
                break
            page = str(count)
            Flickr.flickr_restful(self, album_name=album_name, per_page='50',
                             page=page, photoset_id=photoset_id, reqId=reqId
                             )
            count += 1


    # ---- 使用方式 ----
flickr = Flickr()
flickr.download('沖繩暫時存圖', '72157685891272174', reqId='65a36c77')

