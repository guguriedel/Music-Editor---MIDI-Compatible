# 🎼 Music Score Editor - Interactive MIDI Composer 🎹

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![PyGame](https://img.shields.io/badge/PyGame-2.1.3-green)](https://www.pygame.org/)
[![Mido](https://img.shields.io/badge/Mido-1.2.10-yellow)](https://mido.readthedocs.io/)

Um editor de partituras musical interativo com suporte a MIDI, permitindo composição visual e conversão para arquivos executáveis.
![image](https://github.com/user-attachments/assets/40abdfdd-7de0-4a54-b00e-2b67a63d08ae)


![Demo](screenshots/demo.gif) <!-- Adicionar gravação da interface em funcionamento -->

## ✨ Principais Recursos
- **Editor Visual de Partituras** com suporte a claves de Sol e Fá
- **Conversão MIDI Bidirecional** (importação/exportação)
- **Reprodução em Tempo Real** das composições
- **Símbolos Musicais Completo**:
  - Notas (Semibreve, Mínima, Semínima, Colcheia, Semicolcheia)
  - Pausas
  - Sustenidos
- **Sistema de Compassos** ajustável (4/4, 3/4, 2/4, 3/8)
- **Interface Intuitiva** com ferramentas de desenho musical

## 📦 Instalação
1. **Pré-requisitos**:
   ```bash
      # Instalar pacotes Python
      pip install mido python-rtmidi pygame

      # Usuários Windows talvez precisem instalar:
      python -m pip install python-tk
   ```
## 🛠️ Configuração de Desenvolvimento
1. Instale fontes musicais:
   ```bash
   sudo apt-get install fonts-noto-music
   # Instalar dependências do sistema para PyGame
   sudo apt-get install python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
   ```
   ```bash
   pip install -r requirements.txt
   ```


