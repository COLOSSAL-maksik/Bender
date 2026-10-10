from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction

import pytest

# Sign conventions:
# x-axis is positive to the right.
# Forces are positive to the right.
# Displacements are positive to the right.
# Internal force N is positive in tension (causes elongation).
# Normal stress sigma is positive in tension.
# Strain epsilon is positive for elongation.


@dataclass
class PointLoad:
    x: Fraction
    value: Fraction


@dataclass
class Support:
    x: Fraction
    fixed_displacement: Fraction


@dataclass
class Section:
    x_start: Fraction
    x_end: Fraction
    E: Fraction
    A: Fraction
    q: Fraction  # Uniform distributed load, positive to the right
    alpha: Fraction = Fraction(0)
    delta_T: Fraction = Fraction(0)


@dataclass
class SectionSolution:
    x_start: Fraction
    x_end: Fraction
    N: Callable[[Fraction], Fraction]
    sigma: Callable[[Fraction], Fraction]
    eps_mech: Callable[[Fraction], Fraction]
    eps_full: Callable[[Fraction], Fraction]
    u: Callable[[Fraction], Fraction]


@dataclass
class ExactSolution:
    reactions: dict[Fraction, Fraction]  # key: x, value: reaction force (positive to the right)
    sections: list[SectionSolution]


@dataclass
class Axial1DBenchmark:
    name: str
    length: Fraction
    sections: list[Section]
    point_loads: list[PointLoad]
    supports: list[Support]
    solution: ExactSolution


def create_case_1() -> Axial1DBenchmark:
    # 1. Bar with constant EA, fixed at x=0, axial force F at x=L.
    # L = 10, E = 200, A = 5, F = 100 at x=10
    # Reactions: R_0 = -100
    # N(x) = 100
    # sigma = 100 / 5 = 20
    # eps = 20 / 200 = 1/10
    # u(x) = x/10
    L = Fraction(10)
    E = Fraction(200)
    A = Fraction(5)
    F = Fraction(100)

    sec = Section(Fraction(0), L, E, A, Fraction(0))
    sol_sec = SectionSolution(
        Fraction(0),
        L,
        N=lambda x: Fraction(100),
        sigma=lambda x: Fraction(20),
        eps_mech=lambda x: Fraction(1, 10),
        eps_full=lambda x: Fraction(1, 10),
        u=lambda x: x / Fraction(10),
    )

    return Axial1DBenchmark(
        name="Case 1: Constant EA, fixed at one end, force at the other",
        length=L,
        sections=[sec],
        point_loads=[PointLoad(L, F)],
        supports=[Support(Fraction(0), Fraction(0))],
        solution=ExactSolution(reactions={Fraction(0): Fraction(-100)}, sections=[sol_sec]),
    )


def create_case_2() -> Axial1DBenchmark:
    # 2. Stepped bar, E1/A1 and E2/A2, multiple forces.
    # Fixed at x=0.
    # Sec 1: x in [0, 5], E=100, A=10
    # Sec 2: x in [5, 10], E=200, A=5
    # Force 1: F1 = 50 at x=5
    # Force 2: F2 = -20 at x=10
    # R_0 = - (F1 + F2) = -30
    #
    # N(x) for x in (0, 5): R_0 + N = 0 -> N = -R_0 = 30. Wait.
    # Sum of forces to the right of section:
    # x in (5, 10): N = F2 = -20
    # x in (0, 5): N = F1 + F2 = 50 - 20 = 30
    #
    # Sec 1 (0 to 5):
    # N = 30
    # sigma = 30/10 = 3
    # eps = 3/100
    # u(x) = u(0) + (3/100)*x = (3/100)*x. u(5) = 15/100 = 3/20
    #
    # Sec 2 (5 to 10):
    # N = -20
    # sigma = -20/5 = -4
    # eps = -4/200 = -1/50
    # u(x) = u(5) + eps * (x - 5) = 3/20 - 1/50 * (x - 5) = 15/100 - 2/100 * (x - 5)

    return Axial1DBenchmark(
        name="Case 2: Stepped bar with multiple concentrated forces",
        length=Fraction(10),
        sections=[
            Section(Fraction(0), Fraction(5), Fraction(100), Fraction(10), Fraction(0)),
            Section(Fraction(5), Fraction(10), Fraction(200), Fraction(5), Fraction(0)),
        ],
        point_loads=[PointLoad(Fraction(5), Fraction(50)), PointLoad(Fraction(10), Fraction(-20))],
        supports=[Support(Fraction(0), Fraction(0))],
        solution=ExactSolution(
            reactions={Fraction(0): Fraction(-30)},
            sections=[
                SectionSolution(
                    Fraction(0),
                    Fraction(5),
                    N=lambda x: Fraction(30),
                    sigma=lambda x: Fraction(3),
                    eps_mech=lambda x: Fraction(3, 100),
                    eps_full=lambda x: Fraction(3, 100),
                    u=lambda x: x * Fraction(3, 100),
                ),
                SectionSolution(
                    Fraction(5),
                    Fraction(10),
                    N=lambda x: Fraction(-20),
                    sigma=lambda x: Fraction(-4),
                    eps_mech=lambda x: Fraction(-1, 50),
                    eps_full=lambda x: Fraction(-1, 50),
                    u=lambda x: Fraction(3, 20) - (x - Fraction(5)) * Fraction(1, 50),
                ),
            ],
        ),
    )


