# Axial 1D Analytical Benchmarks

This document outlines the six analytical benchmark cases designed to verify the `Axial1D` structural mechanics solvers and checks within the Bender subsystem. These benchmarks are formulated to yield exact solutions representable by rational numbers and piecewise polynomials, avoiding floating-point inaccuracies. They serve as physical ground truths.

## General Sign Conventions and Notation

The exact tests and analytical derivations use the following conventions strictly:
- **Global Coordinate System**: The $x$-axis runs along the bar. The origin $x=0$ is typically at the left end.
- **Direction**: Right is positive, left is negative.
- **Forces**: Applied point loads ($F$) and distributed loads ($q$) are positive if pointing to the right.
- **Displacements**: Displacement $u(x)$ is positive if to the right.
- **Internal Normal Force ($N$)**: Positive in tension (i.e., causes elongation). A positive $N$ at a cut means the material to the left is pulling the material to the right towards the left (and vice versa).
- **Stress ($\sigma$)**: Positive in tension ($\sigma = N/A$).
- **Strain ($\varepsilon$)**: Positive for elongation. Mechanical strain $\varepsilon_{mech} = \sigma / E$. Total strain $\varepsilon_{full} = \varepsilon_{mech} + \alpha \Delta T$.

## Automated Invariant Checks

The following invariants are checked in the automated tests (`tests/bender/exact/axial1d/test_axial1d_benchmarks.py`):
1. **Global equilibrium**: $\sum F + \sum R + \int q dx = 0$.
2. **Local equilibrium**: $N'(x) + q(x) = 0$ at any cross-section.
3. **Internal force jumps**: $N(x^+) - N(x^-) = - (F_{applied} + R_{applied})$.
4. **Hooke's Law**: $\sigma = N/A$, $\varepsilon_{mech} = \sigma/E$, $\varepsilon_{full} = \varepsilon_{mech} + \alpha\Delta T$.
5. **Kinematic relation**: $u'(x) = \varepsilon_{full}$.
6. **Boundary conditions**: The displacement $u(x)$ must match fixed displacement values at support locations.
7. **Continuity**: The displacement function $u(x)$ must be continuous across section boundaries.

---

## Case 1: Constant EA, fixed at one end, force at the other

**Description**: A simple bar of constant cross-section fixed at the left end and pulled by a single force at the right end.

**Parameters**:
- $L = 10$, $E = 200$, $A = 5$
- Support at $x = 0$ with $u(0) = 0$
- Force $F = 100$ at $x = 10$

**Analytical Method**:
- **Equilibrium**: The reaction at the left support $R_0$ balances the applied force: $R_0 + F = 0 \implies R_0 = -100$.
- **Internal Force**: Making a cut at $x$, taking the right side: $-N + F = 0 \implies N(x) = 100$.
- **Stress & Strain**: $\sigma = 100/5 = 20$, $\varepsilon_{mech} = 20/200 = 1/10$.
- **Displacement**: $u(x) = \int \varepsilon_{mech} dx = x/10 + C$. With $u(0) = 0$, $C = 0$.

**Results**:
- $R_0 = -100$
- $N(x) = 100$
- $\sigma(x) = 20$
- $\varepsilon(x) = 1/10$
- $u(x) = x/10$

---

## Case 2: Stepped bar with multiple concentrated forces

**Description**: A bar with two segments of different stiffnesses, subject to point loads in opposite directions.

**Parameters**:
- Section 1: $x \in [0, 5]$, $E = 100$, $A = 10$
- Section 2: $x \in [5, 10]$, $E = 200$, $A = 5$
- Support at $x = 0$ with $u(0) = 0$
- Forces: $F_1 = 50$ at $x = 5$, $F_2 = -20$ at $x = 10$

**Analytical Method**:
- **Equilibrium**: $R_0 + F_1 + F_2 = 0 \implies R_0 = -30$.
- **Section 2 ($5 < x \le 10$)**: Cut at $x$, take right side: $-N + F_2 = 0 \implies N = -20$.
- **Section 1 ($0 \le x < 5$)**: Cut at $x$, take right side: $-N + F_1 + F_2 = 0 \implies N = 30$.
- **Displacements**:
  - $0 \le x \le 5$: $\sigma_1 = 30/10 = 3$, $\varepsilon_1 = 3/100$, $u(x) = 3x/100$. At $x=5$, $u(5) = 15/100 = 3/20$.
  - $5 < x \le 10$: $\sigma_2 = -20/5 = -4$, $\varepsilon_2 = -4/200 = -1/50$, $u(x) = 3/20 - (x-5)/50$.

**Results**:
- $R_0 = -30$
- $N(x) = \{30 \text{ for } x \in (0, 5); -20 \text{ for } x \in (5, 10)\}$
- $u(x) = \{3x/100 \text{ for } x \in (0, 5); 3/20 - (x-5)/50 \text{ for } x \in (5, 10)\}$

---

## Case 3: Uniform distributed load

**Description**: A bar with constant stiffness fixed at the left end, subjected to a uniformly distributed load.

**Parameters**:
- $L = 10$, $E = 100$, $A = 2$
- $q = 10$ (positive to the right)
- Support at $x = 0$ with $u(0) = 0$

