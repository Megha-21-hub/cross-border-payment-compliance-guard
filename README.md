\# Cross-Border Payment Compliance Guard



A prototype for checking international payment configurations before a merchant processes a payment.



\## What this project does



The idea behind this project is simple: a merchant should be able to check a payment configuration before accepting an international payment and see if anything important is missing.



The application takes transaction details such as currency, amount, customer country and payment method, and checks additional configuration details using a rule-based compliance engine.



If something is missing, the system creates a finding with a risk level and a suggested action.



An AI explanation layer is also included to explain the finding in simpler language.



\## Why I built it



International payments can involve additional information and documentation compared with a normal domestic payment.



For example, a merchant may need to keep track of things such as:



\- Purpose code

\- IEC information

\- HS classification

\- Invoice reference

\- Supporting documentation



Instead of discovering missing information later, this project tries to provide an early warning during payment configuration.



\## How it works



```text

Payment Configuration

&#x20;       ↓

Compliance Rule Engine

&#x20;       ↓

Risk Detection

&#x20;       ↓

Risk Level + Findings

&#x20;       ↓

AI Explanation

&#x20;       ↓

Recommended Action


## Screenshots

### Login

![Login Page](Screenshots/login.png)

### Dashboard

![Dashboard](Screenshots/dashboard.png)

### Payment Scanner

![Payment Scanner](Screenshots/scanner-empty.png)

### Audit Trail

![Audit Trail](Screenshots/audit-trail.png)

