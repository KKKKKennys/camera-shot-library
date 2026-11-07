<p align="center"><img src="assets/cover.svg" alt="Camera Shot Library V2"></p>

# Camera Shot Library · V2

**先决定这一镜头要让人看懂什么，再决定摄影机怎么动。**

`V2.0.0` · `50 张镜头卡` · `7 类用途` · `Blender / Remotion` · `MIT`

[安装与调用](#安装发给-agent-即可) · [浏览 50 张卡](references/catalog.md) · [制作复盘](docs/case-study.md) · [V2 更新](CHANGELOG.md) · [Agent 入口](SKILL.md)

为三维资产与场景展示整理的镜头指令库，作者与维护者 **李铿 / Kenny**。将观看目的、构图、轨迹、节奏和检查点拆开描述，让 Agent 能把镜头落到指定软件中。

<img src="assets/workflow.svg" alt="明确观看目的、选择镜头卡、落到软件、检查画面和时间的流程">

## 安装：发给 Agent 即可

复制下面整段到支持本地 Skills 的 Agent 聊天框：

```text
请安装 Camera Shot Library v2.0.0：
https://github.com/KKKKKennys/camera-shot-library
先阅读 INSTALL.md，安装到当前 Agent 的用户技能目录；已有同名版本先备份再升级。
完成后告诉我版本、路径和调用方式，仅安装，不渲染或修改工程。
```

只想发一个链接时，把下方链接连同“帮我按页面安装”交给 Agent：

```text
https://raw.githubusercontent.com/KKKKKennys/camera-shot-library/main/INSTALL.md
```

[详细安装说明与回退](INSTALL.md)。安装不包含 Blender、Remotion 或 MCP 环境；执行镜头还需要对应的软件能力。

## 50 张卡，怎么选

| 观众要看懂什么 | 卡片方向 | 数量 | 代表 |
|---|---|---:|---|
| 完整外形、比例、主体 | 建立与基础 | 8 | [全貌建立](cards/foundation/silhouette-establish.md) |
| 空间连接与纵深 | 空间探索 | 8 | [通道穿行](cards/space/corridor-travel.md) |
| 零件怎么组成整体 | 资产与结构 | 8 | [拆开再归位](cards/structure/explode-return.md) |
| 材质、灯光和观察重点 | 光影与焦点 | 6 | [浏览系列](references/catalog.md) |
| 前后画面如何交接 | 转场与衔接 | 8 | [中心显色](cards/transition/center-material-reveal.md) |
| 节奏、停留和信息密度 | 节奏组织 | 6 | [短预告开场](cards/rhythm/opening-teaser.md) |
| 制作阶段与结束状态 | 制作过程与收尾 | 6 | [后撤收束](cards/presentation/closing-withdrawal.md) |

每张卡包括目的、起止构图、三维执行、时间组织、后期适配与验收重点。时长是起点建议，不能脱离主体尺度、素材和音乐直接套用。

## V2 让选卡和落地更连贯

| V1 已有 | V2 增加 |
|---|---|
| 50 张卡与目录 | 本地关键词检索，返回卡片路径；无匹配时明确返回空结果 |
| 按目的选一到三张卡 | 选卡决策表与组合约束，避免同镜头同时承担过多效果 |
| Blender / Remotion 适配说明 | 明确摄影机、物体、灯光与合成遮罩各自负责什么 |
| 通用画面检查 | 帧区间约定、时间线检查器及同机位双层对齐检查 |
| 简要作品关联 | NEREID 失败试验到修订规则的复盘，包含原有证据范围 |

卡片总数仍是 **50 张**。V2 的变化在检索、执行约定和检查能力，不靠扩充数量充当升级。

## 三种调用方式

```text
使用 $camera-shot-library 为硬表面道具挑选三个镜头。
先看完整轮廓，再解释拆装关系，最后回到整体。
现在只要分镜方案，保留既定时长，不制作演示。
```

```text
使用 $camera-shot-library 在 Blender 中调整这个已选镜头。
沿用原音乐、帧率和机位起点，让相机穿过通道后稳定观察门心。
保留原工程与可编辑动画，检查中途遮挡和视线突跳。
```

```text
使用 $camera-shot-library 处理白模到成品的中心显色。
两层使用同机位、同帧、同尺寸；保持原来的运动和音轨。
先检查时间线，再只调整遮罩与羽化，不用变速或补帧掩盖问题。
```

## 在本地检索和检查

```bash
python scripts/find_shots.py "白模 成品" --limit 3
python scripts/find_shots.py --category structure --limit 8 --json
python scripts/check_sequence.py examples/sequence.json
python -m unittest discover -s tests -v
```

检索器返回的是候选，不会替代镜头选择。时间线检查器只核对计划数据：切点空隙/重叠、未知卡名、素材帧数和双层对齐声明；画面是否好看、有无穿模、声音是否悦耳仍需实际观察。

## 做 Skill 时遇到的问题

### 01 · “更流畅”不一定是更好
NEREID 的一次补帧试验在圆环、显示器、椅子、门框等结构上引入新增变形。相邻原帧完整，说明问题来自插值。最终放弃该缓存，保留原 30fps 帧序，再调整轻量衔接。

### 02 · 同机位，也可能不同帧
白模和成品做显色时，如果一层晚一帧，会在边缘出现双影。V2 要求记录源帧起点、帧率、机位和尺寸，不以“看起来差不多”替代对齐。

### 03 · 一张卡里要分清谁在动
拆装是零件动画，推近是摄影机运动，中心显色是合成遮罩。V2 把这几层分开，避免把二维放大当成三维推进，或为了一个后期变化重做整段运镜。

[阅读全文：问题 → 证据 → 处理 → 规则](docs/case-study.md)

## 既有作品语境

- **NEREID 深海科研站**：全貌建立、室内导览、中心显色与环境收束。
- **AK-50**：完整轮廓、分件关系、拆卸与归位的阅读顺序。

这些影片先于本库 V2。它们提供规则整理的案例，不代表 V2 已经回头执行过影片，也不代表 50 张卡都逐一实渲验证。[V56 验收摘要](docs/evidence/nereid-v56-review.txt)

## 阅读路线

[选卡与组合](references/selection-v2.md) → [镜头简报](references/shot-brief.md) → [帧与素材约定](references/timing-v2.md) → [Blender 实现](references/blender.md) → [画面复查](references/review.md)

<details><summary><b>常见问题</b></summary>

**需要先装 video-shotcraft 吗？** 不需要。本包的 50 张卡和检查脚本都在仓库内。若任务明确要求其他库的具体模板或参考实现，则另行读取对应原库。

**Maya 能用吗？** 镜头意图和参数组织可以参考，但本包没有 Maya 执行器。需要可用的软件连接和原生动画实现，再按相同画面标准验收。

**复制指令能直接得到电影级成片吗？** 不能保证。Skill 帮助选型、组织执行和检查，结果还取决于模型、灯光、构图与软件实现。

**为什么没有新做一支 Demo？** 本次沿用已有作品讲清规则，并验证脚本与文档；没有新增渲染任务或把示例计划写成成片验证。
</details>

---
**李铿 / Kenny** · [MIT License](LICENSE) · [发布版本](https://github.com/KKKKKennys/camera-shot-library/releases)

A practical shot-planning library for editable 3D work, with searchable cards and timeline checks. No renderer or third-party demo bundle included.
