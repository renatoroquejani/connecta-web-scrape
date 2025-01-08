# Connecta Web Scraper API

A FastAPI application that scrapes product data from Connecta Venda catalogs and returns it as TEXT.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/connecta-web-scraper.git
cd connecta-web-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- On Windows:
```bash
venv\Scripts\activate
```
- On macOS/Linux:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Local Development

1. Start the FastAPI server:
```bash
python app.py
```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

### Using Docker Compose

1. Build and start the container:
```bash
docker-compose up
```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### Scrape Catalog
- **GET** `/scrape`
- Parameters:
  - `url`: The Connecta catalog URL to scrape
- Example:
```bash
http://localhost:8000/scrape?url=https://app.conectavenda.com.br/c25adbbf63a83befa6c04e686c3c090f
```

## Requirements

- Python 3.8+
- Docker (optional)
- See [requirements.txt](requirements.txt) for complete dependency list

## License

MIT License - See [LICENSE](LICENSE) for details
