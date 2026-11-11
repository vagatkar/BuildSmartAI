# BuildSmart AI — Construction Project Intelligence Dashboard

A self-initiated portfolio prototype demonstrating how Python, data processing and workflow automation can support construction project controls.

## Run locally
1. Install Python 3.10+.
2. Create and activate a virtual environment.
3. Run: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`

## Included
- Project overview KPIs
- Phase progress and activity status
- Planned schedule timeline
- Budget vs actual cost view
- Contractor performance register
- Risk register and rule-based alerts
- Downloadable weekly status summary

## Data integrity
All project names, contractor names, costs, dates, progress figures and risks in the included CSV files are fictional demonstration data. This is not a Sanctuary project and must not be presented as a deployed client solution or as a tool already used by a construction team.

## Suggested next development steps
- Replace CSV inputs with editable forms and SQLite persistence.
- Add APScheduler for scheduled weekly report generation.
- Add authenticated data import and audit trail.
- Add LLM-assisted narrative generation with human review.
- Add baseline / earned-value calculations and change-order tracking.
