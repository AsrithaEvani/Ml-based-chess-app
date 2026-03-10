# ♟ Chess AI — Django Application

This project is a web-based chess game built using Django that allows users to play against an AI opponent.  
The application includes a custom chess engine that uses the Minimax algorithm with Alpha-Beta pruning to make intelligent moves.  
It supports standard chess rules and provides an interactive user interface for gameplay.

---

## Features

- AI opponent implemented using the **Minimax algorithm** with **Alpha-Beta pruning** (configurable depth from 1–4)
- Position evaluation based on **material values and piece-square tables**
- Implementation of **complete chess rules**, including:
  - Castling
  - En passant
  - Pawn promotion
  - Check, checkmate, and stalemate detection
- Interactive **dark-themed user interface** with highlighted legal moves
- **Move history tracking**
- **Captured pieces display**
- **Material advantage indicator**
- Option to **play as either White or Black**

---

## Setup and Installation

### 1. Install Django

```bash
pip install Django
chess_project/
├── manage.py
├── requirements.txt
├── chess_project/          # Django project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── chess_app/              # Main chess application
    ├── chess_engine.py     # Core chess logic and AI implementation
    ├── views.py            # Backend API endpoints
    ├── urls.py             # Application routing
    └── templates/
        └── chess_app/
            └── index.html  # User interface for the chess game