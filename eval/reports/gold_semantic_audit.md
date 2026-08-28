# Gold-Set Semantic Audit Report

**Date:** 2026-08-28

---

## Purpose

This audit verifies that each gold chunk actually contains answer-bearing evidence for its question.
This is NOT an embedding-similarity check — it's a semantic relevance verification.

**Important:** Don't require every individual gold chunk to independently answer the whole question.
Some questions legitimately require multiple chunks. The criterion is whether the chunk provides
meaningful evidence, and whether the **set of gold chunks collectively supports the answer**.

---

## Summary

| Metric | Value |
|--------|-------|
| Total gold cases | 245 |
| Answerable cases | 40 |
| Total gold chunks | 120 |
| Chunks needing verification | 120 |

**Status:** PENDING MANUAL VERIFICATION

---

## Manual Verification Instructions

For each case below, verify:

1. Read the question.
2. Read every assigned `relevant_chunk_id`.
3. Inspect the actual chunk content.
4. Mark each chunk:
   - **YES** = directly contains answer-bearing evidence
   - **PARTIAL** = supports an essential part but is insufficient alone
   - **NO** = merely belongs to the correct document/domain
5. For each case, ensure the remaining gold chunks collectively contain enough evidence to answer the question.
6. Replace/remove incorrect gold chunks using semantic judgment, NOT embedding similarity.
7. Record the reason for every change.

---

## Case 1: What are the byelaws for a cooperative society?

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 2: Voting rights in a cooperative society

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 3: Quorum requirements for cooperative society meetings

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 4: How to become a member of a cooperative society?

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 5: Share transfer rules in cooperative society

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 6: Election process for cooperative society committee

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 7: Restrictions on cooperative society borrowing

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 8: Managing committee powers under cooperative act

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 9: Surplus distribution in cooperative society

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 10: Member expulsion from cooperative society

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 11: Cooperative society bylaw amendment process

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 12: Dividend declaration rules for cooperative

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 13: Cooperative society special resolution requirements

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 14: Election of the PACS managing committee

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 15: PACS meeting frequency requirements

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 16: PACS bylaw amendment procedure

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 17: PACS annual general meeting rules

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 18: What risks does PMFBY cover for standing crops?

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 19: PMFBY premium rates for food crops

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 20: Who is eligible for PMFBY coverage?

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 21: PMFBY enrollment deadline for kharif crops

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 22: Gujarat PMFBY crop insurance portal

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 23: PMFBY coverage for horticultural crops

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 24: PMFBY preventive sowing provision

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 25: PMFBY add-on coverage options

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 26: PMFBY use of technology for crop cutting experiments

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 27: PMFBY premium subsidy by state government

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 28: Gujarat PMFBY farmer enrollment drive

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 29: PMFBY coverage for perennial crops

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 30: PMFBY insurance company empanelment

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 31: PMFBY coverage area definition

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 32: PMFBY private crop insurance companies list

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 33: PMFBY restructured weather-based scheme

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 34: Gujarat PMFBY district-wise premium rates

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 35: PMFBY indemnity level calculation

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 36: PMFBY exclusion period for prevented sowing

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 37: PMFBY claim amount based on yield estimation

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 38: PMFBY notification date for each season

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 39: Cooperative society deposit insurance coverage

- **Domain:** pacs_governance
- **Expected sources:** ['pacs_model_bylaws_2023']
- **Gold chunks:** 3

### Chunk 1: `9b4953ef-8e2...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 380 chars

**Content preview:**

> No. R-11016/10/2022-I&P Government of India Ministry of Cooperation CTP/IT Division   Atal Akshay Urja Bhawan, CGO Complex Lodhi Road, New Delhi-110003.   Date: 5 January, 2023   To   The Additional Chief Secretary/ Principal Secretary/ Secretary Cooperation of all the States and Union Territories. ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `1e63b1fc-112...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3930 chars

**Content preview:**

> ## Dear Madan/Sir,   As you would be aware there are nearly 95,000 Primary Agriculture Credit Societies (PACS) in the country, with a member base of around 13 crores. PACS serve as a crucial link in sustaining the rural economy of the country by providing short-term and medium-term credit to farmers...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `8f055eab-cbe...`

- **Status:** EXISTS
- **Source:** pacs_model_bylaws_2023
- **Page:** 0
- **Content length:** 3847 chars

**Content preview:**

> ## **4. DEFINITIONS:** - (1) **"Act"** means the Cooperative Societies Act under which the Society is registered; - (2) **“Agriculture”** means agriculture and allied activities; - (3) **"Area of operation"** means the geographical area (Revenue village (s)/ Panchayat (s)) from which the Society is ...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---

## Case 40: PMFBY premium subsidy through PACS

- **Domain:** pmfby
- **Expected sources:** ['pmfby_operational_guidelines']
- **Gold chunks:** 3

### Chunk 1: `e2c84858-d56...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 2299 chars

**Content preview:**

> ###### **II. Surplus Sharing:**   - a. GoI will not share surplus (if any) with State/UT Government if the claim ratio is less than 80%   - b. Surplus sharing between Insurance Company and State/UT Government will be done at cluster & season level or at the level of determination of L1 bidder & seas...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 2: `eaceebf6-763...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 5673 chars

**Content preview:**

> ##### **5.8 Sandbox for Agricultural & Rural Security, Technology & Insurance Platform (SARTHI) & Product Innovation**   - **5.8.1** With a view to enhance the access to agriculture & allied insurance products for farmers and to increase penetration of insurance adoption in the Agri ecosystem, GoI i...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

### Chunk 3: `2b187ae2-628...`

- **Status:** EXISTS
- **Source:** pmfby_operational_guidelines
- **Page:** 0
- **Content length:** 4097 chars

**Content preview:**

> ##### **6.1 State/UTs** Issuance of Notification by the State Governments/UT Administrations for the implementation of the Scheme shall imply their acceptance of all the provisions, modalities and Operational Guidelines of the Scheme. **The main conditions relating to the scheme which are binding on...

**Contains answer-bearing evidence?** [ ] YES / [ ] PARTIAL / [ ] NO

---
