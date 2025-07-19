# Contributing to Amethyst AI

Welcome! We're excited you're considering contributing to **Amethyst**, the world's first AI-native language and IDE to build composite agents.

Our mission is to make building AI agents as easy as writing natural language – no boilerplate, no brittle workflows, just clean, powerful, composable AI programs.


---

## 🛠️ Getting Started

1. Clone the repo: `git clone https://github.com/fask/amethyst`
2. Choose a folder you're interested in (`compiler`, `ide`, or `platform`)
3. Follow the README or `setup.md` in that folder (coming soon)

---

## 🤝 How to Contribute

We welcome contributions of all kinds:

- 🚀 Code (features, bug fixes, refactors)
- 📄 Docs (tutorials, architecture, FAQs)
- 🧪 Tests (unit, integration, regression)
- 🔌 Plugins (tools, agents, integrations)

Steps:
1. Open an issue or find one tagged `good first issue`
2. Fork and create a branch
3. Commit using clear messages (e.g., `feat: add @calendar_agent`)
4. Submit a Pull Request (PR) — we’ll review ASAP

---

## 🔮 Architecture
Coming Soon

---

## 📁 Project Structure

Amethyst follows a modular architecture with clear separation between the compiler, IDE, and platform components.

### **🏗️ Overall Architecture**

```
amethyst/
├── 📄 README.md                    # Main project documentation & vision
├── 📄 CONTRIBUTING.md              # This file
├── 📄 LICENSE                      # MIT License
├── 📄 package.json                 # Root package configuration
├── 📁 compiler/                    # 🚧 **WIP** - Core compiler
├── 📁 ide/                         # 🚧 **PLANNED** - IDE applications
├── 📁 platform/                    # 🚧 **PLANNED** - SaaS platform services
└── 📁 docs/                        # 📝 **EMPTY** - Documentation
```

### **🔧 Compiler**

**Location**: `compiler/`

**Structure**:
```
compiler/
├── 📁 src/amethyst_compiler/        # Canonical Python package
│   ├── 📄 __init__.py               # Package exports
│   ├── 📄 parser.py                 # AmethystParser class
│   ├── 📄 runtime.py                # AmethystCompiler class
│   └── 📄 amethyst_types.py         # Type definitions
├── 📁 tests/                        # Test suite
│   ├── 📄 run_test.py               # Main test runner
│   ├── 📄 test_agent.amt            # Basic syntax test
│   ├── 📄 readme_example.amt        # README syntax test
│   ├── 📄 test_readme_syntax.py     # README test runner
│   ├── 📄 hello_world_agent.py      # A2A agent implementation
│   └── 📄 run_hello_world_server.py # Server runner
├── 📄 pyproject.toml                # Poetry configuration
├── 📄 poetry.lock                   # Dependency lock file
└── 📄 README.md                     # Compiler documentation
```

**Getting Started with Compiler**:
```bash
cd compiler
poetry install
cd tests
python run_test.py
```

### **💻 IDE (🚧 PLANNED)**

**Location**: `ide/`
**Status**: **Planning Phase** - NextJS TypeScript projects

**Structure**:
```
ide/
├── 📁 consumer/                   # Consumer-facing IDE
│   └── 📄 README.md               # TODO: NextJS TS project
└── 📁 dev/                        # Developer IDE
    └── 📄 README.md               # TODO: NextJS TS project
```

**Planned Features**:
- 🎯 **Consumer IDE**: Simple GUI for non-technical users
- 🛠️ **Developer IDE**: Advanced tools for debugging, observability, breakpoints, step-through execution
- 📊 **Observability**: Real-time agent monitoring

### **🌐 Platform (🚧 PLANNED)**

**Location**: `platform/`
**Status**: **Planning Phase** - SaaS platform built with NestJS/NextJS TypeScript projects

**Structure**:
```
platform/
├── 📁 api/                         # Backend API services
│   └── 📄 README.md               # TODO: NestJS TS project (REST APIs)
├── 📁 enterprise/                  # Enterprise platform
│   └── 📄 README.md               # TODO: NextJS TS project
└── 📁 consumer/                    # Consumer platform
    └── 📄 README.md               # TODO: NextJS TS project
```

**Planned Features**:
- 🔌 **API Layer**: REST APIs for agent orchestration and management
- 🏢 **Enterprise**: Advanced deployment, monitoring, scaling
- 👥 **Consumer**: Simple user interface for agent creation, ChatGPT-like.
- 🔐 **Authentication**: OAuth flows for external integrations
- 📦 **Package Management**: npm/pip-like package system

### **👥 Target User Groups**

**1. Consumers** 
- Non-tech users building AI sidekicks
- Home automation enthusiasts, managers, founders, etc.
- Simple GUI IDE experience

**2. Developers**
- Enterprise users building large-scale applications
- Advanced debugging and observability tools
- Global deployment and management

### **📊 Current Status**

| Component | Status | Description |
|-----------|--------|-------------|
| **Compiler** | 🚧 **WIP** | Tested A2A communication |
| **IDE Consumer** | 🚧 **Planned** | NextJS TS project |
| **IDE Developer** | 🚧 **Planned** | NextJS TS project |
| **Platform API** | 🚧 **Planned** | NestJS TS project |
| **Platform Enterprise** | 🚧 **Planned** | NextJS TS project |
| **Platform Consumer** | 🚧 **Planned** | NextJS TS project |

### **🎯 Contribution Areas**

**Ready for Contributions**:
- ⚙️ **Core Features**: MCP tool calling `@tool_name`, task state management 
- 🧪 **Compiler Tests**: Add more test cases, edge cases
- 📚 **Documentation**: API docs, tutorials, examples
- 🔌 **Agent Integrations**: Create new agents using a2a-sdk
- 🐛 **Bug Fixes**: Compiler edge cases, parser improvements

**Coming Soon**:
- 💻 **IDE Development**: NextJS TypeScript projects
- 🌐 **Platform Services**: NestJS backend APIs
- 🔧 **DevOps**: CI/CD, deployment, monitoring
- 🎨 **UI/UX**: Design system, components

---

## 🔐 License & Contributor Rights

This project is licensed under the [Apache 2.0 License](./LICENSE). Given it's OSS anyone can contribute, even if you're employed by Big Tech.

---

## 💬 Communication

- GitHub Issues and Discussions for questions
- Discord/Slack community coming soon
- Weekly roadmap updates in the repo

---

## ❤️ Code of Conduct

Please treat others with respect and curiosity. Be kind, be constructive, and remember — we’re all here to make agents (and therefore humans) awesome.

---

Thank you for being part of the Amethyst journey!