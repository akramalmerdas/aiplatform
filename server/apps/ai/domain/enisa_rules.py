from typing import Dict, Any
def check_enisa_basic(intake:Dict[str,Any])->Dict[str,Any]:
    ask=float(intake.get("requested_loan_eur") or 0)
    own=float(intake.get("own_funds_eur") or 0)
    return {"candidate_line_hint":"Crecimiento","own_funds_ok":own>=ask,
    "audit_required":ask>300000,
    "sources":["https://www.enisa.es/es/financia-tu-empresa/lineas-de-financiacion",
    "https://www.enisa.es/es/financia-tu-empresa/lineas-de-financiacion/d/crecimiento"]}
