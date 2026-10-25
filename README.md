# Multi-Agent Emergency Response & Disaster Management System

## Overview

The Multi-Agent Emergency Response & Disaster Management System is a prototype that demonstrates how multiple AI agents can coordinate to assess weather conditions, estimate a risk level, identify potential shelter records, and generate emergency recommendations.

The project uses LangGraph to orchestrate agents and Streamlit to provide an interactive command-center dashboard.

## Key Features

- **Weather Agent:** Retrieves live weather data using the Open-Meteo API.
- **Risk Assessment Agent:** Calculates an illustrative risk score from rainfall, precipitation, and wind speed.
- **Monitoring Agent:** Generates recommendations for low-risk scenarios.
- **Warning Agent:** Provides precautionary guidance for medium-risk scenarios.
- **Resource Agent:** Searches the SQLite database for shelter records.
- **Communication Agent:** Generates a message based on the workflow results.
- **Finalization Agent:** Produces the final workflow summary.
- **Interactive Dashboard:** Supports Live Weather and Demo Mode.
- **Error Handling:** Includes weather API retries, input validation, and safe fallback recommendations.
- **Automated Testing:** Tests risk classification, workflow routing, database filtering, and error handling.

## Technology Stack

- **Language:** Python
- **Agent Orchestration:** LangGraph, LangChain
- **Dashboard:** Streamlit
- **Weather API:** Open-Meteo
- **Database:** SQLite
- **Testing:** Python test scripts
- **Development Environment:** VS Code and Python virtual environment

## Project Structure

```text
emergency-response-system/
├── agents.py
├── app.py
├── day1_workflow.py
├── requirements.txt
├── run.py
├── shelter_db.py
├── shelters.db
├── state.py
├── weather_service.py
├── workflow.py
├── test_full_workflow.py
├── test_output_validation.py
├── test_resource_agent.py
├── test_resource_logging.py
├── test_risk_agent.py
├── test_risk_validation.py
├── test_shelter_db.py
├── test_weather_errors.py
└── test_weather_retry.py
```

## Installation and Setup

### 1. Clone or download the project

Open the project directory in VS Code.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Check dependencies

```powershell
python -m pip check
```

### 6. Launch the dashboard

```powershell
streamlit run app.py
```

Open the local URL displayed in the terminal, typically `http://localhost:8501`.

## Running Tests

Run the following commands from the project directory with the virtual environment activated:

```powershell
python test_shelter_db.py
python test_resource_agent.py
python test_risk_agent.py
python test_risk_validation.py
python test_resource_logging.py
python test_weather_retry.py
python test_weather_errors.py
python test_output_validation.py
python test_full_workflow.py
```

The end-to-end workflow tests cover LOW, MEDIUM, and HIGH prototype risk scenarios, including conditional routing and execution-trace validation.

## Workflow Architecture

```text
Weather Agent
      |
      v
Risk Assessment Agent
      |
      v
Conditional Routing
      |
      +---- LOW ------> Monitoring Agent
      |
      +---- MEDIUM ---> Warning Agent
      |
      +---- HIGH -----> Resource Agent
                           |
                           v
                  Communication Agent
                           |
                           v
                    Finalization Agent
                           |
                           v
                      Final Summary
```

## Important Limitations

- Risk scores and thresholds are illustrative prototype logic, not official flood-risk assessments or government warning criteria.
- Weather observations may be delayed or incomplete and should not replace official weather alerts.
- Shelter database records may be fictional test records or otherwise unverified. A database match does not establish that a shelter is real, open, safe, or available.
- The system does not replace emergency services or the instructions of local authorities.
- This project is a demonstration prototype and should not be used as the sole basis for real-world emergency decisions.

## Future Improvements

- Integrate authoritative disaster alerts and verified shelter information.
- Improve risk estimation using validated historical weather and flood data.
- Add mapping and distance-based shelter recommendations.
- Introduce role-based access, persistent event history, and monitoring.
- Add deployment automation and broader integration tests.

## Project Status

The prototype includes a working Streamlit dashboard, live weather integration, simulated demonstration scenarios, conditional multi-agent workflows, SQLite shelter lookup, and automated tests.

Further validation, documentation review, and deployment checks remain part of project readiness.