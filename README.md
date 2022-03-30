# 👀🪙🤣.jpg
專門看NFT的錢包哈哈.jpg

## 功能
* 查看目前最高的區塊
* 查看區塊中的所有交易
* 查看交易的內容

## 執行程式
```
flask run
```

開啟瀏覽器查看網頁  
http://localhost:5000

## 環境設置
1. 複製 `config.sample.py` 到 `config.py`。
2. 到 [Infura](https://infura.io/) 申請 API，將 Project ID 填入 `config.py` 的 `infura_project_id` 變數中。
3. 到 [Moralis](https://moralis.io/) 申請 server，將 Web3 API Key 填入 `config.py` 的 `moralis_api_key` 變數中。
4. 在 `files` 資料夾中建立 `account.json`，並在檔案中寫入 `[]`

## 使用說明
1. 使用前請先至右上方選擇網路 (預設為 Rinkeby)
2. 查詢功能可直接使用，請勿輸入錯誤的參數以免程式錯誤
3. 交易功能會動用到帳戶資產，請謹慎操作
4. 若要執行交易請先儲存錢包地址
5. NFT 查詢為獨家功能，請多加體驗！