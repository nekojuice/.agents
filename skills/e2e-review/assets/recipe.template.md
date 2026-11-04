---
purpose: <what this flow achieves, e.g. prepare records whose due date falls inside a reminder window>
preconditions: <state required before step 1>
surfaces:
  - web
  - api
writes: <data this recipe creates or changes, or none>
---

# <Recipe title>

<One or two sentences: when to use this recipe and what the result looks like.>

### 1. <Step title>

```yaml
id: 1
surface: api
kind: script
run: actions/<fragment>
args: {account: <account key>}
save: <value file name>
expect: <what the returned value must show>
```

### 2. <Step title>

```yaml
id: 2
surface: web
kind: agent
do: <what the agent operates and how, e.g. which tool and which screen>
expect: <what must be true afterwards>
evidence:
  - shots/<name>.png
  - values/<name>.json
```
