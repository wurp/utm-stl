---
name: new-module
description: Scaffold a new Go module in the monorepo
disable-model-invocation: true
---
Create a new Go module: $ARGUMENTS

1. Verify specs/$ARGUMENTS/spec.md exists. If not, stop and say the spec must be written first (use /spec-component).
2. Read the spec to understand the types and interfaces.
3. Check ~/projects/ourcloud-attempt-1/pkg/ for a corresponding package. If one exists, review it for proven algorithms, edge cases, and test patterns worth carrying forward.
4. Create pkg/$ARGUMENTS/ directory.
5. Create pkg/$ARGUMENTS/go.mod with appropriate module path.
6. Add the module to go.work.
7. Create Go source files with types and interfaces from the spec. Use one file per major type or interface.
8. Create corresponding _test.go files with table-driven test stubs for each exported function/method.
9. Run `go build ./pkg/$ARGUMENTS/...` to verify compilation.
10. Run `go test ./pkg/$ARGUMENTS/...` to verify tests execute (stubs should pass).
