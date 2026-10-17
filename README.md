# Northwind Payments Gateway (`svc_payments_gateway`)

High-throughput acquirer routing and 3-D Secure validation microservice for Northwind Pay.

## Architectural Invariants & Governance

This repository is governed by **INVARIX Continuous Pre-Merge Architectural Risk Gate**:
- **Service ID**: `svc_payments_gateway`
- **Critical Topology Dependencies**: Depends on `svc_checkout_api`, `svc_card_vault`, and `svc_fraud_scoring`.
- **Percolation Circuit Breaker**: Blocks merges if avalanche risk score $\ge 75$ or if temporal expiry collisions are detected.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Running Pre-Merge Risk Scan Locally

```bash
pip install -r requirements.txt
invarix check -s svc_payments_gateway --horizon 30
```
