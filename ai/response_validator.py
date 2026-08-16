import re
from typing import Dict, Any, List

def validate_ai_response(response_text: str, verified_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates an AI response for numerical consistency and safety.
    
    Checks:
    - Hallucinations: Extracts numerical terms and compares large figures (balances, payments)
      against verified Python calculations.
    - Safety/Guarantees: Checks for unsupported assertions (like 'guarantee' debt removal).
    
    Returns a dict containing:
    - is_valid (bool)
    - sanitized_text (str)
    - warnings (list of str)
    """
    warnings = []
    sanitized_text = response_text
    
    # 1. Check for absolute guarantees or unrealistic claims
    guarantee_patterns = [
        (r"\bguarantee\w*\s+debt\s+elimination\b", "guarantees debt elimination"),
        (r"\bguarantee\w*\s+credit\s+score\b", "guarantees credit score improvement"),
        (r"\bwill\s+eliminate\s+all\s+your\s+debt\b", "unsupported claims of absolute debt clearance"),
        (r"\berase\s+your\s+credit\s+history\b", "erasure of credit records")
    ]
    
    for pattern, description in guarantee_patterns:
        if re.search(pattern, response_text, re.IGNORECASE):
            warnings.append(f"AI response contained a credit/debt guarantee rule trigger: '{description}'")
            
    # 2. Extract and check numerical claims
    # Extract all numbers from the text that look like currency values or large values (>100)
    numbers_in_text = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', response_text)
    
    # Standardize numbers in text to floats
    extracted_values = []
    for num_str in numbers_in_text:
        # Strip commas
        clean_str = num_str.replace(",", "")
        try:
            val = float(clean_str)
            # Only track larger values or non-integers that look like financial amounts
            if val > 100.0 or "." in num_str:
                extracted_values.append(val)
        except ValueError:
            continue
            
    # Gather verified numbers from the Python engine
    verified_values = []
    for k, v in verified_metrics.items():
        if isinstance(v, (int, float)):
            verified_values.append(round(float(v), 2))
            verified_values.append(round(float(v))) # check rounded integer as well
            
    # Look for discrepancy (numbers in text that are large and don't match any verified values)
    # We ignore standard formatting values like 12 (months), 24, 36, or ratios if they match
    hallucinated_values = []
    for val in extracted_values:
        # Allow standard rounding tolerances (+-1) or matching values
        matched = False
        for v in verified_values:
            if abs(val - v) <= 1.0 or (v > 0 and abs((val - v) / v) < 0.02):  # 2% rounding difference tolerance
                matched = True
                break
        
        # Additional safety list for common non-financial integers
        common_integers = [12.0, 24.0, 36.0, 48.0, 60.0, 100.0, 360.0, 30.0, 15.0, 20.0, 10.0, 5.0, 6.0, 3.0, 1.0, 2.0, 8.0, 0.0]
        if val in common_integers:
            matched = True
            
        if not matched:
            hallucinated_values.append(val)
            
    # If we found multiple large unverified values, warn the user
    if len(hallucinated_values) >= 2:
        warnings.append(
            f"Detected unverified financial numbers in AI response: {hallucinated_values}. "
            "Please cross-reference these with the official dashboard calculations."
        )
        
    # 3. Handle warning insertions
    if warnings:
        sanitized_text += (
            "\n\n---\n"
            "*⚠️ **Educational Disclaimer & Verification Warning:**\n"
            "This AI response contains estimates and general summaries. Some numbers above "
            "may be generic projections. Always refer to the verified mathematical calculations "
            "shown in the dashboard cards and graphs for final planning.*"
        )
        
    return {
        "is_valid": len(warnings) == 0,
        "sanitized_text": sanitized_text,
        "warnings": warnings
    }