def create_case_3() -> Axial1DBenchmark:
    # 3. Bar with uniform distributed load.
    # L=10, E=100, A=2, q=10 (positive to the right)
    # Fixed at x=0
    # R_0 + q*L = 0 -> R_0 = -100
    # N(x) = int_x^L q dt = q*(L-x) = 10*(10-x) = 100 - 10x
    # sigma(x) = N/A = 50 - 5x
    # eps(x) = sigma/E = (50 - 5x)/100 = 1/2 - x/20
    # u(x) = int eps = x/2 - x^2/40

    L = Fraction(10)
    E = Fraction(100)
    A = Fraction(2)
    q = Fraction(10)

    return Axial1DBenchmark(
        name="Case 3: Uniform distributed load",
        length=L,
        sections=[Section(Fraction(0), L, E, A, q)],
        point_loads=[],
        supports=[Support(Fraction(0), Fraction(0))],
        solution=ExactSolution(
            reactions={Fraction(0): Fraction(-100)},
            sections=[
                SectionSolution(
                    Fraction(0),
                    L,
                    N=lambda x: Fraction(100) - Fraction(10) * x,
                    sigma=lambda x: Fraction(50) - Fraction(5) * x,
                    eps_mech=lambda x: Fraction(1, 2) - x / Fraction(20),
                    eps_full=lambda x: Fraction(1, 2) - x / Fraction(20),
                    u=lambda x: x / Fraction(2) - (x**2) / Fraction(40),
                ),
            ],
        ),
    )


def create_case_4() -> Axial1DBenchmark:
    # 4. Bar fixed at both ends, concentrated force inside.
    # L=10. Fixed at x=0, x=10. E=100, A=2.
    # Force F=30 at x=4.
    # R_0 + R_10 + 30 = 0
    # u(10) = 0
    # Sec 1 (0 to 4): N1 = -R_0. eps1 = -R_0/(200). u(4) = -4*R_0/200 = -R_0/50
    # Sec 2 (4 to 10): N2 = -R_0 - 30. eps2 = (-R_0 - 30)/200.
    # u(10) = u(4) + 6*(-R_0 - 30)/200 = -R_0/50 - 6*R_0/200 - 180/200 = 0
    # -4*R_0 - 6*R_0 - 180 = 0 -> -10*R_0 = 180 -> R_0 = -18
    # R_10 = -30 - (-18) = -12
    # Sec 1: N = 18, sigma = 9, eps = 9/100, u(x) = 9x/100
    # Sec 2: N = 18 - 30 = -12, sigma = -6, eps = -6/100 = -3/50, u(x) = u(4) - 3/50*(x-4) = 36/100 - 3/50(x-4) = 9/25 - 3/50(x-4)

    return Axial1DBenchmark(
        name="Case 4: Fixed at both ends with internal point load",
        length=Fraction(10),
        sections=[
            Section(Fraction(0), Fraction(4), Fraction(100), Fraction(2), Fraction(0)),
            Section(Fraction(4), Fraction(10), Fraction(100), Fraction(2), Fraction(0)),
        ],
        point_loads=[PointLoad(Fraction(4), Fraction(30))],
        supports=[Support(Fraction(0), Fraction(0)), Support(Fraction(10), Fraction(0))],
        solution=ExactSolution(
            reactions={Fraction(0): Fraction(-18), Fraction(10): Fraction(-12)},
            sections=[
                SectionSolution(
                    Fraction(0),
                    Fraction(4),
                    N=lambda x: Fraction(18),
                    sigma=lambda x: Fraction(9),
                    eps_mech=lambda x: Fraction(9, 100),
                    eps_full=lambda x: Fraction(9, 100),
                    u=lambda x: x * Fraction(9, 100),
                ),
                SectionSolution(
                    Fraction(4),
                    Fraction(10),
                    N=lambda x: Fraction(-12),
                    sigma=lambda x: Fraction(-6),
                    eps_mech=lambda x: Fraction(-3, 50),
                    eps_full=lambda x: Fraction(-3, 50),
                    u=lambda x: Fraction(9, 25) - (x - Fraction(4)) * Fraction(3, 50),
                ),
            ],
        ),
    )


