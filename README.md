# iamok
华工iamok自动打卡+发送结果至邮箱

## 使用

### 使用GitHub actions

Settings-Secrets中添加

```
SNO: 学号
PASSWD: 统一认证密码
QQ: QQ
SMTP_CODE: QQ邮箱SMTP授权码
```

每天早上六点会自动打卡，也可在`Actions`选项卡中手动执行

### 本地使用

创建`.env`文件配置变量

