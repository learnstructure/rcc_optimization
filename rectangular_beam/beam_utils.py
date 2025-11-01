def validate_design(b, d, Ast, fck, fy):
    """
    Optional IS 456 validation function.
    Could be extended for reinforcement limits, deflection, etc.
    """
    if b < 200 or d < 300:
        return False, "Section too small"
    if Ast <= 0:
        return False, "Invalid reinforcement area"
    return True, "Design OK"
