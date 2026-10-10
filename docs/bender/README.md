# Bender

Bender is a large internal subsystem for:
- creating problems in mechanics of materials;
- generating variants;
- solving problems analytically with specific methods;
- outputting real step-by-step solutions (causal `SolutionTrace`);
- visualization;
- independent cross-verification;
- integration with Studium features.

## What Bender is NOT
- It is NOT a standard numerical solver.
- It is NOT a FEM frontend.
- It is NOT just a set of diagram drawing tools.
- It is NOT a generator of textual explanations from pre-computed answers.

## Architecture
Bender is located within the Studium repository but is a distinct Python package.

### Dependency Direction
`studium -> bender` is ALLOWED.
`bender -> studium` is FORBIDDEN.

Bender must not know about domain entities like `Student`, `Group`, `Lesson`, `Homework`, etc.

### Core Architectural Layers
- **Core**: Mechanics-agnostic abstractions.
- **Domains**: Various theories and mathematical grammars (e.g., `axial1d`, `beam_planar`).
- **Methods**: Implementations of pedagogical algorithms.
- **Reference**: Cross-verification solvers.
- **Structural**: Structural graph topologies for methods that require them.
- **Graphics**: Diagram frame visualization bindings.
- **Verification**: Contracts and cross-checks.
- **Generation**: Constraint-based problem definition construction.

## Current Implementation Status
BND-00: Foundation Architecture Bootstrap. Currently establishing architectural boundaries and skeletons.

## Roadmap
See `roadmap.md` for details.
