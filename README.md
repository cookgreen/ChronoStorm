# ChronoStorm  
## 超时空风暴（CRS）引擎 - 复刻红色警戒2和尤里的复仇

![Python Badge](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pygame Badge](https://img.shields.io/badge/Pygame-2.5+-green.svg)
![License Badge](https://img.shields.io/badge/License-MIT-yellow.svg)
  
**ChronoStorm(C.R.S.)** is an open-source, modern engine reimplementation of the classic RTS games *Command & Conquer: Red Alert 2* and *Yuri's Revenge*. Built from scratch utilizing Python and Pygame, it aims to provide a highly moddable, cross-platform foundation for isometric 2D strategy games.  
  
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/e0e337f9-1721-4082-adfb-4673a4145b4e" />



## ⚠️ Important Legal Notice
**ChronoStorm is a game engine, NOT a full game.** This repository does not contain any original game assets, artworks, sounds, or copyrighted materials belonging to Electronic Arts. To use or test this engine, you **must** own a legal copy of *Red Alert 2 / Yuri's Revenge* and provide your own `.MIX` asset files.

## 🚀 Vision & Roadmap
The ultimate goal is to recreate the authentic 2.5D isometric experience while replacing the 20-year-old legacy codebase with flexible, Pythonic architecture—opening the doors for modern AI implementations and limitless modding capabilities.

- [x] **Phase 1: Asset Forging**
  - [x] `.MIX` file archive extraction.
  - [x] `.SHP` (Sprite) and `.VXL` (Voxel) rendering via Pygame.
  - [x] Palette (`.PAL`) loading and color mapping.
- [ ] **Phase 2: The Grid**
  - [ ] Map (`.MAP`) parsing and isometric grid rendering.
  - [ ] Terrain tilesets and basic world rendering.
- [ ] **Phase 3: Mechanics & AI**
  - [ ] A* Pathfinding optimized for isometric tiles.
  - [x] Classic Sidebar UI implementation.
  - [ ] Entity state machines and modern AI behavior trees.
- [ ] **Phase 4: Integrate Large Language Model**
  - [ ] Integrate the LLM like DeepSeek
  - [ ] Use DeepSeek to command the enemy AI

## 🛠️ Getting Started

### Prerequisites
- Python 3.10 or higher
- Pygame Community Edition (Pygame-CE recommended for better performance)

### Installation
```bash
git clone https://github.com/cookgreen/ChronoStorm.git
cd ChronoStorm
pip install -r requirements.txt

(Note: Instructions on where to place your original game .MIX files will be updated soon.)
```

## 📺 Devlogs & Community
Game development is a journey. We document our engine-building process, tackling challenges like isometric coordinate math, Pygame render optimizations, and integrating advanced AI into indie games.

Watch the full development journey and technical deep-dives on the [My YouTube channel](https://www.youtube.com/@ckgndodocat)!

## 🤝 Contributing
Whether you are a Pygame enthusiast, a pathfinding algorithm wizard, or a veteran C&C modder familiar with file structures, your pull requests are welcome! Check out our CONTRIBUTING.md (coming soon) to see how you can help.

## 📜 License
Distributed under the MIT License. See LICENSE for more information.
