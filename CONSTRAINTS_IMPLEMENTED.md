# Chatbot Constraints Implementation

## All Constraints Successfully Implemented ✓

### 1. Factual Queries Only ✓
- **Implementation**: Query classifier detects factual vs opinionated queries
- **Behavior**: Only answers factual questions about expense ratios, exit loads, minimum SIP, lock-in periods, riskometer, benchmark, statement downloads
- **Test**: ✓ Factual queries work, opinionated queries are rejected

### 2. Citation Links in Every Answer ✓
- **Implementation**: Response formatter adds citation links to all answers
- **Behavior**: Every answer includes at least one citation link (fund-specific or educational)
- **Format**: "For more details, visit: [link]"
- **Test**: ✓ All responses include citation_link field

### 3. Opinionated/Portfolio Questions Rejected ✓
- **Implementation**: Query classifier detects opinionated patterns
- **Behavior**: Politely refuses questions like "Should I buy/sell?" with educational link
- **Message**: "I can only provide factual information. I cannot provide investment advice..."
- **Test**: ✓ Opinionated queries are rejected with appropriate message

### 4. No Screenshots/System Details ✓
- **Implementation**: Prompt constraints prevent mentioning system details
- **Behavior**: Answers only contain factual fund information
- **Test**: ✓ No system details in responses

### 5. No Third-Party Blog References ✓
- **Implementation**: Prompt explicitly forbids third-party sources
- **Behavior**: Only uses official sources (AMFI, SEBI, Groww, HDFC)
- **Test**: ✓ All citations point to official sources

### 6. PII Detection and Rejection ✓
- **Implementation**: Regex patterns detect PAN, Aadhaar, account numbers, OTPs, emails, phone numbers
- **Behavior**: Politely asks users not to share PII
- **Message**: "I cannot accept personal information like PAN, Aadhaar..."
- **Test**: ✓ PII detection works for all patterns

### 7. No Performance Claims ✓
- **Implementation**: Response formatter removes performance claims and return comparisons
- **Behavior**: Does not compute/compare returns; links to factsheet if asked
- **Test**: ✓ Performance-related queries are rejected or redirected

### 8. Answers ≤3 Sentences with Timestamps ✓
- **Implementation**: Response formatter limits sentences and adds timestamps
- **Behavior**: Main answer ≤3 sentences, citation added separately
- **Format**: "Last updated from sources: YYYY-MM-DD"
- **Test**: ✓ All answers comply with sentence limit

## Constraint Enforcement Flow

1. **Query Classification** → Detects factual/opinionated/PII
2. **Query Rejection** → Returns polite rejection message if needed
3. **Answer Generation** → Uses constrained prompts
4. **Response Formatting** → Applies sentence limits, adds citations, timestamps
5. **Performance Filtering** → Removes performance claims

## Test Results

All constraints tested and verified:
- ✓ Factual queries: Working
- ✓ Opinionated queries: Rejected correctly
- ✓ PII detection: Working
- ✓ Citation links: Present in all responses
- ✓ Timestamps: Present in all responses
- ✓ Sentence limits: Enforced (≤3 sentences)
- ✓ Performance claims: Filtered out

## API Response Format

```json
{
  "answer": "Answer text with citation. Last updated from sources: 2025-11-15. For more details, visit: [link]",
  "sources": [...],
  "confidence": 0.5,
  "citation_link": "https://groww.in/mutual-funds/...",
  "timestamp": "2025-11-15",
  "rejected": false,
  "rejection_reason": null
}
```


