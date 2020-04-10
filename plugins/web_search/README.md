## 搜索引擎插件
默认搜索引擎  

![](images/readme_web_search_default.gif)

搜索引擎关键字  

![](images/readme_web_search_wiki.gif)

### 插件设置

```json
{
  "proxy": {
    "http": "http://127.0.0.1:8001"
  },
  "default": {
    "engine": "google",
    "suggestion": "Google"
  },
  "engines": {
    "google": {
      "name": "Google",
      "icon": "images/web_search_google.png",
      "query": "https://www.google.com/search?q={text}",
      "home": "https://www.google.com"
    },
    "bing": {
      "name": "Bing",
      "icon": "images/web_search_bing.png",
      "query": "https://www.bing.com/search?q={text}",
      "home": "https://www.bing.com"
    }
  }
}
```
`proxy`: 设置代理，如果不需要代理，记得设为`{}`  
`default.engine`: 默认的搜索引擎，设为engines下的关键字，如`"google"`、`"bing"`  
`default.suggestion`: 搜索引擎建议，可设为`"Google"`、`"Baidu"`、`"Bilibili"`、`"知乎"`、`"Wikipedia"`  

对于每个搜索引擎的设置  
`name`:名称，可以于搜索引擎建议配对  
`icon`: 搜索引擎的图标  
`query`: 查询URL格式  
`home`: 在没有输入查询关键词，可以直接跳到搜索引擎的主页  






