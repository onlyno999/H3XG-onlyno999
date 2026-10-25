# CZX233 出口 · 节点图谱（2026-10-26 普查定版，H3XG 第二出口）

## 出口

- 帖子：https://www.runninghub.cn/post/2108739345095155713/（作者 CZX233，2026-10-15 更新）
- 名称：H3 无损融合单采
- API 工作流 ID：`2108739345095155713`（AI 应用 `2108746401877417986` 不用）
- 画布结构（浏览器进画布实读）：79 节点；核心 MiniMax H3 Reference to Video；模型栈含 diffusion、qwen3 CLIP、turbo LoRA、稀疏注意力、BasicScheduler；**采样链只有一条**（“单采”）；“空间折叠”＝大量 Get/Set 命名通道＋三组“忽略多组 孤海”开关组，关时整组紫色旁路。
- **本出口走 API**：画布前台的开关不影响 API；按要求正常挂图（199 图 1、188 图 2）。

## API 实测可用（POST /openapi/v2/run/workflow/2108739345095155713）

| 节点 | 字段 | 用途 | 证据 |
|:--- |:--- |:--- |:--- |
| 238 | value | 提示词全文（不是 prompt 字段） | 派发成功多单 |
| 227 | value | 时长（秒；10、20 均成功） | 派发成功多单 |
| 228 | aspect_ratio | 画幅（如 `9:16 (Portrait Widescreen)`） | 派发成功多单 |
| 228 | megapixels | 分辨率档（如 1.1） | 派发成功多单 |
| 129 | noise_seed | 种子（control_after_generate＝randomize，设了也可能被随机化） | 派发成功多单 |
| 199 | image | 参考图像 1（Load Image） | 派发成功多单 |
| 188 | image | 参考图像 2（Load Image） | 派发成功多单 |

探针法：bogus 字段哨兵（用不存在的字段名逐个试节点，803 回执自报缺失与否），全扫 1–238 号，零建任务零扣费。

## 画布前台的槽位（仅作图谱记录；画布前台开关不影响 API）

工作流设计容量：**6 图＋3 音频＋1 视频**（2026-10-26 画布实测完整核对，画布副本 2114438481467494402，只读核对、未保存未运行）：

| 槽位 | Load 节点 | Set 节点 | 输入字段 | 控制开关 |
|:--- |:--- |:--- |:--- |:--- |
| 参考图像 1 | 199 Load Image | 193 | image | 200（图像组） |
| 参考图像 2 | 188 Load Image | 194 | image | 200（图像组） |
| 参考图像 3 | 189 Load Image | 195 | image | 200（图像组） |
| 参考图像 4 | 190 Load Image | 196 | image | 200（图像组） |
| 参考图像 5 | 191 Load Image | 197 | image | 200（图像组） |
| 参考图像 6 | 192 Load Image | 198 | image | 200（图像组） |
| 参考音频 1 | 182 Load Audio | 179 | audio | 187（音频组） |
| 参考音频 2 | 183 Load Audio | 180 | audio | 187（音频组） |
| 参考音频 3 | 184 Load Audio | 181 | audio | 187（音频组） |
| 参考视频 1 | 185 Load Video (Upload) | 178 | video | 186（视频组） |

- 开关归属：200 号（“忽略多组 孤海”）含图像 1–6 六个开关、控制图像组；187 号同类型含音频 1–3 三个开关、控制音频组；186 号同类型仅含视频 1 一个开关、控制视频组。核对时图像 1、2 为开启、其余关闭（画布副本状态，各副本可能不同）。
- 视频字段纠正：画布实测 185 号输入字段是 **video**（节点体、Parameters INPUTS 首项、Node Info Widgets 均显示 “video: The video file to be loaded.”，带 “choose video to upload” 按钮，画布上未见 file 字段）——此前记的 file 是错的，以 video 为准。

**本出口按 API 接口正常挂图：199 图 1、188 图 2。** 画布前台的开关只影响画布前台，不影响 API。

## 派发端点

- 上传：`POST /openapi/v2/media/upload/binary`（multipart file → `data.fileName`，形如 `openapi/<hash>.<ext>`）
- 建单：`POST /openapi/v2/run/workflow/2108739345095155713`（`{nodeInfoList, instanceType:"default", usePersonalQueue:false}`）
- 查询：`POST /openapi/v2/query`（`{taskId}`；results URL 仅 24h 有效，SUCCESS 后立即下载）
- 鉴权：surrogate 凭据 `custom.runninghub`（dynamic_credentials helper），Key 不落盘。
- 画布默认出片档：16:9、7 秒、随机种子、约 80 RH 币/条（应用页估）；本项目用 9:16、10 秒一段/20 秒整篇、Standard。
