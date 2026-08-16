# AI-Powered Debt Relief & Financial Recovery Platform

An intelligent, Python-first financial technology application designed to help individuals analyze cash flows, assess default risk using Machine Learning, compare optimization strategies (Avalanche vs. Snowball), retrieve grounded financial education using RAG (Retrieval-Augmented Generation), generate customized AI recovery plans via Google Gemini, run what-if simulators, and compile comprehensive recovery statements.

---

## 1. Project Overview
The **AI-Powered Debt Relief & Financial Recovery Platform** provides users with an end-to-end sandbox to catalog their financial profile, income streams, monthly expenditures, and outstanding liabilities. It combines deterministic Python financial algorithms with scikit-learn models and Google Gemini API workflows to offer safe, explainable, and personalized debt recovery guidance.

## 2. Problem Statement
Many individuals struggling with multiple debts (credit cards, loans) lack the financial literacy to optimize their payoff order. Traditional methods either require manual spreadsheet calculations or depend on black-box AI tools that are prone to hallucinating numerical balances. Furthermore, users often find personal finance concepts confusing and struggle to contextualize generic financial advice.

## 3. Project Objectives
- **Persist Data Locally**: Securely log cash flow details and debts without cloud-account leaks.
- **Compute Ratios Accurately**: Prevent AI engines from performing raw math by utilizing a verified Python calculation engine.
- **Explain Choices Clearly**: Translate complex amortization schedules into natural language summaries using Google Gemini.
- **Provide Grounded Education**: Implement a local RAG vector database to answer user queries using trusted, pre-seeded materials.
- **Assess Defaults via ML**: Deploy an explainable Random Forest classifier to predict default risk categories separate from heuristic credit scores.

---

## 4. Technology Stack
- **Language**: Python 3.10+
- **Frontend / Interface**: Streamlit
- **Generative AI**: Google Gemini API via official `google-generativeai` SDK
- **Embeddings**: Google Gemini Embedding API (`text-embedding-004`)
- **Vector Database**: FAISS (`faiss-cpu`) for local cosine similarity search
- **Data Processing**: Pandas & NumPy
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Database**: SQLite (SQLAlchemy ORM)
- **Data Visualizations**: Plotly Express & Plotly Graph Objects
- **Testing**: pytest

---

## 5. Architecture & Workflows

### System Architecture
```
                         USER (Web Browser)
                           │
                           ▼
                 ┌──────────────────┐
                 │    STREAMLIT     │
                 │   PYTHON UI      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ PYTHON SERVICES  │
                 └────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
 Financial Analysis   Machine Learning   Generative AI
  - Debt Engine        - Risk Predictor  - Gemini Service
  - Budget Engine      - Random Forest   - Prompt Engine
  - Health Score       - Synthetic Data  - RAG Pipeline
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼
                    SQLITE DATABASE (via SQLAlchemy)
                          │
                          ▼
                    REPORTS & PROGRESS
```

### RAG System Pipeline
```
┌────────────────────────┐      ┌────────────────────────┐      ┌─────────────────────────┐
│ Financial Articles     │ ───> │  Gemini Embedding API  │ ───> │ Vector Database         │
│ (Markdown/Text files)  │      │   (text-embedding-004) │      │ (FAISS / Numpy Array)   │
└────────────────────────┘      └────────────────────────┘      └───────────┬─────────────┘
                                                                            │
                                                                            ▼
┌────────────────────────┐      ┌────────────────────────┐      ┌─────────────────────────┐
│  Grounding Context     │ <─── │ Vector Distance Match  │ <─── │ User Question / Query   │
│  (Pass top-K articles) │      │   (Cosine Similarity)  │      │ ("Explain Avalanche")   │
└───────────┬────────────┘      └────────────────────────┘      └─────────────────────────┘
            │
            ▼
┌────────────────────────┐      ┌────────────────────────┐
│  Gemini GenAI model    │ ───> │  Grounded Response     │
│ (gemini-1.5-flash)     │      │  (with cited sources)  │
└────────────────────────┘      └────────────────────────┘
```

### Machine Learning Workflow
1. **Feature Engineering**: Standardizes 8 features (`income`, `total_debt`, `dti_ratio`, `expense_ratio`, `savings_rate`, `active_debts_count`, `max_apr`, `disposable_income`) into a normalized NumPy array.
2. **Synthetic Data**: Generates 5,000 samples mapping features to risk levels using logical rules with 5% injected random classification noise.
3. **Training**: Fits a RandomForestClassifier (accuracy ~95%) and outputs classification metrics.
4. **Serialization**: Exports model to `data/models/risk_model.joblib`. Auto-trains on-demand if the file is missing during initialization.

