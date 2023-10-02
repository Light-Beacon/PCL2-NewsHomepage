更新： CurseForge 已经完成了自检，目前从启动器内、CurseForge/Modrinth 网站新下载的 Mod 和整合包已经可以确认安全了，但从其他途径（例如 QQ）获取的 Mod 和整合包文件依然有潜在的风险。部分杀毒软件已经可以扫描这个病毒了，且病毒的运行链已经被截断，所以至少目前它已经无法再感染新的电脑了。
从2023年5月（或更早）开始，CurseForge 中和 dev.bukkit.org 的部分账户被盗号，上传了含有恶意程序的模组、服务端插件和整合包。
## 检测排除方法
如果你最近运行过最新版模组或模组包的 Minecraft，且担心被感染，下面是检测方法
### 检测
i 这只能检测出下载的恶意程序，并不能检测出被感染的jar文件
i 如果病毒传播更高级的恶意程序，这些方法可能无法检出和排除
下载 CurseForge 官方的检测工具
* 龙猫的镜像源1：https://ltcat.lanzoum.com/inF7F0ykhh3c
* 龙猫的镜像源2：https://pan.baidu.com/s/1h-k39O1qAvySMTjUVaQzyQ?pwd=5yix
? 按钮 镜像源1 打开网页 https://ltcat.lanzoum.com/inF7F0ykhh3c 打开网页
? 按钮 镜像源2 打开网页 https://pan.baidu.com/s/1h-k39O1qAvySMTjUVaQzyQ?pwd=5yix 打开网页
![checkshot](https://i0.hdslb.com/bfs/article/d405df5a1b01943a7227c1fcf9cc71ba572af421.png "检测方式（图源：龙腾猫跃）")
### 处理
如果你的电脑被检出恶意程序，建议以以下方式处理：
1. 见 https://prismlauncher.org/news/cf-compromised-alert ，运行清理脚本
? 按钮 打开该链接 打开网页 https://prismlauncher.org/news/cf-compromised-alert 打开网页
2. 修改你在电脑上保存过的所有账号和密码
3. 最近尽量最近不要启动 Minecraft，如需要请重新下载并安装所有 MC核心、Mod、服务器核心、Bukkit插件、（即使文件很老，这些 jar 文件很可能被注入感染了，见程序行为）
## 影响范围
该恶意程序主要影响以下版本：1.16.5、1.18.2、1.19.2。
### 模组、模组包
* 地牢崛起之时（When Dungeons Arise）
* Sky Villages（天空集市）
* Better MC 模组包
* Dungeonz
* Skyblock Core
* Vault Integrations
* AutoBroadcast
* Museum Curator Advanced
* Vault Integrations Bug fix
* 其它未被发现的模组、模组包
* 被感染注入恶意代码后二次分发的模组、模组包（见程序行为）
### 服务器 Bukkit 插件
* Display Entity Editor
* Haven Elytra
* The Nexus Event Custom Entity Editor
* Simple Harvesting
* MCBounties 
* Easy Custom Foods
* Anti Command Spam Bungeecord Support
* Ultimate Leveling
* Anti Redstone Crash
* Hydration
* Fragment Permission Plugin
* No VPNS
* Ultimate Titles Animations Gradient RGB
* Floating Damage
* 其它未被发现的插件
* 被感染注入恶意代码后二次分发的插件（见程序行为）
## 程序行为
它会尝试从服务器下载恶意可执行文件并运行，该恶意程序至少执行以下行为：
* 使其自身开机启动
* 获取微软账户、Discord、Minecraft、加密货币钱包的登录凭据
* 窃取浏览器 Cookie 和登录信息（可能包含所有保存的密码和登录凭证信息）
* 组成傀儡网络，允许远程执行 DDoS 操作
* 在整个电脑上查找 Minecraft 客户端核心和服务端核心 jar 文件、Mod文件、服务器插件，并植入恶意代码使其进一步扩散与传播
* 可能有其它未探明的行为
以上感染要素主要在后台执行，用户几乎无被感染的直观感受
目前下载可执行文件的服务器暂时离线，无法执行其感染步骤，但不排除其有恢复的可能
## 后续处置
* 所有的受影响账号已被 Curseforge 方面封禁/阻止登录。
* CurseForge 方面正在对近期的所有新项目进行检查，在此期间新文件的审核将被暂停。
## 其它
* 此文为紧急发布，接下来会对该文做优化处理
* 新闻主页将会持续更新本次事件动态