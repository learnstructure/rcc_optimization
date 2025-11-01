import numpy as np
import math


# === Helper Functions ===
def get_xul(d, fy):
    Es = 2e5
    return round(0.0035 * d / (0.0055 + 0.87 * fy / Es), 2)


def calculate_moment_capacity(b, d, Ast, fck, fy):
    xu = (0.87 * fy * Ast) / (0.36 * fck * b)
    MOR = 0.87 * fy * Ast * (d - 0.416 * xu) / 1e6
    xul = get_xul(d, fy)
    Mul = 0.36 * fck * b * xul * (d - 0.416 * xul) / 1e6
    return round(MOR, 3), round(Mul, 3)


def Ast_limits(b, d, fy):
    Ast_min = 0.85 * b * d / fy
    Ast_max = 0.04 * b * d
    return round(Ast_min, 2), round(Ast_max, 2)


def bd_ratio(b, d):
    return b / d


def get_cost(b, d, Ast):
    concrete_vol = (b * d) * 1e-6  # m³/m
    steel_wt = Ast * 1e-6 * 7850  # kg/m
    return round(concrete_vol * 15000 + steel_wt * 140, 2)


def is_valid_design(b, d, Ast, fck, fy, Mu):
    Ast_min, Ast_max = Ast_limits(b, d, fy)
    if not (Ast_min <= Ast <= Ast_max):
        return False
    if bd_ratio(b, d) < 0.3:
        return False
    MOR, Mul = calculate_moment_capacity(b, d, Ast, fck, fy)
    return not (Mu > MOR or MOR > Mul)
