Slide fight tactics
```
slide_fight_tactics/
├── main.py                        # Entrypoint
├── requirements.txt
├── config/                        # Configuration and constants
│   └── settings.py
│   └── paths.py
│
├── interface/                     # Presentation Layer (UI/UX)
│   └── main_ui.py                 # GUI app (Tkinter, etc.)
│   └── chat_interface.py          # Chat window with history
│   └── slide_selector.py          # Slide thumbnail interaction
│   └── dragdrop_handler.py        # Drag & drop handler
│
├── application/                   # Application Layer (Controllers)
│   └── query_controller.py
│   └── deck_manager.py
│   └── wallpaper_controller.py
│
├── services/                      # Service Layer (Business logic)
│   └── docling_service.py         # Interface to Docling
│   └── prompt_generator.py        # Create prompts for Gemma
│   └── gemma_client.py            # Call Gemma-3n via Ollama
│   └── content_ranker.py          # Rank extracted content
│
├── data/                          # Data Layer (DB models and access)
│   └── database.py                # Init & connect SQLite
│   └── query_builder.py           # Build content queries
│   └── models/                    # ORM-like schema classes (optional)
│       └── deck.py
│       └── slide.py
│       └── page.py
│       └── content.py
│       └── access_log.py
│
├── infra/                         # Infrastructure Layer (System integration)
│   └── file_watcher.py            # Detect new PDFs in folder
│   └── pdf_opener.py              # Open slide by OS
│   └── wallpaper_generator.py     # Generate wallpaper from access logs
│   └── ollama_runner.py           # Interface with Ollama CLI
│
├── assets/                        # Images, wallpaper thumbnails
│   └── icons/
│   └── wallpapers/
│
├── tests/                         # Unit and integration tests
│   └── test_gemma_prompt.py
│   └── test_docling_extraction.py
│
└── README.md
```