# SpectraWorkshop

View and manipulate NIR spectra with a modern PySide6 interface.

## Features

- **MDI Interface**: Multiple document interface for working with several files simultaneously
- **CSV Import/Export**: Easy data import and export functionality
- **Dock Widgets**: Customizable side panels for properties and file management
- **Modern UI**: Built with PySide6 for a native look and feel

## Project Structure

```
SpectraWorkshop/
├── src/
│   └── spectra_workshop/
│       ├── __init__.py
│       ├── main.py          # Application entry point
│       ├── ui/
│       │   ├── __init__.py
│       │   └── main_window.py  # Main window with MDI interface
│       └── utils/           # Utility modules
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SpectraWorkshop.git
cd SpectraWorkshop
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python -m src.spectra_workshop.main
```

Or install the package and use the entry point:
```bash
pip install -e .
spectra-workshop
```

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests (if available)
5. Submit a pull request

## Requirements

- Python >= 3.8
- PySide6 >= 6.6.0

## License

MIT License (or your preferred license)