---

## 6. Project Structure
```
ai-debt-relief-platform/
│
├── app.py                     # Main Streamlit Entrypoint
│
├── requirements.txt           # Project Dependencies
├── README.md                  # Project Documentation
├── .env.example               # Template for Environment Variables
├── .gitignore                 # Git ignore rules
│
├── config/
│   ├── settings.py            # App & Database Settings
│   └── constants.py           # Financial & Risk constants
│
├── ui/
│   ├── dashboard.py           # Metrics and Plotly Charts
│   ├── profile.py             # User profile form
│   ├── income_expenses.py     # Income & Expenses inputs and classifications
│   ├── debt_management.py     # CRUD operations for debts
│   ├── financial_analysis.py  # Health score & DTI ratios
│   ├── debt_strategy.py       # Avalanche & Snowball comparison
│   ├── recovery_plan.py       # AI-Generated recovery plans
│   ├── chatbot.py             # Chatbot interface with RAG
│   ├── knowledge_hub.py       # Educational articles search
│   ├── what_if.py             # What-if scenario simulator
│   ├── progress.py            # Progress tracking interface
│   └── reports.py             # Statement compiler
│
├── financial/
│   ├── analyzer.py            # Summary analyzer (income, expense, debt)
│   ├── debt_engine.py         # Payoff strategies (Avalanche, Snowball)
│   ├── health_score.py        # Explainable, deterministic health scorer
│   ├── payoff_calculator.py   # Month-by-month debt amortization
│   └── what_if_engine.py      # Calculations for scenarios
│
├── ai/
│   ├── gemini_service.py      # Gemini API communications
│   ├── prompt_engine.py       # Structured prompts and constraints
│   ├── recovery_generator.py  # Recovery plan orchestrator
│   ├── financial_assistant.py # Chatbot helper matching context + RAG
│   └── response_validator.py  # Validates AI response values against Python outputs
│
├── rag/
│   ├── document_loader.py     # Loads financial articles
│   ├── chunker.py             # Text splitting
│   ├── vector_store.py        # FAISS index management
│   └── pipeline.py            # Integrates search with LLM grounding
│
├── ml/
│   ├── feature_engineering.py  # Feature mapping
│   ├── train.py               # Dataset generation and training script
│   └── predictor.py           # Risk level predictor
│
├── database/
│   ├── database.py            # Connection setup & session management
│   ├── models.py              # SQLAlchemy database models
│   └── repository.py          # DB operations (CRUD) for all models
│
├── models/
│   ├── financial_models.py    # Pydantic data schemas
│   └── debt_models.py
│
├── data/
│   ├── knowledge/             # Markdown files containing educational materials
│   └── models/                # Serialized ML model
│
└── tests/
    ├── test_financial.py      # Unit tests
    ├── test_debt.py
    ├── test_budget.py
    └── test_ai.py
```

---

## 7. Financial Safety Disclaimer
This platform provides educational and informational financial guidance based on the information supplied by the user. It does not replace professional financial, legal, tax, credit, or investment advice. Results are estimates and actual outcomes may vary.

**We never guarantee:**
- Complete debt elimination
- Credit-score improvements
- Mandatory interest savings

---

## 8. Installation & Setup

### Prerequisites
- Python 3.10+ installed
- Google Gemini API Key

### Steps

1. **Clone the Repository** and navigate to the folder:
   ```bash
   cd "AI POWERED DEBT RELIEF & FINANCIAL RECOVERY PLATFORM"
   ```

2. **Initialize and Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment variables**:
   Create a `.env` file in the root directory (copy from `.env.example`) and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```

5. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

6. **Running Unit Tests**:
   ```bash
   pytest
   ```

---

## 9. Testing Summary
The project contains 24 unit tests covering:
- **Income & Expense Schemas**: Validates categories, frequencies, and checks against negative amounts.
- **Debt Schemas**: Validates APR boundaries, minimum payments, and status defaults.
- **Repository CRUD**: Validates database insertions, updates, reads, and deletes inside an in-memory SQLite setup.
- **Health Scorer & Metrics**: Confirms accuracy of DTI, disposable cash flow, savings rate, and risk assessments.
- **RAG Chunker & Loader**: Tests character limits splitting and file parsers.
- **ML Features & Predictor**: Verifies feature array dimensions and RandomForest class probabilities.
- **AI Validator**: Verifies hallucination filters and warning triggers.
