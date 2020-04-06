function formateXml(xmlStr){
    text = xmlStr;
    //使用replace去空格
    text = '\n' + text.replace(/(<\w+)(\s.*?>)/g,function($0, name, props){
        return name + ' ' + props.replace(/\s+(\w+=)/g," $1");
    }).replace(/>\s*?</g,">\n<");
    //处理注释
    text = text.replace(/\n/g,'\r').replace(/<!--(.+?)-->/g,function($0, text){
        var ret = '<!--' + escape(text) + '-->';
        return ret;
    }).replace(/\r/g,'\n');
    //调整格式  以压栈方式递归调整缩进
    var rgx = /\n(<(([^\?]).+?)(?:\s|\s*?>|\s*?(\/)>)(?:.*?(?:(?:(\/)>)|(?:<(\/)\2>)))?)/mg;
    var nodeStack = [];
    var output = text.replace(rgx,function($0,all,name,isBegin,isCloseFull1,isCloseFull2 ,isFull1,isFull2){
        var isClosed = (isCloseFull1 == '/') || (isCloseFull2 == '/' ) || (isFull1 == '/') || (isFull2 == '/');
        var prefix = '';
        if(isBegin == '!'){//!开头
            prefix = setPrefix(nodeStack.length);
        }else {
            if(isBegin != '/'){///开头
                prefix = setPrefix(nodeStack.length);
                if(!isClosed){//非关闭标签
                    nodeStack.push(name);
                }
            }else{
                nodeStack.pop();//弹栈
                prefix = setPrefix(nodeStack.length);
            }
        }
        var ret =  '\n' + prefix + all;
        return ret;
    });
    var prefixSpace = -1;
    var outputText = output.substring(1);
    //还原注释内容
    outputText = outputText.replace(/\n/g,'\r').replace(/(\s*)<!--(.+?)-->/g,function($0, prefix,  text){
        if(prefix.charAt(0) == '\r')
            prefix = prefix.substring(1);
        text = unescape(text).replace(/\r/g,'\n');
        var ret = '\n' + prefix + '<!--' + text.replace(/^\s*/mg, prefix ) + '-->';
        return ret;
    });
    outputText= outputText.replace(/\s+$/g,'').replace(/\r/g,'\r\n');
    return outputText;
}
 
//计算头函数 用来缩进
function setPrefix(prefixIndex) {
    var result = '';
    var span = '    ';//缩进长度
    var output = [];
    for(var i = 0 ; i < prefixIndex; ++i){
        output.push(span);
    }
    result = output.join('');
    return result;
}