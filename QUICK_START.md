# 如何在 GitHub 上使用本项目

## 1. 项目概览

**AI Workflow Automator** 是一个功能完整的多 Agent AI 编程工作流自动化系统。已经过完整开发、测试和演示验证。

## 2. 快速开始（3 步）

### 步骤 1: Clone 项目
```bash
git clone https://github.com/your-username/ai-workflow-automator.git
cd ai-workflow-automator
```

### 步骤 2: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤 3: 运行演示
```bash
# 选项 A: 演示脚本（推荐）
python examples/quickstart.py

# 选项 B: 命令行扫描
python main.py scan --target examples/sample_project

# 选项 C: 完整管道（演示模式）
python main.py run --target examples/sample_project --dry-run
```

## 3. 完整功能演示

项目已包含演示项目，展示了所有检测能力：

```
Examples:
- examples/sample_project/bad_module.py    (包含 5 个意图错误)
- examples/sample_project/good_module.py   (优质代码参考)
```

运行扫描会检测到：
- ✅ 3 个安全问题（硬编码密钥、SQL 注入等）
- ✅ 1 个性能问题（N+1 查询）
- ✅ 1 个技术债问题（长函数）

## 4. 使用 MiMo 或 Claude API

### 使用 MiMo（推荐）
```bash
export MIMO_API_KEY=sk-your-key-here
python main.py run --target your_project --provider mimo
```

### 使用 Claude
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
python main.py run --target your_project --provider claude
```

## 5. 项目结构

```
ai-workflow-automator/
├── main.py                    # CLI 入口
├── examples/
│   ├── quickstart.py         # 快速启动脚本 ⭐
│   ├── example1_basic_pipeline.py
│   ├── example2_scan_only.py
│   └── sample_project/       # 演示项目
├── src/
│   ├── pipeline.py           # 4 阶段协调器
│   ├── agents/
│   │   ├── scan_agent.py     # 代码扫描
│   │   ├── refactor_agent.py # 重构建议
│   │   ├── test_agent.py     # 测试生成
│   │   └── doc_agent.py      # 文档同步
│   └── core/
│       ├── base_agent.py     # 抽象基类
│       └── models.py         # 数据模型
├── tests/                     # 11 个测试（全部通过）
├── docs/
│   ├── GETTING_STARTED.md    # 详细指南
│   ├── ARCHITECTURE.md       # 系统设计
│   └── api/                  # API 参考
└── README.md                 # 项目总览
```

## 6. 主要特性

### 4 阶段智能管道

**Phase 1: ScanAgent** → 检测安全、性能、技术债问题  
**Phase 2: RefactorAgent** → 生成重构建议（需 LLM）  
**Phase 3: TestAgent** → 自动生成测试用例（需 LLM）  
**Phase 4: DocAgent** → 同步更新文档（需 LLM）

### 无需 LLM 的演示模式

所有功能都可以在演示模式下运行（无需 API 密钥）：
```bash
python main.py run --target your_project --dry-run
```

### 支持的检测

- 🔒 **安全**：硬编码密钥、SQL 注入、eval 使用、shell 注入
- ⚡ **性能**：N+1 查询、同步睡眠、嵌套推导式
- 🛠️ **技术债**：长函数、过多参数

## 7. 测试和验证

```bash
# 运行所有测试
pytest tests/ -v
# 结果: 11 passed ✅

# 运行特定测试
pytest tests/test_scan_agent.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

## 8. 配置

编辑 `config.yaml` 自定义行为：

```yaml
llm:
  provider: mimo  # 或 claude

phases:
  scan:
    include_patterns: ["*.py", "*.ts", "*.js"]
  refactor:
    max_proposals_per_run: 10
  test:
    coverage_target: 0.80
  doc:
    auto_update_changelog: true
```

## 9. 输出示例

运行完整管道后生成：
- `awa_output/CHANGELOG.md` - 更新的变更日志
- `awa_output/docs/api/` - API 参考文档
- `awa_output/tests/generated/` - 生成的测试用例

## 10. 文档导航

| 文档 | 用途 |
|------|------|
| [README.md](README.md) | 项目总览和特性 |
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | 详细安装和使用指南 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系统设计和扩展 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 如何贡献代码 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目完成总结 |

## 11. 常见问题

**Q: 需要 API 密钥吗？**  
A: 不需要！演示模式可以运行所有 Phase 1 的功能（代码扫描）。Phase 2-4（LLM 功能）可选。

**Q: 支持哪些语言？**  
A: 当前支持 Python。可以在 `ScanAgent` 中扩展支持其他语言。

**Q: 可以定制检测规则吗？**  
A: 可以！编辑 `src/agents/scan_agent.py` 中的 `SECURITY_PATTERNS` 和 `PERF_PATTERNS`。

**Q: 如何与 CI/CD 集成？**  
A: 看 `.github/workflows/tests.yml` 中的 GitHub Actions 配置。

## 12. 快速命令参考

```bash
# 帮助
python main.py --help

# 仅扫描
python main.py scan --target ./project

# 演示模式（推荐）
python main.py run --target ./project --dry-run

# 完整管道 + MiMo
python main.py run --target ./project --provider mimo --api-key sk-xxx

# 快速启动脚本
python examples/quickstart.py

# 运行测试
pytest tests/ -v

# 扫描本项目本身
python main.py scan --target ./src
```

## 13. 下一步

1. **本地运行演示**：`python examples/quickstart.py`
2. **扫描你的项目**：`python main.py scan --target your_project`
3. **阅读架构**：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. **贡献代码**：[CONTRIBUTING.md](CONTRIBUTING.md)
5. **申请 MiMo Token**：将此项目作为申请案例

---

**项目状态**: ✅ 完全可用，已验证  
**最后更新**: 2024-05-02  
**许可证**: MIT
