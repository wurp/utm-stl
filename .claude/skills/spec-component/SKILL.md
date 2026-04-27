---
name: spec-component
description: Write or update a component design from plan source documents
disable-model-invocation: true
---
Create or update the design for component: $ARGUMENTS

1. Read plan/plan-implementation-plan.md and find the source mapping table row for this component
2. Read each referenced plan section and tech-spec file listed in that row
3. If advisory sources are listed, read those too
4. Check ~/projects/ourcloud-attempt-1/ for relevant source material:
   - tech-spec/*.md for protocol details, validation rules, error codes, crypto parameters
   - tech-spec/schemas/cbor/*.cddl for wire format definitions
   - tech-spec/ourcloud.proto for gRPC message definitions
   - pkg/ for implementation details and edge cases discovered in practice
4. Write pkg/<component>/<component>_design.go following Design-as-Code conventions:

   - `//go:build design` tag
   - `// Status: DRAFT`
   - Go types and interfaces with concrete types from plan module definition
   - Validation rules and test expectations as doc comments
   - `// OPEN:` for unresolved decisions
   - `// --- Open Questions ---` block at end

5. Wire format references should point to `pkg/<module>/*.cddl` (per-package CDDL)
6. If advisory sources exist, add design rationale as doc comments or a separate advisory section in the design file
7. Verify all interface methods from the plan appear in the design
8. Verify all referenced CDDL types exist in the relevant `pkg/<module>/*.cddl`
