# 阿里云语音文档参考

本 skill 对接的是阿里云**录音文件识别闲时版**（`speechfiletranscriberlite.cn-shanghai`），异步两步式：`SubmitTask` 提交后由控制台排队识别，结果通过 `GetTaskResult` 拉回，SLA 24 小时。

官方 Python 调用示例（含完整 SDK 用法、参数说明、返回结构）：

- <https://help.aliyun.com/zh/isi/developer-reference/python-demo>

调用注意：

- 使用阿里云 AccessKey（`ALIYUN_AK_ID` / `ALIYUN_AK_SECRET`）做主账号鉴权；
- 业务侧 `appkey` 必须从 [智能语音交互控制台](https://nls-portal.console.aliyun.com/) 取，**不是**阿里云控制台的 AccessKey；
- 闲时版与普通版 endpoint / 计费 / SLA 都不同，调用前先确认对接的是哪一版。
