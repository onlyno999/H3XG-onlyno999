---
name: h3xg-onlyno999
description: H3XG 短剧生产 Agent（XG＝西瓜）：西瓜短剧 Agent 的前半截（剧本/分镜/提示词流水线）＋ RunningHub 云端出片工作流 2110385615559806978 的独立技能包。第一次安装先拉取西瓜短剧 Agent 本体，出图分工＝三视图等现成图原样直用、缺的图由 Agent 本地绘制，出片一律走云端工作流 API。与 H3PRO/H3YU 等其他线完全独立、不混用。用户说「H3XG」「西瓜短剧」「用西瓜出片」时触发。
---

# H3XG-onlyno999 · 西瓜短剧生产 Agent

## Purpose
一句话故事进，一条云端生成的短剧成片出。结构是「西瓜前半截 ＋ 云端出片」：
- **剧本 / 分镜 / 提示词**：西瓜短剧 Agent 的流水线负责（事件图谱、抽角色/场景/道具、分镜拆解、审查、提示词编排）。
- **出图**：分工定死——**三视图等现成图是现成的，原图直用、一个像素不许动**；没有的图（如场景图）才由 Agent 在本地绘制。
- **出片**：只走云端 RunningHub 工作流 API 生成，本 Agent 不用本地 ComfyUI、不用宿主原生视频生成顶替。

本包**独立自含**：脚本、节点图谱都在本目录内，不依赖、不混用其他技能包的派发器与节点映射。

## 第一次安装（First Install）
1. 拉取第一个 Agent 技能——西瓜短剧 Agent 本体：
   ```bash
   git clone https://github.com/zjs134679-sketch/xigua-drama-agent.git ~/workspace/xigua-drama-agent
   ```
