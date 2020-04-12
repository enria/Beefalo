## API插件

![Vue](images/readme_vue.gif)

### 文档设置

以Vue来举例，配置文件（./setting.json）内容为
```
   "vue": {
      "url": "https://cn.vuejs.org/v2/api/",
      "section_selector": "a.headerlink",
      "icon": "images/API_vue.png",
      "local": "C:/Users/13972/Documents/Beefalo/api/vuejs_api.html",
      "content": {
        "title": "ele.attrs['title']",
        "url": "'https://cn.vuejs.org/v2/api/'+ele.attrs['href']"
      }
    }
```
`vue`: 插件触发关键字  

`url`: 用来下载API页面的地址  

`section_selector`:  api章节的元素选择器  

`icon`:  用来显示的图标（相对于当前文件夹）  

`local`: 本地的的API页面的html文件地址，如果设置为空，则使用url进行下载，否则使用这个地址去解析，如果url方问比较慢的话，使用这种方法体验会比较好。  

`content.title`: `section_selector`选中元素中，用于显示的标题的属性  

`content.url`: `section_selector`选中元素中，用于跳转的URL  

 
