import math

# Shared Unicode Engineering Symbols
PI = "π"
MULT = "×"
DIV = "÷"
OHM = "Ω"
MICRO = "µ"
SQRT = "√"
DEG = "°"
SUP_2 = "²"
SUP_3 = "³"

# Superscript dictionary for arbitrary exponents
SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '-': '⁻', '+': '⁺', '.': '˙'
}

def to_superscript(text: str) -> str:
    """Converts a standard text string (like '-9') into Unicode superscript characters."""
    return "".join(SUPERSCRIPTS.get(c, c) for c in str(text))

def format_value_base(val: float, unit: str) -> str:
    """Formats a value for the substitution step.
    
    If the unit has a prefix (e.g. k, M, m, u, n, p), it formats the value
    as a product of the base number and 10^exponent in superscript.
    Example: 10 nF -> '10 × 10⁻⁹'
    """
    # Identify prefixes and their exponents
    # We parse unit strings like 'kΩ', 'nF', 'µH'
    if len(unit) > 1 and unit[0] in ['k', 'M', 'G', 'm', 'µ', 'μ', 'u', 'n', 'p']:
        prefix = unit[0]
        exp_map = {
            'k': 3, 'M': 6, 'G': 9,
            'm': -3, 'µ': -6, 'μ': -6, 'u': -6, 'n': -9, 'p': -12
        }
        exp = exp_map.get(prefix, 0)
        if exp != 0:
            # Check if val is an integer or close to it
            val_str = f"{val:g}"
            return f"{val_str} × 10{to_superscript(str(exp))}"
            
    return f"{val:g}"

def format_num(val: float, decimals: int = 2) -> str:
    """Formats a number with comma separators and specified decimal places."""
    try:
        if abs(val) < 1e-3 and val != 0:
            return f"{val:g}"
        # Standard decimal layout, stripping trailing zeros/dots
        formatted = f"{val:,.{decimals}f}"
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted
    except (ValueError, TypeError):
        return str(val)

def format_eng(value: float, unit: str = "") -> str:
    """Formats a numeric value using standard engineering prefix notation.
    
    Example: 15915.494309, 'Ω' -> '15.92 kΩ'
             0.000001, 'F' -> '1.00 µF'
    """
    if value == 0:
        return f"0.00 {unit}"
        
    abs_val = abs(value)
    # Find exponent as a multiple of 3
    exp = int(math.floor(math.log10(abs_val) / 3.0) * 3)
    # Clamp to common prefixes
    exp = max(-12, min(9, exp))
    
    prefix_map = {
        -12: "p", -9: "n", -6: "µ", -3: "m",
        0: "", 3: "k", 6: "M", 9: "G"
    }
    
    prefix = prefix_map.get(exp, "")
    mantissa = value / (10**exp)
    
    # Strip trailing zeroes/dot for neatness if it represents an exact integer
    formatted_mantissa = f"{mantissa:.2f}"
    
    # Add spacing between value and unit
    spaced_unit = f" {prefix}{unit}" if prefix or unit else ""
    return f"{formatted_mantissa}{spaced_unit}".strip()

def build_5_step_breakdown(
    formula: str,
    given_dict: dict,
    substitution: str,
    calculation: str,
    final_ans: str
) -> str:
    """Builds the standardized 5-step plain Unicode calculation breakdown.
    
    Applies colored Markdown headers for each step.
    """
    given_lines = []
    for k, v in given_dict.items():
        given_lines.append(f"- {k} = {v}")
    given_str = "\n".join(given_lines)
    
    return (
        f"<font color='#06b6d4'>**Step 1**</font>\n"
        f"**Formula**\n"
        f"  {formula}\n\n"
        f"<font color='#06b6d4'>**Step 2**</font>\n"
        f"**Given Values**\n"
        f"{given_str}\n\n"
        f"<font color='#06b6d4'>**Step 3**</font>\n"
        f"**Substitution**\n"
        f"  {substitution}\n\n"
        f"<font color='#06b6d4'>**Step 4**</font>\n"
        f"**Calculation**\n"
        f"  {calculation}\n\n"
        f"<font color='#06b6d4'>**Step 5**</font>\n"
        f"**Final Answer**\n"
        f"  {final_ans}"
    )
