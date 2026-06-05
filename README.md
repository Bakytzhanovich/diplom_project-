# Development of a Dynamic Access Control System Based on User Behavior Monitoring

This project is a fully functional prototype of a modern, context-aware **Dynamic Access Control System** built on **Zero Trust** and **UEBA (User and Entity Behavior Analytics)** principles. It continuously monitors user activities within a corporate portal session, calculates a real-time risk score based on 15 distinct behavioral factors, and dynamically restricts access permissions or terminates the session when suspicious activity is detected.

---

## 🚀 Key Features

### 1. User Behavior Monitoring (UEBA Engine)
The system monitors and evaluates user actions in real-time. It tracks **15 behavioral risk factors**:
*   **Network Anomalies**: IP address change (`ipChange`), impossible travel/geographical jumps (`geoJump`).
*   **Temporal Anomalies**: Access during off-business hours (`offHours`).
*   **Data Exfiltration Markers**: Mass download (`massDownload`), high data volume anomaly (`dataVolume`), clipboard exfiltration (`clipboard`).
*   **Lateral Movement**: Attempts to access unauthorized department portals (`failedAccess`, `crossDept`, `lateralMove`).
*   **System Integrity**: Uploading dangerous file extensions/scripts (`scriptExec`, `massUpload`).
*   **Anomalous Interaction**: Excessive action velocity indicating automated bots (`highVelocity`).

### 2. Dynamic Access Control & Response Policies
Unlike traditional static Role-Based Access Control (RBAC), this system adapts permissions on-the-fly:
*   🟢 **Full Access (Safe | Risk < 25)**: Normal user experience.
*   🟡 **Caution (Risk 25-50)**: Minor UI warnings, increased logging.
*   🟠 **Restricted / Read-Only (Risk 50-75)**: **Dynamic Quarantine.** The user can view data but is blocked from downloading files, sending emails, posting chat messages, or editing notes. Requires **Step-up Multi-Factor Authentication (MFA)** to restore access.
*   🔴 **Session Lock (Risk 75-80)**: Screen is locked; re-authentication with password is required.
*   🚫 **Session Terminated (Critical | Risk > 80)**: The user session is immediately destroyed, and an incident report is logged on the backend.

### 3. Corporate Portal Emulation
A sleek, modern dark-themed enterprise dashboard containing fully functional modules:
*   **Chat Module** (Channels & Direct Messages)
*   **Email Client** (Inbox, Outbox, Compose)
*   **Calendar & Events**
*   **File Explorer** (With simulated VirusTotal file security verification)
*   **Notes App**

### 4. Security Operations Center (SOC) Admin Dashboard
Accessible via the **🛡 Admin** button in the header (Password: `admin`). Features:
*   Real-time session risk speedometer (0-100 scale).
*   Live threat level graph.
*   Granular charts displaying active risk factor weights.
*   Real-time system audit logs streamed directly from the FastAPI backend.

---

## 🛠 Tech Stack

*   **Backend**: Python, FastAPI, SQLAlchemy (SQLite database engine), Uvicorn.
*   **Frontend**: Vanilla HTML5, CSS3, Modern ES6+ JavaScript.
*   **Database**: SQLite (`access_control.db`), pre-seeded with roles, permissions, users, and logs.

---

## 📁 Repository Structure

```
├── backend/
│   ├── main.py            # Main FastAPI server with security endpoints
│   ├── database.py        # SQLite SQLAlchemy configuration
│   └── (empty helper files for future structural modularization)
├── frontend/
│   ├── dynamofinal_backend_connected.html  # Main frontend integrated with backend
│   └── dynamofinal.html                    # Offline/standalone prototype frontend
├── schema.sql             # SQL database structure
├── seed.sql               # Seed data (pre-configured users, roles, permissions)
├── requirements.txt       # Python package dependencies
├── Dockerfile             # Container configuration
└── docker-compose.yml     # Multi-container orchestration (Postgres, Redis, Backend)
```

---

## 📥 Installation & Running Instructions

### Prerequisites
*   Python 3.10 or higher
*   A modern web browser

### Local Launch (Recommended)

1.  **Clone / open the project directory**:
    ```bash
    cd /path/to/project
    ```

2.  **Create and activate a virtual environment**:
    *   **macOS / Linux**:
        ```bash
        python3 -m venv venv_mac
        source venv_mac/bin/activate
        ```
    *   **Windows**:
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start the Backend server**:
    ```bash
    uvicorn backend.main:app --host 127.0.0.1 --port 8000
    ```
    *Note: On first run, the system automatically initializes `access_control.db` using the schema and seed scripts.*
    *   API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

5.  **Serve the Frontend**:
    Run a local server in the project folder to prevent CORS/browser-security issues:
    ```bash
    # Run a simple python web server on port 8080
    python3 -m http.server 8080
    ```
    Now, open your browser and navigate to:
    👉 [http://localhost:8080/frontend/dynamofinal_backend_connected.html](http://localhost:8080/frontend/dynamofinal_backend_connected.html)

---

## 🧪 Testing Scenarios (For Presentation / Defense)

### Test Accounts (Credentials)
*   **Employee (Default)**: Username: `aiman.sholpan` | Password: `user123`
*   **Manager**: Username: `manager` | Password: `manager123`
*   **Admin**: Username: `admin` | Password: `admin123`
*   **Founder (Admin)**: Username: `nurs` | Password: `nurs2004`


### Step-by-Step Security Demo
1.  **Login** as `aiman.sholpan` on the portal.
2.  Open the SOC dashboard by clicking **🛡 Admin** in the header (Enter password: `admin`). Position the admin panel side-by-side or on a split screen.
3.  **Simulate an Insider Threat / Attack**:
    *   Navigate to **Files** and click **Download all** or attempt to upload multiple unchecked files.
    *   Attempt to access restricted departments from the sidebar (e.g., click **IT Systems** or **Finance**).
4.  **Observe the Dynamic Reaction**:
    *   The SOC risk score will instantly spike on the charts.
    *   The user's portal will transition into **Read-only restricted mode**, blocking any write actions (chat messages, mail delivery, file downloads).
5.  **Self-healing (MFA Bypass)**:
    *   Click on the restricted banner or perform an action to trigger Step-Up MFA.
    *   Enter the 2FA code simulated on the phone UI to verify identity.
    *   Watch the risk score decrease back to **Safe (Green)** and write permissions instantly restore!
