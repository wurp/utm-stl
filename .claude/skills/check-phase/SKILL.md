---
name: check-phase
description: Audit completion status of a build phase
disable-model-invocation: true
---
Check completion status for phase: $ARGUMENTS

1. Read plan/plan-implementation-plan.md and find the component list for the specified phase
2. For each component in the phase:
   a. Check if specs/<component>/spec.md exists
   b. Check if pkg/<component>/ exists with Go source files
   c. If source exists, run `go build ./pkg/<component>/...`
   d. If source exists, run `go test ./pkg/<component>/...`
3. Report a summary table:

```
| Component | Spec | Code | Builds | Tests Pass |
|-----------|------|------|--------|------------|
```

4. List any blocking issues found
