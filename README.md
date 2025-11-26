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
EXCEL_PATH = "Myntra_dataset_large.csv"
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

### Deploying to Streamlit Cloud

1.  **Push to GitHub**: Ensure your code is pushed to a GitHub repository.
2.  **Create App**: Go to [Streamlit Cloud](https://streamlit.io/cloud) and click "New app".
3.  **Select Repository**: Choose your repository, branch, and the main file path (`dashboard.py`).
4.  **Configure Secrets**:
    *   Click on "Advanced settings" before deploying, or go to your app settings after deployment.
    *   Navigate to the "Secrets" tab.
    *   Add your Gemini API key in the following format:
        ```toml
        GEMINI_API_KEY = "your_gemini_api_key_here"
        ```
5.  **Deploy**: Click "Deploy!".

### Important Notes
*   **Data Persistence**: This app uses a CSV file (`users.csv`) for user storage. On Streamlit Cloud, the file system is ephemeral, meaning any new users registered will be lost when the app restarts or re-deploys. For a production application, consider connecting to a database (e.g., Google Sheets, Firestore, or SQL).
*   **Dependencies**: Streamlit Cloud will automatically install dependencies from `requirements.txt`.

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