# CodeQuest 2026 · Chaotic Crossing

## 🏆 First Prize — 2026 CodeCombat CodeQuest Hackathon

**I won First Prize at the 2026 CodeCombat CodeQuest Hackathon.**

I'm [Jackson Tai](https://github.com/JacksonTai2007). I'm sharing this collection of Chaotic Crossing arena bots so other contestants can study the strategies, run the code, and build their own approaches.

**我在 2026 CodeCombat CodeQuest Hackathon 获得了 First Prize（一等奖）。**
这里整理了国内与国际赛场使用和研究过的代码版本，供其他选手学习、运行与改进。

Also included: **[Algorithm Iteration Lab](skills/algorithm-iteration-lab/SKILL.md)**, an MIT-licensed agent skill for evidence-driven algorithm iteration with local simulation and a measured compute budget.

This is a collection of competition-era versions, not a claim that every file was the prize-winning submission. Historical ladder scores are not current performance guarantees.

## Choose a version / 选择版本

| File | Purpose |
| --- | --- |
| [`bots/cn/CN_final2.py`](bots/cn/CN_final2.py) | Later domestic snapshot: two-player role selection, goalkeeper feed cycles, passing and shooting. / 较后的国内版本。 |
| [`bots/cn/CN_final.py`](bots/cn/CN_final.py) | Alternative domestic snapshot: separate player roles and interception calculations. / 另一份国内版本。 |
| [`bots/international/chaotic_crossing_bot_intl_v16.py`](bots/international/chaotic_crossing_bot_intl_v16.py) | International v16 archive: side-aware positioning, shooting/pass evaluation, and throttled decisions. / 国际 v16 历史版。 |

The scripts are alternatives. **Use one complete file at a time; do not concatenate them.** Their original code is preserved, including historical quirks.

这些脚本互为备选。**一次复制一份完整代码，不要拼接。** 本次整理不改变算法。

## Reusable workflow skill / 可复用工作流

The model proposes hypotheses and candidate code. The local machine runs the experiments. A trustworthy evaluator decides whether a candidate actually improves. More tokens or faster hardware cannot compensate for a wrong result parser or an inaccurate simulator.

[`algorithm-iteration-lab`](skills/algorithm-iteration-lab/SKILL.md) packages that workflow:

- Freeze a baseline and the evaluation inputs.
- Investigate a loss before changing tactics.
- Make one evidence-backed candidate and run the key regressions first.
- Expand to the acceptance set only after the gates pass.
- Measure CPU/memory needs before increasing match parallelism.
- Keep official-engine results, approximations, timeouts and unexecuted work distinct.

它不是“一键保证冠军”的提示词，也不自带官方引擎或自动抓取对手。模型负责找方向，本机负责做实验，评测负责判对错。

### Install the skill

Copy `skills/algorithm-iteration-lab` into the skill directory used by your agent. For Codex, use `$CODEX_HOME/skills` when configured, otherwise `~/.codex/skills`. Do not overwrite an existing customized copy without reviewing the changes.

PowerShell example, from this repository:

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
$target = Join-Path $skillRoot 'algorithm-iteration-lab'
if (Test-Path -LiteralPath $target) { throw "Skill already exists: $target" }
New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
Copy-Item -LiteralPath './skills/algorithm-iteration-lab' -Destination $target -Recurse
```

Invoke it with a concrete algorithm and evaluator, for example:

> Use $algorithm-iteration-lab to inspect my bot and local evaluator, reproduce the baseline loss, and validate a candidate within a 20-match budget. Do not submit anything online.

The bundled read-only probe needs Python 3 and no external packages:

```sh
python skills/algorithm-iteration-lab/scripts/resource_probe.py
python -B -m unittest discover -s skills/algorithm-iteration-lab/tests -p test_resource_probe.py -v
```

Supply measured per-match memory and runtime only after calibration. For example, **if** a measured match takes 20 seconds and a whole worker peaks at 512 MiB:

```sh
python skills/algorithm-iteration-lab/scripts/resource_probe.py --seconds-per-match 20 --peak-memory-mb 512 --matches 36 --workers 4
```

Those example numbers are not benchmark results. The probe does not launch a game, model or network request; its wall-time output is an estimate.

## Quick start

1. Open the **Chaotic Crossing** arena in CodeCombat or the corresponding Chinese platform. Use the arena available to your account and competition.
2. Select **Python** in the game editor.
3. Open one of the files above and copy its complete contents into the editor.
4. Run a practice match. Check for errors and test both red and blue sides.
5. Adjust the strategy for the current arena rules before submitting it.

**No pip or npm packages are needed to paste these bots into the game.** The game supplies `hero`, `params`, player objects, and the `spawn-mate` event. These are game scripts, not standalone Python applications: `python CN_final2.py` will not start a match.

`CN_final2.py` registers its callback before the function declaration. That ordering relies on the game's Python execution environment; do not use ordinary CPython execution as a game-runtime test.

### 中文快速上手

1. 打开 CodeCombat／扣哒世界对应的 **Chaotic Crossing** 关卡，选择 **Python**。
2. 从上表选一份脚本，将全文复制到游戏编辑器。
3. 先运行练习对局，确认无报错，并分别检查红蓝两边。
4. 根据当前关卡规则调整，再提交比赛。

无需安装 Python 依赖。`hero`、`params` 和队员事件由游戏提供，不能在终端直接运行这些脚本来启动比赛。

## Validation and known limits / 验证与限制

- All three published snapshots pass Python syntax compilation. This checks syntax only; it does not execute a bot or prove game compatibility.
- This publication does **not** include a fresh in-game match, live ladder evaluation, or tournament submission.
- Historical mechanics, runtime limits, and platform APIs may change. Test with the arena you are actually entering.
- The later domestic snapshot retains two known review findings: a whistle-distance condition repeats player 0, and one pass-safety condition mixes passer and receiver references. These have **not** been fixed or match-tested in this release.
- The international filename records v16; its opening comment still says v2. The source comment was left unchanged.

三份脚本均通过静态语法编译检查；本次没有重新运行官方对局或验证胜率。国内较后版本保留了两处已知索引问题，未擅自修复，也不将旧版本战绩套用到这些文件。

Optional local syntax check, with Python 3 installed:

```sh
python -B -c "from pathlib import Path; files=sorted(Path('bots').rglob('*.py')); assert len(files)==3; [(compile(p.read_text(encoding='utf-8-sig'), str(p), 'exec'), print('PASS:', p)) for p in files]"
```

This compiles source strings only. It does not import or execute the bots.

## What's intentionally excluded / 未公开的内容

- Raw opponent-source collections and unrelated experimental variants.
- Captured sessions, account records, network payloads, ladder snapshots, and match logs.
- Downloaded game-engine bundles and the internal replay harness.
- Local agent settings, private notes, and the original internal handoff document.

The repository is an unofficial contestant project. It is not affiliated with or endorsed by CodeCombat. Third-party code retains its own attribution and applicable permissions; an award does not imply sole authorship of every technique or snapshot.

## License and provenance / 许可与来源

The new workflow skill, helper, tests and repository documentation are **MIT licensed**; see [LICENSE](LICENSE).

The archived bots are published with permission confirmed by the repository owner. They are **not automatically covered by the MIT license**: the domestic snapshots include third-party-derived code, and a named upstream license was not supplied for this release. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for source context. Public availability alone does not establish unrestricted relicensing rights.

新编写的 Skill、工具、测试和文档按 MIT 开源。历史 bot 按仓库作者确认的许可公开，保留第三方归属，不擅自替第三方部分改签 MIT；需要进一步分发或改签时，应先明确相应授权条款。
