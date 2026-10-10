# Methods

## Open-ended Method Registry
Methods are registered dynamically via a generic `MethodRegistry`. Adding a new solver does not require modification to Bender Core.

## Pedagogical Family vs Implementation
A pedagogical principle, like "Method of Sections", can have different mathematical applications across different domains.

We prohibit a "Universal Solver" masquerading as multiple methods.
Instead, we specify distinct domain implementations:

- `axial.sections`
- `torsion.sections`
- `beam.sections`
- `truss.sections`
- `frame2d.sections`
- `frame3d.sections`

Each relies on the same pedagogical approach (cut -> isolate -> expose actions -> equilibrium) but operates on domain-specific mathematical semantics.

## Future Extension
To extend the system, register a new solver in `methods` using `MethodDescriptor`, which specifies capabilities, assumptions, and failure modes.
