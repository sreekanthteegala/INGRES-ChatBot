# INGRES Groundwater AI Chatbot

An intelligent chatbot system for querying and analyzing groundwater data from India's Central Ground Water Board (CGWB). Built with FastAPI, React, and LangChain.

## 🌐 Live Demo

**🚀 Try it now**: [Coming Soon - Deploy using DEPLOYMENT_GUIDE.md]

**Backend API**: [Your Render URL]  
**API Documentation**: [Your Render URL]/docs

## 🎯 Features

- **Natural Language Queries**: Ask questions in plain English about groundwater data
- **Filter-Based Queries**: Use structured filters for precise data retrieval
- **Theme System**: 4 beautiful themes (Light, Dark, Ocean, Forest)
- **Data Visualization**: Interactive charts and tables using Recharts
- **SQL-Driven**: Zero hallucination - all data comes from database queries
- **Multi-Year Support**: Query data across multiple years (2016-2025)
- **District-Level Data**: Access detailed district-level groundwater information

## 📊 Data Coverage

- **Years**: 2016-17, 2019-20, 2021-22, 2022-23, 2023-24, 2024-25
- **States/UTs**: 37 states and union territories
- **Districts**: ~700 districts across India
- **Records**: 4,160 clean, validated records
- **Metrics**: 154 columns including:
  - Total Ground Water Availability
  - Rainfall
  - Ground Water Recharge
  - Extraction Rates
  - Environmental Flows
  - And more...

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ingres-chatbot
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

### Running the Application

1. **Start the backend server**
```bash
# From project root
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

2. **Start the frontend server** (in a new terminal)
```bash
cd frontend
npm run dev
```

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

## 📁 Project Structure

```
ingres-chatbot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── chatbot_v2.py        # LangChain chatbot with validation
│   ├── query_handler.py     # Direct SQL query handler
│   └── security.py          # Input sanitization
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── themes.js        # Theme system
│   │   └── components/      # React components
│   ├── index.html
│   └── package.json
├── data/
│   └── raw_excel/           # Original Excel files from CGWB
├── notebooks/
│   ├── preprocess_groundwater_data.py    # Data preprocessing
│   ├── create_database.py                # Database creation
│   └── update_database_with_cleaned_data.py
├── processed_data/
│   ├── groundwater_cleaned.csv           # Cleaned dataset
│   └── preprocessing_report.txt          # Validation report
├── groundwater.db           # SQLite database
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
└── README.md               # This file
```

## 🔧 API Endpoints

### Chat Endpoint
```bash
POST /chat
Content-Type: application/json

{
  "question": "Which state has the highest groundwater availability?"
}
```

### Filter Query Endpoint
```bash
POST /filter_query
Content-Type: application/json

{
  "metric": "Total Ground Water Availability in the area (ham) Fresh",
  "states": ["ASSAM"],
  "years": ["2024_25"]
}
```

## 💡 Usage Examples

### Natural Language Queries

```
"Which state has the highest groundwater availability?"
"What is the rainfall in Punjab for 2023-24?"
"Top 5 states by groundwater recharge"
"Show extraction rate in Rajasthan"
"Compare groundwater in Assam and Andhra Pradesh"
```

### Filter Queries

1. Select a metric (e.g., "Total Ground Water Availability")
2. Select state(s) (e.g., "Assam", "Punjab")
3. Select year(s) (e.g., "2024-25")
4. Click "Run Query"

## 🎨 Theme System

Switch between 4 themes using the buttons in the header:
- ☀️ **Light Mode**: Clean white background (default)
- 🌙 **Dark Mode**: Dark slate background for low-light environments
- 🌊 **Ocean Theme**: Cyan/blue colors with water theme
- 🌿 **Forest Theme**: Green/emerald tones with nature theme

Theme preference is saved in localStorage and persists across sessions.

## 📊 Data Processing

### Preprocessing Pipeline

The data preprocessing pipeline ensures 100% data integrity:

1. **Dynamic Header Detection**: Automatically finds actual header row
2. **Multi-Level Headers**: Handles C, NC, PQ, Total, Fresh, Saline categories
3. **Metadata Removal**: Removes report metadata rows
4. **Duplicate Detection**: Identifies and removes duplicates
5. **Column Standardization**: Cleans and standardizes column names
6. **Data Type Conversion**: Converts numeric columns properly
7. **Validation**: Comprehensive validation and anomaly detection

**Run preprocessing**:
```bash
python notebooks/preprocess_groundwater_data.py
```

**Update database**:
```bash
python notebooks/update_database_with_cleaned_data.py
```

## 🔍 Key Features

### 1. Zero Hallucination
- All responses come from SQL queries
- Strict validation rejects any generated numbers
- No approximations or estimates

### 2. Correct Aggregation
- **Rainfall**: Uses AVG() (intensity measure)
- **Availability**: Uses SUM() for state totals (STOCK variable)
- **Recharge**: Uses SUM() (FLOW variable)
- **Extraction Rate**: Uses AVG() (percentage)

### 3. Multi-Year Support
- Single year: Returns specific year data
- Multiple years: Returns year-wise breakdown
- Proper handling of STOCK vs FLOW variables

### 4. Fast Performance
- Direct SQL handler for common queries (<1 second)
- LLM fallback for complex queries (5-10 seconds)
- No timeout errors

## 🛠️ Development

### Adding New Metrics

1. Update `COLUMN_MAP` in `backend/query_handler.py`
2. Add aggregation rule in `AGG_RULES`
3. Add unit in `UNITS`
4. Update `valid_metrics` in `backend/main.py`
5. Update `METRICS` array in `frontend/src/App.jsx`

### Running Tests

```bash
# Test preprocessing
python notebooks/preprocess_groundwater_data.py

# Test database
python notebooks/create_database.py

# Test API
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Which state has highest groundwater?"}'
```

## 📝 Data Sources

Data sourced from:
- **Central Ground Water Board (CGWB)**
- **Ministry of Jal Shakti, Government of India**
- Dynamic Groundwater Resources Reports (2016-2025)

## ⚠️ Important Notes

### Data Integrity Rules
1. **NEVER generate synthetic data**
2. **NEVER fill missing values with assumptions**
3. **ONLY use real values from Excel files**
4. **Preserve original data integrity at all costs**

### Aggregation Rules
- **STOCK variables** (Availability): Use latest year, don't sum across years
- **FLOW variables** (Recharge): Can sum across years
- **Rainfall**: Always use AVG(), never SUM()
- **Percentages**: Always use AVG(), never SUM()

## 🐛 Troubleshooting

### Backend not starting
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Restart backend
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend not loading
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database issues
```bash
# Restore from backup
cp groundwater_backup.db groundwater.db

# Or regenerate from cleaned data
python notebooks/update_database_with_cleaned_data.py
```

## 📄 License

This project is developed for the Central Ground Water Board (CGWB), Ministry of Jal Shakti, Government of India.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please contact the development team.

---

## 🚀 Deployment

Ready to deploy? Follow our comprehensive guides:

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment instructions
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Quick checklist for deployment

### Quick Deploy:

**Backend (Render):**
```bash
Build: pip install -r requirements.txt
Start: uvicorn backend.main:app --host 0.0.0.0 --port 10000
```

**Frontend (Vercel):**
```bash
Root: frontend
Framework: Vite
Env: VITE_API_URL=https://your-backend-url.onrender.com
```

---

**Built with ❤️ for sustainable groundwater management in India**
