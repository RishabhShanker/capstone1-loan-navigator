from decimal import Decimal
from typing import Optional, Literal, List, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from app.agents.whatif_calc import compute_emi, build_schedule, with_prepayment, totals

router = APIRouter(prefix="/whatif", tags=["whatif"])

class Prepayment(BaseModel):
    month: int = Field(ge=1, description="Month number (1-based) to apply prepayment at end of that month")
    amount: float = Field(gt=0, description="Prepayment amount")
    mode: Literal["reduce_tenure","reduce_emi"] = "reduce_tenure"

class WhatIfReq(BaseModel):
    loan_amount: float = Field(gt=0)
    annual_interest_rate: float = Field(gt=0, lt=100, description="APR in percent")
    tenure_months: int = Field(ge=1, le=1200)
    prepayment: Optional[Prepayment] = None

    @field_validator("loan_amount","annual_interest_rate",mode="before")
    @classmethod
    def no_strs(cls, v):
        if isinstance(v, str):
            raise ValueError("Use numeric values, not strings")
        return v

class Row(BaseModel):
    month: int
    opening: float
    interest: float
    principal: float
    emi: float
    prepayment: float
    closing: float

class WhatIfResp(BaseModel):
    emi: float
    tenure_months: int
    total_interest: float
    total_payment: float
    schedule: List[Row]

def _to_float_rows(sched: List[Dict]) -> List[Row]:
    # Convert Decimals to floats for JSON
    out: List[Row] = []
    for r in sched:
        out.append(Row(
            month=r["month"],
            opening=float(round(r["opening"], 2)),
            interest=float(round(r["interest"], 2)),
            principal=float(round(r["principal"], 2)),
            emi=float(round(r["emi"], 2)),
            prepayment=float(round(r["prepayment"], 2)),
            closing=float(round(r["closing"], 2)),
        ))
    return out

@router.post("", response_model=WhatIfResp)
def whatif(req: WhatIfReq):
    P   = Decimal(str(req.loan_amount))
    apr = Decimal(str(req.annual_interest_rate))
    n   = int(req.tenure_months)

    try:
        if req.prepayment:
            sched = with_prepayment(
                P, apr, n,
                month=req.prepayment.month,
                amount=Decimal(str(req.prepayment.amount)),
                mode=req.prepayment.mode
            )
        else:
            sched = build_schedule(P, apr, n)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    emiv = compute_emi(P, apr, n) if not req.prepayment or req.prepayment.mode=="reduce_tenure" else float(_to_float_rows(sched)[-1].emi)
    t = totals(sched)

    return WhatIfResp(
        emi=float(round(emiv, 2)),
        tenure_months=t["tenure_months"],
        total_interest=float(t["total_interest"]),
        total_payment=float(t["total_payment"]),
        schedule=_to_float_rows(sched)
    )
