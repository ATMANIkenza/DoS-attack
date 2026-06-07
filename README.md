# DoS Attack Simulation — CPU Exhaustion via Bcrypt Hashing

> **Warning:** This project is a controlled simulation for personal learning about application-layer DoS vulnerabilities. Never use against systems you don't own.

## Overview

A personal challenge to understand and simulate a **CPU-exhaustion Denial of Service (DoS)** attack targeting web applications that use expensive hashing algorithms (like `bcrypt`) for password authentication.

The simulation consists of two components:
- A **vulnerable Flask server** (`victim_server.py`) that performs a costly `bcrypt.checkpw()` on every login attempt
- An **attack script** (`dos_hashing_attack.py`) that floods the server with concurrent login requests, saturating its CPU

## How It Works

```
Attacker (100 threads)                  Victim Server
       │                                      │
       │──── POST /login (random creds) ────► │
       │──── POST /login (random creds) ────► │  bcrypt.checkpw() ← CPU-intensive!
       │──── POST /login (random creds) ────► │
       │           x 20,000 requests          │
                                              ↓
                                     CPU saturated → legitimate
                                     users can't log in
```

**Why bcrypt?** bcrypt is intentionally slow (cost factor 12 = ~2^12 iterations). While this is great for security against brute-force, it becomes a weapon in a DoS attack since each request forces the server to spend significant CPU time.

## Project Structure

```
DoS-attack/
├── victim_server.py        # Vulnerable Flask login server (port 8000)
├── dos_hashing_attack.py   # Multi-threaded DoS attack simulator
└── README.md
```

## Setup & Usage

### Prerequisites

```bash
pip install flask bcrypt requests
```

### Step 1 — Start the victim server

```bash
python victim_server.py
```

The server starts on `http://127.0.0.1:8000`. Navigate to `/` to see the login form.

### Step 2 — Run the attack simulation

```bash
python dos_hashing_attack.py
```

### Step 3 — Observe the impact

Watch the server's CPU usage spike as the attack floods the login endpoint. Legitimate requests will time out or receive very slow responses.

## Configuration

In `dos_hashing_attack.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TARGET_URL` | `http://127.0.0.1:8000/login` | Target endpoint |
| `NUM_THREADS` | `100` | Number of concurrent "attackers" |
| `REQUESTS_PER_THREAD` | `200` | Requests sent per thread |
| `DELAY_PER_REQUEST` | `0.001s` | Delay between requests per thread |

> Total simulated login attempts = `NUM_THREADS × REQUESTS_PER_THREAD` = **20,000 requests**

## Countermeasures

| Defense | How it helps |
|--------|--------------|
| **Rate limiting** (e.g., Flask-Limiter) | Limits requests per IP/user |
| **CAPTCHA** | Blocks automated scripts |
| **IP-based blocking** | Detects and bans flooding IPs |
| **Request queuing** | Throttles bcrypt calls per unit time |
| **Async hashing** | Offloads bcrypt to a worker queue (e.g., Celery) |
| **Account lockout** | Temporarily disables accounts after N failures |

## Sample Output

```
--- Simulation d'Attaque DoS : Saturation CPU par Hachage ---
Cible : http://127.0.0.1:8000/login
Nombre de threads : 100
Requêtes par thread : 200
Total des tentatives : 20000

Progression totale : 4823 tentatives | Succès HTTP: 4721 | Échecs: 102 | Temps: 12.45s

--- Résultats de la Simulation ---
Total des tentatives effectuées : 20000
Réponses HTTP réussies : 19453
Requêtes échouées (timeouts/erreurs) : 547
Temps total : 87.32 secondes
Tentatives par seconde (APS) : 229.04
```

## Legal & Ethical Notice

This code is strictly for personal research and learning in controlled, local environments. Running this against any system without explicit written authorization is **illegal** and unethical.

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![bcrypt](https://img.shields.io/badge/bcrypt-hashing-green)
![Threading](https://img.shields.io/badge/threading-multithreaded-orange)