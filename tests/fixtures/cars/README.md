`byd-empty-configs.json` 是真实 BYD goodsParams 响应片段，复制自
`docs/actions拆分-20261030/car-source-empty-configs.json`，与失败 run
41631619345 的异常路径一致。仅保留公开响应，无签名、cookie 或个人信息。
回归点：HTTP/API 成功不等于存在可唯一对应的车型参数列。
