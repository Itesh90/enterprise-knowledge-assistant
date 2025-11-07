# Safety and Guardrails

Assistants should decline to answer if context is insufficient and avoid speculation.
Provide citations and indicate uncertainty when needed.

## Guardrails in EKA

1. **Similarity Threshold**: Retrieved chunks must meet a minimum similarity score
   - Default threshold: 0.30 (configurable via `CITATION_SIM_THRESHOLD`)
   - Low similarity triggers "I'm not sure" response

2. **Safety Classifier**: Simple heuristic-based classifier for unsafe queries
   - Detects off-topic or harmful content
   - Returns early rejection for unsafe queries

3. **Confidence Scoring**: Based on average similarity of top retrieved chunks
   - Low confidence (< 0.4): Red badge, disclaimer
   - Medium confidence (0.4-0.7): Yellow badge
   - High confidence (> 0.7): Green badge

4. **Citation Coverage**: Ensure sufficient context coverage
   - Check that retrieved chunks provide adequate coverage
   - Fallback to "I'm not sure" if coverage is insufficient

## Best Practices

- Always provide citations when available
- Clearly indicate uncertainty
- Avoid speculation beyond available context
- Use confidence scores to guide user expectations

