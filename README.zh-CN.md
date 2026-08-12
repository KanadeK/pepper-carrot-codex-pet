# Codex 桌面宠物 Pepper

[English](README.md) | [在线预览](https://kanadek.github.io/pepper-carrot-codex-pet/)

这是一个以 David Revoy 的自由漫画
[Pepper&Carrot](https://www.peppercarrot.com/) 中的年轻女巫 **Pepper**
为原型制作的 Codex v2 桌面宠物。

![Pepper 待机动画](artwork/qa/previews/idle.gif)

它不是只有网页或截图的空壳。仓库实际提供：

- 8 列 11 行、1536x2288 的 WebP 动画图集；
- 9 种任务状态和连续 16 方向视线循环，共 73 个动画格，另含 1 个 v2
  指针中性格；
- Windows、macOS、Linux 可用的 SHA-256 校验安装器；
- 可执行的校验、安装、诊断、修复、卸载和确定性打包命令；
- 自动化测试、可视化 QA、CI 与读取真实图集的在线预览页。

本项目是独立二次创作，并非 Pepper&Carrot 官方项目。Pepper 角色、上游参考图和
本项目生成的角色图使用 CC BY 4.0；程序代码使用 MIT。完整来源、原始文件哈希、
改动说明和署名方式见 [NOTICE.md](NOTICE.md)。

## 安装

[在 Codex 中安装 Pepper](codex://pets/install?name=Pepper%20%7C%20Pepper%26Carrot&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2FKanadeK%2Fpepper-carrot-codex-pet%2Fmain%2Fpet%2Fspritesheet.webp&spriteVersionNumber=2)

Windows PowerShell：

```powershell
irm https://raw.githubusercontent.com/KanadeK/pepper-carrot-codex-pet/main/scripts/install.ps1 | iex
```

macOS 或 Linux：

```sh
curl -fsSL https://raw.githubusercontent.com/KanadeK/pepper-carrot-codex-pet/main/scripts/install.sh | sh
```

安装器会下载并校验 `pet.json`、`spritesheet.webp`、`provenance.json`。如果
已经安装过同 ID 宠物，旧版本会先移动到 `~/.codex/pet-backups/`，不会直接
删除。完成后在 Codex 的 **Settings > Pets** 中刷新并选择
**Pepper | Pepper&Carrot**。

## 校验、诊断与修复

工具链要求 Python 3.11 或更高版本：

使用 `uv` 可直接安装锁定版本：

```sh
uv sync --extra dev --locked
```

也可以使用标准 Python 环境：

```sh
python -m venv .venv
python -m pip install -e ".[dev]"
pepper-pet validate pet --json
pepper-pet install --source pet
pepper-pet doctor --source pet --json
```

如果安装后的动画图集丢失、被修改或无法读取：

```sh
pepper-pet repair --source pet --json
```

修复命令会先校验源包，再进行带回滚保护的原子替换，并把损坏版本保存在备份
目录。可恢复卸载命令为：

```sh
pepper-pet uninstall --json
```

### 可执行修复示例

下面的示例会创建隔离的临时 Codex 目录，安装 Pepper，只破坏临时副本，确认诊断
状态为 `invalid`，执行修复，并核对损坏副本已保留：

```sh
python examples/demo_repair.py --source pet
```

它不会修改仓库中的宠物，也不会接触真实的 Codex 用户目录。

## 验收

在 Windows 上运行完整发布闸门：

```powershell
./scripts/release-check.ps1
```

跨平台的核心验收命令：

```sh
python -m ruff check .
python -m pytest --cov=pepper_pet --cov-report=term-missing --cov-fail-under=90
python -m pepper_pet.cli validate pet --json
python -m build
python -m pepper_pet.cli package --repo-root . --out-dir dist --version v0.1.0 --json
```

成功标准：

- Ruff 和 Pytest 退出码均为 `0`，分支覆盖率不低于 90%；
- 宠物校验结果包含 `"ok": true`、尺寸 `[1536, 2288]`、文件小于 20 MiB、
  73 个动画格、1 个指针中性格、14 个空白保留格，并且全透明像素没有
  隐藏 RGB；
- 两次在不同目录中完成的打包结果逐字节相同；
- 根目录 `checksums.txt` 覆盖三个可安装宠物文件；
- `dist/SHA256SUMS` 覆盖作为 Release 资产上传的 ZIP、发布清单、wheel 和源码包；
- 预览站使用的图集与可安装图集哈希完全一致。

所有常见失败、诊断命令和修复方法见
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)。

## 目录

```text
pet/                 可安装的 Codex v2 宠物
src/pepper_pet/      校验、安装、诊断、修复与打包工具
tests/               单元、命令行、安全边界与确定性测试
examples/            可执行的安装、损坏与修复演示
scripts/             联网安装器和发布闸门
site/                读取真实图集的 GitHub Pages 预览
artwork/references/  带授权信息的上游参考图
artwork/source/      已验收的生成源图与提示词
artwork/qa/          动画与方向语义 QA 证据
docs/                架构、验收、研究和故障修复说明
```

参与贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。任何动画变更都必须保持
Codex v2 结构、通过校验、更新 QA 证据并保留 CC BY 4.0 署名。
