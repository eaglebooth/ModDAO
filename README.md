# ModDAO: Automated Community Moderator Payroll & AI Audit

ModDAO is a decentralized autonomous platform that tracks, evaluates, and distributes stablecoin payouts for Discord and Telegram community moderators fairly based on support quality scores parsed by GenLayer AI Juries.

## Problem Statement

Traditional moderator payment structures are often flawed:
* **Fixed Salary**: Fails to incentivize active and high-quality assistance, leading to lazy responses.
* **Per-Message Salary**: Easily gamed by spamming meaningless, repetitive, or unhelpful replies.
* **Qualitative Valuation**: Measuring real moderator helpfulness, patience, and competence is highly subjective and requires qualitative assessment.

## GenLayer Solution

ModDAO leverages GenLayer Intelligent Contracts to solve this:
1. **Support Log Scans**: The contract fetches public/private webhook URLs containing moderator chat histories.
2. **AI Jury Audit**: Independent LLM Validator nodes evaluate the chat logs on:
   - Politeness & attitude (0-30 points)
   - Problem-solving efficacy & accuracy (0-50 points)
   - Rule compliance & standard moderation (0-20 points)
3. **Decentralized Payroll**: The AI nodes reach a subjective consensus (`strict_eq`) on the Quality Score (0-100). The contract automatically computes the payout (`base_pay * score // 100`) and transfers the rewards securely from the treasury.

## Directory Structure

```
├── contracts/
│   └── ModDAO.py            # GenLayer Intelligent Contract
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css  # Premium Teal & Charcoal Dark Tech styles
│   │   │   ├── page.tsx     # Dynamic React dashboard UI
│   │   │   └── layout.tsx   
│   │   └── lib/
│   │       └── genlayer.ts  # Client wrapper connecting to studionet
│   └── public/scenarios/    # Preloaded mock evaluation logs
└── tests/
    └── test_contract_static.py
```

## Running Locally

1. Launch GenLayer Studio.
2. Compile and Deploy the contract `d:/Genlayer/ModDAO/contracts/ModDAO.py` on Studio to obtain the contract address.
3. Boot the Next.js dev server on port `3043`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. Open `http://localhost:3043`, connect your wallet, configure the contract address in the configuration bar, and run scenarios.
