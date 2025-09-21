# Universal Device Diagnostics

🔧 **AI-powered universal device diagnostic and repair assistant**

A cross-platform solution that detects hardware issues across phones, laptops, tablets, and more, then guides users through fixes with intelligent explanations and step-by-step repair workflows.

## 🌟 Features

- **Universal Diagnostics**: Works across Windows, Android, macOS, and iOS
- **AI-Powered Explanations**: Converts technical diagnostics into plain language
- **Guided Repairs**: Step-by-step visual guides for software and hardware fixes
- **Cross-Device Support**: One tool for phones, laptops, tablets, and more
- **Community Learning**: AI learns from successful repairs across users
- **Predictive Maintenance**: Warns before failures occur

## 🏗️ Architecture

```
universal-device-diagnostics/
├── backend/          # FastAPI orchestrator service
├── frontend/         # React TypeScript dashboard
├── agents/           # Platform-specific diagnostic agents
│   ├── windows/      # Windows diagnostic scripts
│   ├── android/      # Android ADB-based diagnostics
│   ├── macos/        # macOS system profiler tools
│   └── ios/          # iOS libimobiledevice integration
├── ai/               # AI explanation and guidance system
├── docs/             # Documentation and guides
└── tests/            # Test suites
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- ADB tools (for Android diagnostics)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/S1NAPANAHI/universal-device-diagnostics.git
cd universal-device-diagnostics
```

2. Set up backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

3. Set up frontend:
```bash
cd frontend
npm install
npm start
```

## 🎯 Roadmap

- [x] **Phase 1**: Core architecture and Windows/Android agents
- [ ] **Phase 2**: AI integration and guided repair system
- [ ] **Phase 3**: macOS/iOS support and community features
- [ ] **Phase 4**: Mobile apps and advanced diagnostics

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ to democratize device repair and reduce e-waste**