**Analytical Method**:
- **Equilibrium**: $R_0 + \int_0^L q dx = 0 \implies R_0 = -10 \times 10 = -100$.
- **Internal Force**: Take cut at $x$, sum forces on right portion: $-N(x) + \int_x^L q ds = 0 \implies N(x) = q(L - x) = 10(10 - x) = 100 - 10x$.
- **Stress & Strain**: $\sigma = (100 - 10x)/2 = 50 - 5x$, $\varepsilon = (50 - 5x)/100 = 1/2 - x/20$.
- **Displacement**: $u(x) = \int \varepsilon dx = x/2 - x^2/40 + C$. $u(0) = 0 \implies C = 0$.

**Results**:
- $R_0 = -100$
- $N(x) = 100 - 10x$
- $u(x) = x/2 - x^2/40$

---

## Case 4: Fixed at both ends with internal point load

**Description**: A statically indeterminate bar fixed at both ends, with a single internal point load. Reaction forces must be found using compatibility conditions.

**Parameters**:
- $L = 10$, $E = 100$, $A = 2$
- Supports at $x = 0$ and $x = 10$ ($u(0) = 0, u(10) = 0$)
- Force $F = 30$ at $x = 4$

**Analytical Method**:
- **Equilibrium**: $R_0 + R_{10} + 30 = 0$.
- **Internal Force**:
  - $0 \le x < 4$: $N_1 = -R_0$.
  - $4 < x \le 10$: $N_2 = -R_0 - 30$.
- **Compatibility**: $\Delta L_{total} = \int_0^4 \frac{N_1}{EA} dx + \int_4^{10} \frac{N_2}{EA} dx = 0$.
  - $\frac{-4 R_0}{200} + \frac{6(-R_0 - 30)}{200} = 0 \implies -10 R_0 - 180 = 0 \implies R_0 = -18$.
  - $R_{10} = -30 - (-18) = -12$.
- **Internal Force**: $N_1 = 18$, $N_2 = -12$.
- **Displacements**:
  - $u(x)$ for $x \in [0, 4] = 9x/100$. $u(4) = 36/100 = 9/25$.
  - $u(x)$ for $x \in [4, 10] = 9/25 - 3(x-4)/50$.

**Results**:
- $R_0 = -18$, $R_{10} = -12$
- $N(x) = \{18 \text{ for } x \in (0, 4); -12 \text{ for } x \in (4, 10)\}$
- $u(x) = \{9x/100 \text{ for } x \in (0, 4); 9/25 - 3(x-4)/50 \text{ for } x \in (4, 10)\}$

---

## Case 5: Fixed at both ends, uniform temperature change

**Description**: A statically indeterminate bar fixed at both ends and subjected to a uniform temperature change.

**Parameters**:
- $L = 10$, $E = 100$, $A = 2$
- Supports at $x = 0$ and $x = 10$ ($u(0) = 0, u(10) = 0$)
- $\alpha = 1/1000$, $\Delta T = 50$

**Analytical Method**:
- **Strain relation**: $\varepsilon_{full} = \varepsilon_{mech} + \alpha \Delta T = \frac{N}{EA} + \alpha \Delta T$.
- **Compatibility**: $\int_0^L \varepsilon_{full} dx = 0 \implies 10 \left( \frac{N}{200} + \frac{50}{1000} \right) = 0 \implies \frac{N}{200} = -\frac{1}{20} \implies N = -10$.
- **Equilibrium**: Since $N$ is uniform, $R_0 + N(0) = 0 \implies R_0 = -(-10) = 10$. And $R_0 + R_{10} = 0 \implies R_{10} = -10$.
- **Strains**: $\varepsilon_{mech} = -10/200 = -1/20$. $\varepsilon_{full} = -1/20 + 1/20 = 0$.
- **Displacement**: $u(x) = 0$.

**Results**:
- $R_0 = 10$, $R_{10} = -10$
- $N(x) = -10$
- $u(x) = 0$
- $\varepsilon_{mech}(x) = -1/20$, $\varepsilon_{full}(x) = 0$

---

## Case 6: Prescribed support displacement

**Description**: A statically indeterminate bar fixed at one end, and forced to move by a known exact amount at the other end.

**Parameters**:
- $L = 10$, $E = 100$, $A = 2$
- Support at $x = 0$ with $u(0) = 0$
- Support at $x = 10$ with $u(10) = 1/5$

**Analytical Method**:
- **Compatibility**: $\int_0^{10} \frac{N}{EA} dx = u(10) - u(0) = 1/5$.
- $10 \cdot \frac{N}{200} = 1/5 \implies \frac{N}{20} = 1/5 \implies N = 4$.
- **Equilibrium**: $R_0 + N(0) = 0 \implies R_0 = -4$. $R_{10} = 4$.
- **Stress & Strain**: $\sigma = 4/2 = 2$, $\varepsilon = 2/100 = 1/50$.
- **Displacement**: $u(x) = x/50$.

**Results**:
- $R_0 = -4$, $R_{10} = 4$
- $N(x) = 4$
- $u(x) = x/50$
