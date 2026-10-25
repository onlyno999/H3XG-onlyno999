# CZX233 出口 · 节点图谱（2026-10-26 普查定版，H3XG 第二出口）

## 出口

- 帖子：https://www.runninghub.cn/post/2108739345095155713/（作者 CZX233，2026-10-15 更新）
- 名称：H3 无损融合单采
- API 工作流 ID：`2108739345095155713`（AI 应用 `2108746401877417986` 不用）
- 画布结构（浏览器进画布实读）：79 节点；核心 MiniMax H3 Reference to Video；模型栈含 diffusion、qwen3 CLIP、turbo LoRA、稀疏注意力、BasicScheduler；**采样链只有一条**（“单采”）；“空间折叠”＝大量 Get/Set 命名通道＋三组“忽略多组 孤海”开关组，关时整组紫色旁路。
- **本出口走 API，不走画布**（用户 2026-10-26 亲定：不需要走画布，直接 API 按探测的接口挂图）。

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

## 画布有、API 没有（2026-10-26 直挂实证；本出口不走画布，仅作“为什么 API 只有两图”的说明）

| 节点 | 画布身份 | API 结果 |
|:--- |:--- |:--- |
| 189 | 参考图像 3（默认开） | node_not_found_in_workflow（803）。2026-10-26 按编号直挂 199/188/189＋20 秒原词：三图上传成功、校验到 189 被拒，未建单、未扣费 |
| 190 / 191 / 192 | 参考图像 4 / 5 / 6（开关可开） | node_not_found_in_workflow（803） |
| 185 | 参考视频 1（Load Video，默认关；字段名 `file` 非 `video`） | node_not_found_in_workflow（803） |
| 182 | 音频 1（Load Audio，默认关；字段名 `file`） | node_not_found_in_workflow（803） |
| 200 / 187 / 186 | 开关组（200 最可能对应图片组，186/187 对应音频/视频未确指） | node_inputs_missing，无可设输入——API 里拨不动开关 |
| 130 | 未知 | node_not_found_in_workflow（803） |

**结论：API 线目前只能挂 199/188 两张图，无视频参考、无音频参考。** 本出口按用户定走 API，不走画布，因此只认这两图；词里的参考图注必须与实际挂图一致（只许出现 Reference image 1/2）。

## 派发端点

- 上传：`POST /openapi/v2/media/upload/binary`（multipart file → `data.fileName`，形如 `openapi/<hash>.<ext>`）
- 建单：`POST /openapi/v2/run/workflow/2108739345095155713`（`{nodeInfoList, instanceType:"default", usePersonalQueue:false}`）
- 查询：`POST /openapi/v2/query`（`{taskId}`；results URL 仅 24h 有效，SUCCESS 后立即下载）
- 鉴权：surrogate 凭据 `custom.runninghub`（dynamic_credentials helper），Key 不落盘。
- 画布默认出片档：16:9、7 秒、随机种子、约 80 RH 币/条（应用页估）；本项目用 9:16、10 秒一段/20 秒整篇、Standard。
