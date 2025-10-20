Amethyst Formal Language (AFL) aims to read like natural English typed by non-technical users. Scope is defined by explicit start/end markers for multi-para statements, or just in one line without start/end. This doc outlines the AFL specs.

Amethyst Casual Language (ACL) is even more casual and does not need any syntax at all. The IDE will convert ACL to AFL.

---

# 1) Core ideas (minimal nouns, natural verbs)

* **entity** — anything that exists (people, cities, files, scenes)
* **agent** — an entity that notices, decides, and acts
* **tool** — an entity that performs I/O or side effects (unity, browser, email)
* **function** — a named capability; can live at top level or inside an entity/agent/tool
* **event** — a trigger written as "when ... then ... end when"

---

# 2) Unified call shape (tools, methods, functions)

**Canonical AFL invocation**

```
use <actor> to <action> <role> <value>, <role> <value>, ...
```

* **Actor**: noun (entity/agent/tool)
* **Action**: verb phrase (capability)
* **Arguments**: comma-separated role–value pairs
* **Values**: may be multi-word without quotes (e.g., `main scene`, `safe place`)
* End of line ends the call.

**Examples**

```
use unity to render scene main scene, camera main camera
use player to move to safe place
use browser to open url https://amethyst.dev, timeout 5 seconds
use email to send to alice@example.com, subject weekly report, body draft report
```

---

# 3) Blocks — free text, no indentation

* **Definition blocks**: start/end keywords define scope. Example, parallel blocks: explicit `start in parallel ... end parallel`.
* **Single line statements**: `if .. then ..`; `in parrallel ..` 

**Example**

```
entity person
name Joe
age 25
end entity

agent world controller
when player clicks npc then
if npc mood is friendly then
a: in parallel use dialogue to start conversation speaker player, listener npc
b: in parallel use hud to show message You made a friend
wait for a, b
else
use combat to start fight attacker player, defender npc
end if
end when
end agent

start in parallel
use unity to bake lightmaps
use unity to build cities
end parallel
```

---

# 4) Unified loops and conditions

* **Conditionals**: `if ... then ... else ... end if`
* **Comparisons**: `is`, `is not`, `is greater than`, `is less than or equal to`
* **Boolean**: `and`, `or`, `not`
* **Loops (single family)**:

  * `repeat 10 times ... end repeat`
  * `repeat while <condition> ... end repeat`
  * `repeat for each <item> in <list> ... end repeat`
* **Break/Continue**: `stop loop`, `skip this`
* **Math verbs**: `add`, `reduce`, `multiply`, `divide` (`+ - * /` allowed as shortcuts)

---

# 5) Minimal keyword set

```
set, add, reduce, multiply, divide      # + - * / allowed as shortcuts
if, then, else, end if
repeat, end repeat                      # repeat 10 times / repeat while / repeat for each
in parallel, start in parallel, end parallel, wait for
entity, agent, tool, function, end
when, end when
use, to                                 # arguments use commas; no 'with' or 'and'
```

Whitespace and indentation have no meaning; explicit markers and tokens control parsing.

---

# 6) Comparison snapshot (CL → FL → Python → Ruby)

| Category                   | Amethyst CL                   | Amethyst FL                                                                   | Python                                                   | Ruby                  | Notes                                 |
| -------------------------- | ----------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------- | ------------------------------------- |
| Define entity              | a person with name and age    | `entity person ... end entity`                                                | `class Person`                                           | `class Person`        | One form for definable things         |
| Define agent/tool/function | define an agent/tool/function | `agent A ... end agent`, `tool T ... end tool`, `function F ... end function` | class/def                                                | class/def             | Same block shape                      |
| Attributes                 | person has name Joe           | `name Joe`, `age 25`                                                          | instance vars                                            | same                  | Declarative attributes                |
| Invocation                 | Unity render scene            | `use unity to render scene main scene, camera main camera`                    | `unity.render(scene="main scene", camera="main camera")` | same                  | Unified grammar; comma-separated args |
| Assignment                 | set health to 100             | `set health to 100` (`health = 100`)                                          | `health = 100`                                           | same                  | `=` optional shortcut                 |
| Math updates               | add 5 to score / score + 5    | `add 5 to score` (`score + 5`)                                                | `score += 5`                                             | same                  | Verbal or symbolic                    |
| Comparisons                | if weather is sunny           | `if weather is sunny then ... end if`                                         | `if weather == "sunny":`                                 | same                  | Natural comparative language          |
| Boolean logic              | and, or, not                  | `and`, `or`, `not`                                                            | same                                                     | same                  | Natural connectors                    |
| Conditionals               | otherwise                     | `else`                                                                        | `else`                                                   | `else`                | Synonyms normalize to `else`          |
| Loops (count)              | do this 10 times              | `repeat 10 times ... end repeat`                                              | `for i in range(10)`                                     | `10.times do ... end` | Unified under `repeat`                |
| Loops (while)              | while health above 0          | `repeat while health is greater than 0 ... end repeat`                        | `while health > 0`                                       | same                  | Unified under `repeat`                |
| Loops (collection)         | for each enemy                | `repeat for each enemy in enemies ... end repeat`                             | `for enemy in enemies`                                   | same                  | Collection may be inferred            |
| Break/Continue             | stop / skip this              | `stop loop`, `skip this`                                                      | `break`, `continue`                                      | `break`, `next`       | Plain verbs                           |
| Parallel (single-line)     | at the same time              | `in parallel use X to ...`                                                    | async/gather                                             | threads               | No `do` keyword                       |
| Parallel (block)           | run these together            | `start in parallel ... end parallel`                                          | gather block                                             | threads               | Paragraph-style block                 |
| Wait                       | wait for both                 | `wait for a, b`                                                               | `await gather(a, b)`                                     | `join`                | Uses labels                           |
| Events                     | when player clicks npc        | `when player clicks npc then ... end when`                                    | callbacks                                                | blocks                | Native trigger                        |
| Imports                    | use Unity                     | `use unity`                                                                   | `import unity`                                           | `require`             | Purpose phrase optional               |

---

