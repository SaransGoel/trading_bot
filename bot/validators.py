class InputValidationError(Exception):
    pass

def validate_symbol(symbol: str) -> str:
    if not symbol: raise InputValidationError("Symbol cannot be empty.")
    cleaned = symbol.strip().upper()
    if not cleaned.isalnum(): raise InputValidationError("Invalid symbol format.")
    return cleaned

def validate_side(side: str) -> str:
    cleaned = side.strip().upper()
    if cleaned not in ['BUY', 'SELL']: raise InputValidationError("Must be BUY or SELL.")
    return cleaned

def validate_order_type(order_type: str) -> str:
    cleaned = order_type.strip().upper()
    if cleaned not in ['MARKET', 'LIMIT', 'STOP_MARKET']:
        raise InputValidationError("Must be MARKET, LIMIT, or STOP_MARKET.")
    return cleaned

def validate_quantity(quantity: float) -> float:
    try:
        qty = float(quantity)
        if qty <= 0: raise ValueError
        return qty
    except: raise InputValidationError("Quantity must be greater than 0.")

def validate_price(price: float, field_name="Price") -> float:
    try:
        val_price = float(price)
        if val_price <= 0: raise ValueError
        return val_price
    except: raise InputValidationError(f"A valid positive {field_name} is REQUIRED.")