def create_case_5() -> Axial1DBenchmark:
    # 5. Fixed at both ends, uniform temperature change.
    # L=10, E=100, A=2, alpha=1/1000, delta_T = 50.
    # eps_full = eps_mech + alpha*delta_T
    # eps_mech = N/(EA)
    # N is constant. u(10) - u(0) = 0 -> int eps_full dx = 0
    # eps_full = N/(200) + 50/1000 = N/200 + 1/20 = 0
    # N/200 = -1/20 -> N = -10
    # R_0 = -N = 10 (Wait: N at x=0 side is R_0? N(x) + R_0 = 0 for no distributed load/forces. So R_0 = -N = 10)
    # Sum F = R_0 + R_10 = 0 -> R_10 = -10.
    # N = -10
    # sigma = -5
    # eps_mech = -5/100 = -1/20
    # eps_full = -1/20 + 1/20 = 0
    # u(x) = 0

    L = Fraction(10)

    return Axial1DBenchmark(
        name="Case 5: Fixed at both ends, uniform temperature change",
        length=L,
        sections=[
            Section(
                Fraction(0),
                L,
                Fraction(100),
                Fraction(2),
                Fraction(0),
                alpha=Fraction(1, 1000),
                delta_T=Fraction(50),
            ),
        ],
        point_loads=[],
        supports=[Support(Fraction(0), Fraction(0)), Support(L, Fraction(0))],
        solution=ExactSolution(
            reactions={Fraction(0): Fraction(10), L: Fraction(-10)},
            sections=[
                SectionSolution(
                    Fraction(0),
                    L,
                    N=lambda x: Fraction(-10),
                    sigma=lambda x: Fraction(-5),
                    eps_mech=lambda x: Fraction(-1, 20),
                    eps_full=lambda x: Fraction(0),
                    u=lambda x: Fraction(0),
                ),
            ],
        ),
    )


def create_case_6() -> Axial1DBenchmark:
    # 6. Prescribed relative displacement.
    # Fixed at x=0 with u(0)=0. Fixed at x=10 with u(10) = 1/5.
    # E=100, A=2, L=10.
    # N is constant. eps_full = eps_mech = N/200.
    # u(10) = 10 * (N/200) = N/20 = 1/5 -> N = 4
    # R_0 = -4. R_10 = 4. Wait. Sum F = R_0 + R_10 = 0 -> R_10 = 4.
    # Section x from 0 to 10:
    # N = 4
    # sigma = 2
    # eps = 2/100 = 1/50
    # u(x) = x/50. u(10) = 10/50 = 1/5. Correct.

    L = Fraction(10)

    return Axial1DBenchmark(
        name="Case 6: Prescribed support displacement",
        length=L,
        sections=[Section(Fraction(0), L, Fraction(100), Fraction(2), Fraction(0))],
        point_loads=[],
        supports=[Support(Fraction(0), Fraction(0)), Support(L, Fraction(1, 5))],
        solution=ExactSolution(
            reactions={Fraction(0): Fraction(-4), L: Fraction(4)},
            sections=[
                SectionSolution(
                    Fraction(0),
                    L,
                    N=lambda x: Fraction(4),
                    sigma=lambda x: Fraction(2),
                    eps_mech=lambda x: Fraction(1, 50),
                    eps_full=lambda x: Fraction(1, 50),
                    u=lambda x: x / Fraction(50),
                ),
            ],
        ),
    )


