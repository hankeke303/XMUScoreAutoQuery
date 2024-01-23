# 厦门大学成绩自动查询脚本

一个可以用来自动查询厦门大学学生成绩的 Python 小程序。

## 简介

本脚本基于 Python3 的 `requests` 功能，实现了自动查询成绩，并支持使用系统通知或邮件进行推送。

## 免责声明

本项目是 Inorka 用于练习 Python 以及一些有趣的库而创建的，因为 Inorka 觉得这个项目非常有趣，因此将之开源，请勿用于其它用途，若产生任何后果（包括统一身份认证账号被冻结、被学校或辅导员请喝茶、查询出来错误的成绩导致的情绪波动），Inorka 不负任何责任。

## 安装

首先，您需要将这个项目克隆至本地，想必这个过程并不需要提及。（提示：`git clone https://github.com/Inorka/XMUScoreAutoQuery`）

然后，您需要使用下面的命令安装依赖：

```shell
pip3 install -r requirements.txt
```

对于 MacOS 用户，如果您希望使用系统通知推送，那么您还需要安装 `pyobjus`：

```shell
pip3 install pyobjus
```

## 配置

主要的配置文件位于 `config.yaml` 中，首先你需要将我们提供的 `config.yaml.example` 复制一份，并命名为 `config.yaml`：

```shell
cp config.yaml.example config.yaml
```

然后，您需要补全 `config.yaml` 中的内容，让我们看一下这个文件的内容：

```yaml
info:
  username:       # 用户名（你的学号）
  password:       # 密码
interval: 10      # 检查间隔（分钟）
terms:            # 学期（格式：2022-2023学年 第一学期），留空则为查询所有
  # - 2023-2024学年 第一学期
courses:          # 课程（可以为课程号也可以是课程名），留空则为查询所有
  # 
notify: system    # 通知方式（system: 系统通知，email: 邮件通知，both: 全部使用，留空则不通知）
email:            # 邮件通知配置
  host:           # SMTP 服务器地址
  port:           # SMTP 服务器端口
  username:       # SMTP 用户名
  password:       # SMTP 密码
  use_ssl: false  # 是否使用 SSL
  receiver:       # 收件人（留空则默认与 username 相同）
show_score: true # 是否在推送中显示成绩
```

大部分配置的作用已经在注释中说明了，只有下面几个点需要注意：

- 系统通知的推送样式与新版的 QQ 消息通知类似，MacOS 系统上的表现为在右上角突然出现并停留几秒后滑出，Windows 应该是右下角。
- 邮件通知的方式是使用 SMTP 服务发送邮件，因此需要您配置 SMTP 服务的服务器、端口、账户等，具体可以查看您使用的邮箱的说明：
    - 对于 SMTP 服务器的域名地址、端口号、是否使用 SSL，一般可以在邮箱帮助中 POP3/IMAP/SMTP 的说明中找到，如 QQ 邮箱的[说明](https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode)、163 邮箱的[说明的第六条](https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2a5feb28b66796d3b)，XMU 邮箱的[说明](https://net.xmu.edu.cn/info/1011/1045.htm)。
    - 对于 SMTP 服务的账户，一般来说用户名与您使用的邮箱地址相同，而密码有可能相同，也有可能是您单独设置的授权码，一般来说需要您开启 SMTP/IMAP 服务，并设置至少一个授权码后才能使用。以 QQ 邮箱为例，可以在「设置-账户-POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」中管理。
- 配置文件中的 `receiver` 接收人，指的是您需要将这个成绩提醒邮件发送给谁。这里填写的应该是一个或多个邮箱地址，如果不填则默认发送给自己。

## 使用

运行 `app.py` 即可开始运行：

```shell
python3 app.py
```

通常来说，这个脚本开始运行后会立刻进行一次成绩查询，如果您之前没有运行过脚本（即没有生成 `scores.yaml` 成绩缓存文件），那么第一次成绩查询会存储您所有的成绩，并立刻进行一次推送。

由于 `jw.xmu.edu.cn` 的服务器似乎延迟很高，而且交互的数据量也挺大的，所以每次查询可能需要挺长时间（至少 5s），不过对于后台查询并推送来说，这个时间想必可以接受。

提示：你可能觉得在推送中直接显示成绩太恐怖了，因此我们提供了 `show_score` 的配置，如果为 `false`，那么推送通知中将不会显示具体的成绩。

## 注意

1. 重复：本项目是 Inorka 用于练习 Python 以及一些有趣的库而创建的，因为 Inorka 觉得这个项目非常有趣，因此将之开源，请勿用于其它用途，若产生任何后果（包括统一身份认证账号被冻结、被学校或辅导员请喝茶、查询出来错误的成绩导致的情绪波动），Inorka 不负任何责任。
2. 请注意，短时间内太多次通过统一身份认证进行登录，会引起账号的冻结，一般来说过一会儿就可以恢复，但是为了保险起见，请您不要删除 `Cookie.txt`，这个文件缓存了之前使用的 Cookie，如果缺失 Cookie 会重新登录。
3. 一般来说，个人的主机或者笔记本都有自动休眠的功能，因此如果您将脚本挂载自己的主机或笔记本上，休眠期间不会运行脚本。因此如果希望在您没有使用电脑期间脚本也能工作，建议您使用云服务器或者其它独立的不休眠主机运行。
4. 系统通知由于内容大小限制，如果短时间内出分的课程数过多，那么可能会无法完全输出（而您点击这个通知并不能跳转到完整的内容）。因此建议您使用邮件推送的方式，或者在收到通知后直接打开 jw.xmu.edu.cn 查看。

## 参考

本项目中 `login.py` 和 `utils.py` 参考了 kirainmoe 学长的[健康打卡脚本](https://github.com/kirainmoe/auto-daily-health-report/tree/master)中登录和密码加密部分进行修改。
