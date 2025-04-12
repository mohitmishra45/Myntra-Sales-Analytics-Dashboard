# Myntra Sales Analytics Dashboard Pro

A comprehensive analytics dashboard for Myntra sales data, featuring real-time data updates, interactive visualizations, and AI-powered insights.

## Features

- 📊 Real-time data monitoring and updates
- 📈 Interactive sales trend analysis
- 🏢 Brand performance tracking
- 📍 Geographical sales analysis
- 👥 Customer insights
- 🤖 AI-powered sales predictions
- 💡 Optimization suggestions
- 🔒 Secure authentication system

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/myntra-analytics.git
cd myntra-analytics
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key
```

## Configuration

1. Update the data source path in `dashboard.py`:
```python
EXCEL_PATH = "path/to/your/Myntra_dataset.csv"
```

2. Configure authentication settings in `auth.py` (if needed)

## Running the Dashboard

1. Start the dashboard:
```bash
streamlit run dashboard.py
```

2. Open your web browser and navigate to:
```
http://localhost:8501
```

## Deployment

### Option 1: Streamlit Cloud

1. Push your code to a GitHub repository
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy the dashboard

### Option 2: Heroku

1. Create a `Procfile`:
```
web: streamlit run dashboard.py
```

2. Create a `runtime.txt`:
```
python-3.8.18
```

3. Deploy to Heroku:
```bash
heroku create myntra-analytics
git push heroku main
```

### Option 3: Docker

1. Create a `Dockerfile`:
```dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py"]
```

2. Build and run the container:
```bash
docker build -t myntra-analytics .
docker run -p 8501:8501 myntra-analytics
```

## Project Structure

```
myntra-analytics/
├── dashboard.py          # Main dashboard application
├── auth.py              # Authentication module
├── data_watcher.py      # Real-time data monitoring
├── requirements.txt     # Project dependencies
├── README.md           # Project documentation
└── .env                # Environment variables
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 