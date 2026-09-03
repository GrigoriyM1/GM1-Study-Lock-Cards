# 🃏 GM1 Study Lock Cards

> Lock your PC, unlock with knowledge. Study while you work! 🧠💻

A productivity tool that locks your PC at configurable intervals and requires you to answer questions (cards) to continue working. Perfect for students, developers, and anyone who wants to stay focused while studying.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://www.microsoft.com/windows)
[![Version](https://img.shields.io/badge/Version-3.0-green.svg)]()

---

## 📸 Preview

```
+--------------------------------------------------+
|  🔒 GM1 STUDY LOCK CARDS                         |
|                                                   |
|  Time to study!                                   |
|                                                   |
|  Question: What is the capital of France?        |
|  [              Paris              ]              |
|  [🔍 Check answer]                               |
|                                                   |
|  💡 Hint: It starts with 'P'                     |
+--------------------------------------------------+
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🕒 **Smart Locking** | Locks PC at configurable intervals (default: 30 min) |
| 📝 **Card System** | Answer questions (cards) to unlock your PC |
| 🖼️ **Local Images** | Add images from your computer to questions |
| 🔔 **Smart Alerts** | Show hints or additional info with questions |
| 🧪 **Test Mode** | Preview the lock before committing |
| ⚡ **Immediate Lock** | Lock instantly on demand |
| ⌨️ **Keyboard Shortcuts** | `Ctrl+C` returns to menu, `Enter` submits answer |
| 📦 **JSON Storage** | All questions stored in simple JSON format |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/GrigoriyM1/GM1-Study-Lock-Cards.git
cd GM1-Study-Lock-Cards
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the program
```bash
# Interactive mode
python study_lock.py

# Auto-start with test (30 min)
python study_lock.py --autostart

# Auto-start with custom interval (15 min)
python study_lock.py --autostart 15
```

---

## 🎮 Menu Options

```
MENU:
1. Start lock (with test lock)      ← Test then lock
2. Start lock immediately            ← Lock NOW, ask questions
3. Add question without image        ← Add text-only card
4. Add question with image (file)    ← Add card with local image
5. Remove question                   ← Delete a card
6. Show all questions                ← View all cards
7. Change interval (in minutes)      ← Adjust lock time
8. Exit                              ← Close program
```

---

## 📝 Adding Cards (Questions)

### Simple Card
```json
{
    "question": "What is 2+2?",
    "answer": "4"
}
```

### Card with Image (from file)
```
Choose option 4 → Enter image file path: C:\Users\Admin\Pictures\cat.jpg
```

### Card with Alert (hint)
```json
{
    "question": "What is the capital of France?",
    "answer": "Paris",
    "alert": "💡 Hint: It starts with 'P' and ends with 's'"
}
```

---

## 🖼️ Image Support

| Source | Format | Example |
|--------|--------|---------|
| 📁 File | `.jpg`, `.png`, `.gif`, `.bmp`, `.webp` | `C:\Pictures\cat.jpg` |
| 📦 Base64 | Embedded images (auto-converted) | Stored in `questions.json` |

> **Note:** Images are embedded into `questions.json` as base64, so they work even if the original file is moved or deleted.

---

## 🛠️ Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Runtime |
| pywin32 | ≥306 | Windows API |
| Pillow | ≥10.0.0 | Image processing |
| Tkinter | Built-in | GUI |

---

## ⚙️ Command Line Arguments

```bash
# Show help
python study_lock.py --help

# Interactive mode
python study_lock.py

# Auto-start with test (default 30 min)
python study_lock.py --autostart

# Auto-start with custom interval
python study_lock.py --autostart 15
python study_lock.py --autostart 45
```

---

## 📁 Project Structure

```
GM1-Study-Lock-Cards/
├── study_lock.py          # Main application
├── questions.json         # Cards database (auto-generated)
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
└── .gitignore            # Git ignore file
```

---

## 🔒 How It Works

1. **Start the program** — choose lock mode
2. **Timer runs** — configurable interval (default 30 min)
3. **Lock triggers** — full-screen lock appears
4. **Question appears** — random card from your collection
5. **Enter answer** — correct = unlock, wrong = try again
6. **Cycle repeats** — timer restarts automatically

---

## ⚠️ Important Notes

> **WARNING**: Make sure you have at least one question saved before starting the lock!

If you forget your answers:
- **Option 1**: Force restart your computer (hold power button)
- **Option 2**: Edit `questions.json` manually to add/change questions
- **Option 3**: Use `Ctrl+C` while in menu to return to options

---

## 🎯 Use Cases

- 🎓 **Students** — Review flashcards while studying
- 💻 **Developers** — Learn new technologies during breaks
- 📚 **Language Learners** — Practice vocabulary
- 🧪 **Test Preparation** — Quiz yourself before exams
- 🧠 **Memory Training** — Strengthen recall ability

---

## 🐛 Troubleshooting

### Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'win32gui'` | `pip install pywin32` |
| `ModuleNotFoundError: No module named 'PIL'` | `pip install Pillow` |
| Window doesn't appear | Run as administrator |
| Image not loading | Check file path exists and is accessible |

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## ⭐ Support

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting issues
- 💡 Suggesting features
- 📢 Sharing with others

---

**Happy studying! 📚✨**