2. 装后端：`cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
3. 生成画风包（运行时数据，仓库不带）：`backend/.venv/bin/python scripts/_gen_art_styles.py`（产出 `data/skills/art_styles/` 11 个 xg_* 画风）。
4. 装前端：`cd frontend && npm install && npm run build`
5. 启动后端：`backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 5678`（健康检查 `GET /health` 200、共 108 个接口）。
6. 已知基线（2026-10-14 实测）：西瓜自带测试 109 passed / 13 failed——12 个源于仓库未附带的运行时配置 `data/skills/contracts/negative_packs.json`（打包版/云端下发才有，缺失时后端以空配置兜底可运行）、1 个算力节点 URL 解析，均非安装故障，不要为此停工。
7. 云端工作流激活（一次性）：工作流 `2110385615559806978` 若返回 **810**，须先在 RunningHub 网页打开并**运行一次**激活（之后回 803 即可派发）。激活是账号侧动作，Agent 探针确认状态即可，不代跑。

## Tooling
- 西瓜本体：`~/workspace/xigua-drama-agent`（FastAPI :5678＋React 前端；本 Agent 只用其前半截流水线，不用它的本地 ComfyUI 算力）。
- 云端出口：RunningHub **workflow** `2110385615559806978`《MiniMax H3加速优化版 全能参考(9图 / 3音频 / 3视频)》，端点 `POST /openapi/v2/run/workflow/2110385615559806978`，Standard 实例（`instanceType=default`）。**不是** ai-app 2086289185186603010——同名同家族、不同出口，本包只认工作流 ID。
- 派发：`bin/dispatch_wf.py`（参数化：提示词文件/时长/画幅/种子/图槽/输出目录；自动生成等长静音并灌三路音频；含轮询与下载，results URL 仅 24h 有效、成功后立即下载）。
- 探针：`bin/probe_step1.py`（零扣费查激活状态：810 未激活 / 803 已激活）；节点普查 `bin/census_nodes.py`（bogus 字段哨兵法，全程零建任务零扣费）。
- 节点图谱：`references/node_map.md`（2026-10-14 普查定版，42 节点）。
- 顶级动作库（包内整合，2026-10-15 用户令）：`references/action-library/`——源自 onlyoyrao999/D-Z-P-Z-W 的动作数据全套：`core_actions_32.md`（32 式核心动作）、`ultimate_moves_111.md`（111 式终极大招＋法天象地增补 5 式共 116 式，32 个流派系列）、`shot_recipes_10.md`（10 张分镜配方卡）。本包写打斗/动作段落时查此库取招式、运镜与配方；只借动作技法，不改本包出口、节点与西瓜流水线。
- 鉴权：RunningHub 走 surrogate 凭据 `custom.runninghub`（dynamic_credentials helper），脚本内已封装，Key 不落盘、不进包。
- 交付盘：Google Drive「成片」文件夹（hatch_gws_cli drive +upload --parent <成片夹id>）。

## 云端派发口（定版）
| 用途 | 节点.字段 |
| :--- | :--- |
| 提示词 | 25.value |
| 时长（秒） | 28.value |
| 画幅 | 26.aspect_ratio（如 `9:16 (Portrait Widescreen)`） |
| 种子 | 5.noise_seed |
| 参考图（9 槽） | 18 / 23 / 22 / 24 / 32 / 33 / 34 / 35 / 76（及 77）.image |
| 音频（3 路） | 38 / 67 / 68.audio |

槽位惯例：**主角三视图卡原图 → Node 18**；场景图 → Node 23；其余按提示词主体定义顺序续排。此流无 74/75 视频槽，76/77 均为图槽。

## Workflow
1. **接单**：听完用户的一句话故事/剧本要求；定主角与时长、画幅（默认 9:16 竖屏）。
2. **备图**：
   - 人物三视图：用现成卡原图（先验 md5/来源），不重绘、不裁切、不改图。
   - 场景图等缺图：Agent 本地绘制——纯场景、无人物（场景就是场景）、构图与画幅与成片一致；画完自检再用。
3. **写提示词**：按 MiniMax H3 官方 Ref2VA 六段式（subject_definitions → summary → retention_analysis → detailed_description → overall_soundscape → non_diegetic_music），全文英文、台词只用中文 `<d>[中文] …</d>` 并带 (Sx) 说话人编号；主体长相只许引用参考图（「face 1:1 identical to <Picture N>」），不许用文字复述五官。
   - 签名造型逐项写死（如刁哥：纯黑棒球帽**正戴、帽檐朝前**，写明 never backwards）。
   - **台词次数写死**：只说一句的，必须明写 speaks exactly once, then closes his mouth and stays silent——不写死，模型会把同一句重复说。
   - 声音设定只写拟音白名单（环境声/动作声），无配乐时 non_diegetic_music 写 N/A。
   - **动作段落**：凡打斗、追逐、对决、终结技，先查 `references/action-library/` 取材——核心动作用 32 式定动作质感与运镜，终结技从 111 式里按角色流派选招（spatialAnchor/startPose/charging/execution 四段照库落词），镜头编排套 10 张配方卡的能量阶梯；取到的招式仍要按本包六段式与因果链改写落词，不许整段照搬库里的示例文案。
4. **派发前探针**：`bin/probe_step1.py` 确认 803；810 就停下报用户去网页运行一次，不许换出口、不许用其他生成方式顶替。
5. **派发**：`bin/dispatch_wf.py`——三路音频（38/67/68）一律灌**与时长等长的静音 WAV** 顶掉预置样音（有台词也照灌：对白由模型按提示词原生生成，静音只堵样音、不堵原生声）；Standard 实例；记任务号。
6. **取回**：轮询到 SUCCESS 立即下载原片（原生尺寸如 736×1280，交付不裁不缩）。
7. **质检门**（自己跑完，不拿判断题烦用户）：
   - 抽帧（首/中/尾）：脸对卡、造型逐项（帽向、服装）、场景与场景图 1:1、无烧字水印。
   - ASR 带时间戳转写：台词内容与**次数**逐句核（多说、漏说、串词都是病）。
   - 音频门：只许原生对白＋环境拟音；检出背景音乐/旁白＝污染。
   - 规格：时长、分辨率、帧率与 brief 一致。
8. **交付**：转码收尾（H.264 High@L4.0、yuv420p、bt709、AAC LC 48kHz、剥元数据、+faststart；**尺寸保持云端原生不缩放**）→ 聊天附件＋Drive「成片」夹链接；缺陷旧版删除/回收，不与正版混放。

## 铁律
1. 出片只许走 `2110385615559806978`；用户给的出口以 ID 为准，不许凭标题相似自选其他工作流/ai-app。
2. 三视图现成图**只直用、不动图**：不重绘、不裁、不 P；缺什么图补画什么图，补画的图里不许改动已锁定的人物长相。
3. 每派必先免费探针；探针不过（810）就停，不许先派再说。
4. 三路静音等长覆盖，一路不许缺；不许发空值关音频。
5. 提示词以官方六段式为准，改词只改一个变量，改完核对落地再派（同词连败两版停下来诊断，不许无脑重派）。
6. 质检不过自己修/重派；只有超预算或修不好才上报用户。
