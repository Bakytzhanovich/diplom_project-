import sqlite3
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.database import get_db

app = FastAPI(title="Dynamic Access Control Prototype API")

def initialize_database():
    db_path = Path("access_control.db")
    schema_path = Path("schema.sql")
    seed_path = Path("seed.sql")

    if db_path.exists():
        return

    connection = sqlite3.connect(db_path)

    with open(schema_path, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    with open(seed_path, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    connection.commit()
    connection.close()


initialize_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class AccessCheckRequest(BaseModel):
    username: str
    resource: str
    action: str


class RiskEventRequest(BaseModel):
    username: str
    event_type: str
    resource: str | None = None
    action: str | None = None
    severity: str = "low"


@app.get("/")
def root():
    return {"status": "API is running"}


@app.post("/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(
        text("""
            SELECT u.id, u.username, u.password, u.department, u.is_active, r.name AS role
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = :username
        """),
        {"username": data.username}
    ).mappings().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user["is_active"]:
        raise HTTPException(status_code=403, detail="User account is inactive")

    # For prototype only. Later replace with password hash verification.
    if data.password != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    db.execute(
        text("""
            INSERT INTO audit_logs (user_id, action, resource, decision, risk_score)
            VALUES (:user_id, 'login', 'system', 'ALLOW', 0)
        """),
        {"user_id": user["id"]}
    )
    db.commit()

    return {
        "status": "success",
        "username": user["username"],
        "role": user["role"],
        "department": user["department"],
        "token": f"prototype-token-{user['username']}"
    }


@app.post("/access/check")
def access_check(data: AccessCheckRequest, db: Session = Depends(get_db)):
    user = db.execute(
        text("""
            SELECT u.id, u.username, u.department, r.name AS role
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = :username
        """),
        {"username": data.username}
    ).mappings().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    permission = db.execute(
        text("""
            SELECT p.id
            FROM permissions p
            JOIN role_permissions rp ON p.id = rp.permission_id
            JOIN roles r ON rp.role_id = r.id
            WHERE r.name = :role
              AND p.resource_type = :resource
              AND p.action = :action
        """),
        {
            "role": user["role"],
            "resource": data.resource,
            "action": data.action
        }
    ).first()

    decision = "ALLOW" if permission else "DENY"

    db.execute(
        text("""
            INSERT INTO audit_logs (user_id, action, resource, decision, risk_score)
            VALUES (:user_id, :action, :resource, :decision, 0)
        """),
        {
            "user_id": user["id"],
            "action": data.action,
            "resource": data.resource,
            "decision": decision
        }
    )
    db.commit()

    return {
        "username": user["username"],
        "resource": data.resource,
        "action": data.action,
        "decision": decision
    }


@app.post("/risk/event")
def risk_event(data: RiskEventRequest, db: Session = Depends(get_db)):
    user = db.execute(
        text("SELECT id, username FROM users WHERE username = :username"),
        {"username": data.username}
    ).mappings().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    risk_values = {
        "low": 10,
        "medium": 30,
        "high": 55,
        "critical": 80
    }

    risk_score = risk_values.get(data.severity, 10)

    if risk_score < 25:
        risk_level = "low"
        response = "allow"
    elif risk_score < 50:
        risk_level = "medium"
        response = "step_up_mfa"
    elif risk_score < 75:
        risk_level = "high"
        response = "session_lock"
    else:
        risk_level = "critical"
        response = "session_terminate"

    db.execute(
        text("""
            INSERT INTO risk_events (user_id, event_type, resource, action, severity, risk_score)
            VALUES (:user_id, :event_type, :resource, :action, :severity, :risk_score)
        """),
        {
            "user_id": user["id"],
            "event_type": data.event_type,
            "resource": data.resource,
            "action": data.action,
            "severity": data.severity,
            "risk_score": risk_score
        }
    )

    db.execute(
        text("""
            INSERT INTO audit_logs (user_id, action, resource, decision, risk_score)
            VALUES (:user_id, :action, :resource, :decision, :risk_score)
        """),
        {
            "user_id": user["id"],
            "action": data.event_type,
            "resource": data.resource or "unknown",
            "decision": response,
            "risk_score": risk_score
        }
    )

    db.commit()

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "response": response
    }


@app.get("/audit/logs")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.execute(
        text("""
            SELECT 
                a.id,
                u.username,
                a.action,
                a.resource,
                a.decision,
                a.risk_score,
                a.created_at
            FROM audit_logs a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT 50
        """)
    ).mappings().all()

    return list(logs)