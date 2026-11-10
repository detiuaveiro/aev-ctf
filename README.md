# AEV CTF

Capture-the-flag challenges for students of the **AEV** course. Each challenge is a small, self-contained, deliberately vulnerable service (or binary) that you attack to recover a flag.

There are **57 challenges** in 7 categories. Challenge names are intentionally neutral (e.g. `auth7`, `leak5`) so that they don't give away the vulnerability class — figuring that out is part of the exercise.

## Repository layout

```
<category>/<challenge>/
├── README.md          # challenge notes and lab address
├── challenge.yml      # name, category, description (a hint in verse), points
├── Dockerfile
├── docker-compose.yml
├── app/ (or src/)     # challenge source
└── solution/          # reference solution (staff only)
```

Challenges are deployed in the lab with `./deploy.sh container up <category>/<challenge> flag_file=<path>`. For local testing, run `docker compose up --build` inside a challenge directory. Flags are per student.

## Challenges

Each challenge lists the CWE(s) of its intended weakness (taken from its `challenge.yml`).

### auth — Authentication and session handling (14)

| Challenge | Difficulty | Points | CWE |
|---|---|---|---|
| auth1 | easy | 100 | [CWE-1392](https://cwe.mitre.org/data/definitions/1392.html), [CWE-521](https://cwe.mitre.org/data/definitions/521.html) |
| auth2 | easy | 100 | [CWE-293](https://cwe.mitre.org/data/definitions/293.html) |
| auth3 | easy | 100 | [CWE-598](https://cwe.mitre.org/data/definitions/598.html) |
| auth4 | easy | 100 | [CWE-602](https://cwe.mitre.org/data/definitions/602.html) |
| auth5 | medium | 150 | [CWE-384](https://cwe.mitre.org/data/definitions/384.html) |
| auth6 | medium | 150 | [CWE-384](https://cwe.mitre.org/data/definitions/384.html) |
| auth7 | medium | 150 | [CWE-347](https://cwe.mitre.org/data/definitions/347.html) |
| auth8 | medium | 150 | [CWE-327](https://cwe.mitre.org/data/definitions/327.html) |
| auth9 | medium | 150 | [CWE-330](https://cwe.mitre.org/data/definitions/330.html), [CWE-331](https://cwe.mitre.org/data/definitions/331.html) |
| auth10 | easy | 100 | [CWE-204](https://cwe.mitre.org/data/definitions/204.html) |
| auth11 | medium | 150 | [CWE-330](https://cwe.mitre.org/data/definitions/330.html), [CWE-640](https://cwe.mitre.org/data/definitions/640.html) |
| auth12 | easy | 100 | [CWE-257](https://cwe.mitre.org/data/definitions/257.html), [CWE-522](https://cwe.mitre.org/data/definitions/522.html) |
| auth13 | medium | 150 | [CWE-307](https://cwe.mitre.org/data/definitions/307.html) |
| auth14 | easy | 100 | [CWE-613](https://cwe.mitre.org/data/definitions/613.html) |

### infoleak — Information disclosure (10)

| Challenge | Difficulty | Points | CWE |
|---|---|---|---|
| leak1 | medium | 150 | [CWE-445](https://cwe.mitre.org/data/definitions/445.html) |
| leak2 | medium | 150 | [CWE-489](https://cwe.mitre.org/data/definitions/489.html) |
| leak3 | easy | 100 | [CWE-548](https://cwe.mitre.org/data/definitions/548.html) |
| leak4 | medium | 200 | [CWE-538](https://cwe.mitre.org/data/definitions/538.html) |
| leak5 | hard | 250 | [CWE-639](https://cwe.mitre.org/data/definitions/639.html) |
| leak6 | medium | 200 | [CWE-200](https://cwe.mitre.org/data/definitions/200.html) |
| leak7 | hard | 300 | [CWE-200](https://cwe.mitre.org/data/definitions/200.html) |
| leak8 | easy | 100 | [CWE-200](https://cwe.mitre.org/data/definitions/200.html) |
| leak9 | introductory | 50 | [CWE-200](https://cwe.mitre.org/data/definitions/200.html) |
| leak10 | introductory | 75 | [CWE-209](https://cwe.mitre.org/data/definitions/209.html) |

### inj — Injection (14)

| Challenge | Difficulty | Points | CWE |
|---|---|---|---|
| inj1 | easy | 100 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj2 | easy | 100 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj3 | medium | 150 | [CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| inj4 | medium | 150 | [CWE-611](https://cwe.mitre.org/data/definitions/611.html) |
| inj5 | medium | 150 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj6 | hard | 200 | [CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| inj7 | medium | 150 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj8 | hard | 200 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj9 | hard | 200 | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) |
| inj10 | hard | 250 | [CWE-426](https://cwe.mitre.org/data/definitions/426.html) |
| inj11 | hard | 200 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj12 | hard | 250 | [CWE-94](https://cwe.mitre.org/data/definitions/94.html) |
| inj13 | hard | 250 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |
| inj14 | hard | 200 | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) |

### sqli — SQL injection (8)

| Challenge | Description | Difficulty | Points | CWE |
|---|---|---|---|---|
| sqli1 | Staff Portal | - | 100 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli2 | TechBazaar Search | - | 200 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli3 | PhotoVault | - | 200 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli4 | DropLite | - | 300 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli5 | The Daily Byte | - | 300 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli6 | Guestbook | - | 400 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli7 | Linkly | - | 500 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |
| sqli8 | TransferOps Console | - | 500 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) |

### web — Web application security (9)

| Challenge | Description | Difficulty | Points | CWE |
|---|---|---|---|---|
| bwapp | bWAPP (buggy Web APPlication) | intro→intermediate | 100 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html), [CWE-79](https://cwe.mitre.org/data/definitions/79.html), [CWE-287](https://cwe.mitre.org/data/definitions/287.html) (plus many more, per exercise) |
| dvwa | Damn Vulnerable Web Application | intro→intermediate | 100 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html), [CWE-79](https://cwe.mitre.org/data/definitions/79.html), [CWE-287](https://cwe.mitre.org/data/definitions/287.html) (plus many more, per exercise) |
| juiceshop | OWASP Juice Shop | intro→intermediate | 100 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html), [CWE-79](https://cwe.mitre.org/data/definitions/79.html), [CWE-287](https://cwe.mitre.org/data/definitions/287.html) (plus many more, per exercise) |
| mutillidae | OWASP Mutillidae | intro→intermediate | 100 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html), [CWE-79](https://cwe.mitre.org/data/definitions/79.html), [CWE-287](https://cwe.mitre.org/data/definitions/287.html) (plus many more, per exercise) |
| notes1 | Notes app, intro level | intro | 100 | [CWE-639](https://cwe.mitre.org/data/definitions/639.html) |
| wordpress | Outdated WordPress blog | advanced | 100 | [CWE-1104](https://cwe.mitre.org/data/definitions/1104.html) |
| xss1 | Reflected XSS | - | 100 | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| xss2 | Stored XSS | - | 150 | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |
| xss3 | DOM-based XSS | - | 200 | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) |

For `bwapp`, `dvwa`, `juiceshop` and `mutillidae`, work through the application until you find where your per-student flag lives.

### network (1)

| Challenge | Description | Difficulty | Points | CWE |
|---|---|---|---|---|
| snmp1 | Exposed SNMP service | introductory | 100 | [CWE-1392](https://cwe.mitre.org/data/definitions/1392.html) |

### pwn (1)

| Challenge | Description | Difficulty | Points | CWE |
|---|---|---|---|---|
| pwn1 | Introductory binary exploitation | intro | 100 | [CWE-121](https://cwe.mitre.org/data/definitions/121.html) |

