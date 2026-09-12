# Digital Personal Data Protection (DPDP) Act & Customer KYC Privacy Norms

## Section 1: Data Minimization and Consent Principles
**Source Citation:** [Source: DPDP Act 2023 & UIDAI Circular, Sec 1.1]
1. **Purpose Limitation:** Customer data collected by the bank must be strictly confined to the explicit purpose specified at collection (credit evaluation and loan disbursal).
2. **Data Minimization:** Banks shall not collect more personal information than necessary to complete the regulatory transaction.

## Section 2: Why We Collect PAN and Aadhaar Last 4 Digits
**Source Citation:** [Source: RBI Master Direction - KYC & UIDAI Compliance, Sec 2.2]
1. **Permanent Account Number (PAN):** Under Section 139A of the Income Tax Act and RBI KYC directions, PAN verification is mandatory for credit evaluation and credit bureau inquiries (CIBIL/Experian/Equifax/CRIF).
2. **Aadhaar Masking and Last-4 Digit Rule:** To protect customer privacy under the DPDP Act 2023 and UIDAI regulations:
   - Full 12-digit Aadhaar numbers must **never** be requested, displayed, or stored in plaintext on non-UIDAI servers.
   - Only the **last 4 digits** of Aadhaar are collected to verify identity matching against previously completed offline or video KYC records.
   - The last 4 digits are validated using the **Verhoeff Checksum Algorithm** to detect typographical errors instantly.

## Section 3: Customer Rights Under DPDP Act 2023
**Source Citation:** [Source: DPDP Act 2023 — Customer Rights, Sec 3.4]
1. **Right to Information and Summary:** Borrowers have the legal right to request a summary of personal data being processed and the identities of all entities with whom data has been shared.
2. **Right to Correction and Erasure:** Customers can request correction of inaccurate financial data and request deletion/erasure of data once the statutory loan relationship and retention obligations are concluded.
3. **Right to Grievance Redressal:** If consent is violated, customers have access to the bank's Data Protection Officer (DPO) and subsequent appeal to the Data Protection Board of India (DPBI).
