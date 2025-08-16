from fastapi import FastAPI, HTTPException from pydantic import BaseModel, Field import uuid, time, json, hashlib

app = FastAPI(title="MNNR API v0")

toy in-memory stores
WALLETS = {} CONTRACTS = {} RECEIPTS = {}

class WalletCreate(BaseModel): name: str

class Wallet(BaseModel): id: str name: str pubkey: str

class ContractCreate(BaseModel): payer_wallet: str payee_wallet: str unit_price_usd: float unit: str = "call" daily_cap_usd: float = 2.0 currency: str = "USD" rail: str = "stripe-usd" # or "usdc-sol" allowed_scope: str = "general"

class Contract(BaseModel): id: str created_at: int active: bool = True data: dict

class AuthorizeReq(BaseModel): contract_id: str max_spend_usd: float = 0.20 scope: str = "general" ttl_s: int = 600

class AllowanceToken(BaseModel): token: str exp: int

class SettleReq(BaseModel): contract_id: str units: int = 1 meta: dict = {} proof: str = ""

class Receipt(BaseModel): id: str timestamp: int payer_wallet: str payee_wallet: str contract_id: str units: int unit_price_usd: float amount_usd: float currency: str rail: str settlement_ref: str = "" call_hash: str outcome: str = "success" hash: str

def canonical_hash(d: dict) -> str: s = json.dumps(d, sort_keys=True, separators=(",", "😊) return hashlib.sha256(s.encode()).hexdigest()

@app.post("/v1/wallets", response_model=Wallet) def create_wallet(body: WalletCreate): wid = str(uuid.uuid4()) pubkey = f"mnnr_{wid[:8]}" w = Wallet(id=wid, name=body.name, pubkey=pubkey) WALLETS[wid] = w.model_dump() return w

@app.post("/v1/contracts", response_model=Contract) def create_contract(body: ContractCreate): if body.payer_wallet not in WALLETS or body.payee_wallet not in WALLETS: raise HTTPException(400, "invalid wallet(s)") cid = str(uuid.uuid4()) c = Contract(id=cid, created_at=int(time.time()), data=body.model_dump()) CONTRACTS[cid] = c.model_dump() return c

@app.post("/v1/authorize", response_model=AllowanceToken) def authorize(body: AuthorizeReq): if body.contract_id not in CONTRACTS: raise HTTPException(404, "contract not found") exp = int(time.time()) + body.ttl_s token = json.dumps({"cid": body.contract_id, "max": body.max_spend_usd, "scope": body.scope, "exp": exp}) # NOTE: sign/JWT later; plain for demo return AllowanceToken(token=token, exp=exp)

@app.post("/v1/settlements", response_model=Receipt) def settle(body: SettleReq): c = CONTRACTS.get(body.contract_id) if not c: raise HTTPException(404, "contract not found") data = c["data"] amount = round(body.units * float(data["unit_price_usd"]), 6) base = { "timestamp": int(time.time()), "payer_wallet": data["payer_wallet"], "payee_wallet": data["payee_wallet"], "contract_i
