from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from docbr_pro.core.cpf import CPF
from docbr_pro.core.cnpj import CNPJ
from docbr_pro.core.exceptions import DocbrError
from docbr_pro.core.generator import generate_cpf, generate_cnpj
from docbr_pro.core.sanitizer import sanitize_cpf, sanitize_cnpj

app = FastAPI(
    title="docbr-pro API",
    description="API REST para validação e geração de CPF/CNPJ brasileiros.",
    version="0.1.0"
)

class ValidationResponse(BaseModel):
    valid: bool
    document: str
    formatted: str
    type: str
    fiscal_region: str | None = None

class GenerationResponse(BaseModel):
    document: str
    type: str

@app.get("/validate/{document}", response_model=ValidationResponse)
async def validate_document(document: str):
    clean = "".join(c for c in document if c.isalnum())
    
    try:
        if len(clean) > 11:
            sanitized = sanitize_cnpj(document)
            cnpj_obj = CNPJ(sanitized)
            return ValidationResponse(
                valid=True,
                document=cnpj_obj.clean,
                formatted=cnpj_obj.formatted,
                type="CNPJ"
            )
        else:
            sanitized = sanitize_cpf(document)
            cpf_obj = CPF(sanitized)
            return ValidationResponse(
                valid=True,
                document=cpf_obj.clean,
                formatted=cpf_obj.formatted,
                type="CPF",
                fiscal_region=cpf_obj.fiscal_region
            )
    except DocbrError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/generate/cpf", response_model=GenerationResponse)
async def api_generate_cpf(
    formatted: bool = True,
    region: str | None = Query(None, description="Região fiscal (0-9)")
):
    doc = generate_cpf(region=region, formatted=formatted)
    return GenerationResponse(document=doc, type="CPF")

@app.get("/generate/cnpj", response_model=GenerationResponse)
async def api_generate_cnpj(
    formatted: bool = True,
    alphanumeric: bool = True
):
    doc = generate_cnpj(alphanumeric=alphanumeric, formatted=formatted)
    return GenerationResponse(document=doc, type="CNPJ")