def check_benchmark(bm: Axial1DBenchmark):
    # 1. Global equilibrium
    # Sum F + Sum R + int q dx = 0
    sum_F = sum(p.value for p in bm.point_loads)
    sum_R = sum(r for r in bm.solution.reactions.values())
    sum_q = sum(sec.q * (sec.x_end - sec.x_start) for sec in bm.sections)

    assert sum_F + sum_R + sum_q == Fraction(0), f"Global equilibrium failed for {bm.name}"

    # 2. Section checks
    dx = Fraction(1, 1000)
    for sec, sol_sec in zip(bm.sections, bm.solution.sections):
        # 2a. Hooke's Law and stresses
        x_mid = (sec.x_start + sec.x_end) / Fraction(2)
        N_mid = sol_sec.N(x_mid)
        sigma_mid = sol_sec.sigma(x_mid)
        eps_mech_mid = sol_sec.eps_mech(x_mid)
        eps_full_mid = sol_sec.eps_full(x_mid)

        assert sigma_mid == N_mid / sec.A, "Stress not equal to N/A"
        assert eps_mech_mid == sigma_mid / sec.E, "Mechanical strain not equal to sigma/E"
        assert eps_full_mid == eps_mech_mid + sec.alpha * sec.delta_T, "Full strain incorrect"

        # 2b. Local equilibrium: N'(x) + q(x) = 0
        # Since solutions are piecewise polynomials, finite difference is exact enough or we can just check N'
        x1 = sec.x_start + dx
        x2 = sec.x_end - dx
        dN_dx = (sol_sec.N(x2) - sol_sec.N(x1)) / (x2 - x1)
        assert abs(dN_dx + sec.q) < Fraction(1, 1000000), "Local equilibrium failed"

        # 2c. Kinematic relation: u'(x) = eps_full
        du_dx = (sol_sec.u(x2) - sol_sec.u(x1)) / (x2 - x1)
        assert abs(du_dx - sol_sec.eps_full(x_mid)) < Fraction(1, 1000000), (
            "Kinematic relation failed"
        )

    # 3. Jumps in N and Continuity of u
    # N(x+) - N(x-) = -F_applied
    points_of_interest = set(p.x for p in bm.point_loads)
    points_of_interest.update(sec.x_start for sec in bm.sections)
    points_of_interest.update(sec.x_end for sec in bm.sections)

    for x in sorted(points_of_interest):
        # Applied force at x
        F_app = sum(p.value for p in bm.point_loads if p.x == x)
        R_app = bm.solution.reactions.get(x, Fraction(0))
        Total_force = F_app + R_app

        # Find N just to the left and right
        N_left = Fraction(0)
        u_left = None
        for sol_sec in bm.solution.sections:
            if sol_sec.x_end == x:
                N_left = sol_sec.N(x)
                u_left = sol_sec.u(x)

        N_right = Fraction(0)
        u_right = None
        for sol_sec in bm.solution.sections:
            if sol_sec.x_start == x:
                N_right = sol_sec.N(x)
                u_right = sol_sec.u(x)

        if x == Fraction(0):
            N_left = Fraction(0)
        if x == bm.length:
            N_right = Fraction(0)

        assert N_right - N_left == -Total_force, (
            f"Jump condition in N failed at x={x}. {N_right} - {N_left} != -{Total_force}"
        )

        if u_left is not None and u_right is not None:
            assert u_left == u_right, f"Continuity of u failed at x={x}"

    # 4. Boundary conditions
    for sup in bm.supports:
        # Find u at sup.x
        u_val = None
        for sol_sec in bm.solution.sections:
            if sol_sec.x_start <= sup.x <= sol_sec.x_end:
                u_val = sol_sec.u(sup.x)
                break
        assert u_val == sup.fixed_displacement, f"Support condition failed at x={sup.x}"


def test_case_1():
    check_benchmark(create_case_1())


def test_case_2():
    check_benchmark(create_case_2())


def test_case_3():
    check_benchmark(create_case_3())


def test_case_4():
    check_benchmark(create_case_4())


def test_case_5():
    check_benchmark(create_case_5())


def test_case_6():
    check_benchmark(create_case_6())


def test_negative_reaction():
    bm = create_case_1()
    # Spoil reaction
    bm.solution.reactions[Fraction(0)] = Fraction(999)
    with pytest.raises(AssertionError, match="Global equilibrium failed"):
        check_benchmark(bm)


def test_negative_internal_force_sign():
    bm = create_case_1()
    # Spoil internal force sign
    bm.solution.sections[0].N = lambda x: Fraction(-100)
    with pytest.raises(AssertionError, match="Stress not equal to N/A"):
        check_benchmark(bm)


def test_negative_kinematic_relation():
    bm = create_case_1()
    # Spoil displacement coefficient
    bm.solution.sections[0].u = lambda x: x / Fraction(5)
    with pytest.raises(AssertionError, match="Kinematic relation failed"):
        check_benchmark(bm)
