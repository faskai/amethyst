# Amethyst Formal Language (AFL)

AFL reads like natural English typed by non-technical users. Amethyst Casual Language (ACL) is even more casual and doesn’t require any syntax. The IDE automatically converts ACL to AFL.

---

## 1) Core ideas (minimal nouns, natural verbs)

* **entity** — anything that exists (people, cities, files, scenes)
* **agent** — an entity that notices, decides, and acts
* **tool** — an entity that performs I/O or side effects (unity, email)
* **function** — a named capability; can live at top level or inside an entity
* **event** — a trigger written as `when condition ... end when`

---

## 2) Unified call and import shape

**Canonical AFL invocation and import**

```
use <entity> - <resource> <role>: <value>, <role>: <value>, ...
```

* **Entity**: a noun (agent/tool/system)
* **Resource**: a callable capability, function, or imported module
* **Arguments**: comma-separated role–value pairs
* **Values**: may be multi-word without quotes (e.g., `main scene`, `safe place`)
* Each line is one statement; a new line means the next step.

**Examples (calls)**

```
use unity - render scene: main scene, camera: main camera
use player - move to: safe place
use browser - open url: https://amethyst.dev, timeout: 5 seconds
use email - send to: alice@example.com, subject: weekly report, body: draft report
```

**Examples (imports)**

```
use agent perplexity ai - browse
use model openai - GPT-4o temperature: 0.3
```

---

## 3) Blocks — free text, no indentation

* **Definition blocks**: start/end keywords define scope. Example: `start in parallel ... end parallel`.
* **Single-line statements**: written as complete English sentences (e.g., `in parallel use ...`).

**Example**

```
entity person
name: Joe
age: 25
end entity

agent world controller
when player clicks npc
if npc mood is friendly
a: in parallel use dialogue - start conversation speaker: player, listener: npc
b: in parallel use hud - show message: You made a friend
wait for a, b
else
use combat - start fight attacker: player, defender: npc
end if
end when
end agent

start in parallel
use unity - bake lightmaps
use unity - build cities
end parallel
```

---

## 4) Unified loops and conditions

* **Conditionals**: `if condition  ... else if condition ... else ... end if`
* **Comparisons**: `is`, `is not`, `is greater than`, `is less than or equal to`
* **Boolean logic**: `and`, `or`, `not`
* **Loops (single family)**:

  * `repeat 10 times ... end repeat`
  * `repeat while <condition> ... end repeat`
  * `repeat for each <item> in <list> ... end repeat`
* **Break / Continue**: `stop loop`, `skip this`
* **Math verbs**: `add`, `reduce`, `multiply`, `divide` (`+ - * /` allowed as shortcuts)

---

## 5) Minimal keyword set

```
set, add, reduce, multiply, divide      # + - * / allowed as shortcuts
insert <a> into <b>, <x> to <y>         # list operations
if, else
repeat, end repeat                      # repeat 10 times / repeat while / repeat for each
in parallel, wait for
entity, agent, tool, function
when, end when
<name> <newline> ... end <name>         # start end of multiline blocks
use, -                                  # dash connects entity and resource, args use role: value
```

Whitespace and indentation have no meaning; newline, punctuation and keywords control scope and parsing.

---

| Category                   | Amethyst CL                   | Amethyst FL                                                                   | Python                                                   | Ruby                  | Notes                                 |
| -------------------------- | ----------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------- | ------------------------------------- |
| Define entity              | a person with name and age    | `entity person ... end entity`                                                | `class Person`                                           | `class Person`        | One form for definable things         |
| Define agent/tool/function | define an agent/tool/function | `agent A ... end agent`, `tool T ... end tool`, `function F ... end function` | class/def                                                | class/def             | Same block shape                      |
| Attributes                 | person has name Joe           | `name: Joe`, `age: 25`                                                        | instance vars                                            | same                  | Declarative attributes                |
| Invocation                 | Unity render scene            | `use unity - render scene: main scene, camera: main camera`                   | `unity.render(scene="main scene", camera="main camera")` | same                  | Unified grammar; comma-separated args |
| Assignment                 | set health 100                | `set health: 100` (`health = 100`)                                            | `health = 100`                                           | same                  | Removed redundant `to`                |
| Insert into list           | put 5 in numbers at 2         | `insert 5 into numbers position: 2`                                           | `numbers.insert(1, 5)`                                   | `numbers.insert(1,5)` | Reads naturally, avoids tech terms    |
| Math updates               | add 5 to score / score + 5    | `add 5 to score` (`score + 5`)                                                | `score += 5`                                             | same                  | Verbal or symbolic                    |
| Comparisons                | if weather is sunny           | `if weather is sunny ... end if`                                              | `if weather == "sunny":`                                 | same                  | Natural comparative language          |
| Boolean logic              | and, or, not                  | `and`, `or`, `not`                                                            | same                                                     | same                  | Natural connectors                    |
| Conditionals               | otherwise                     | `else`                                                                        | `else`                                                   | `else`                | Synonyms normalize to `else`          |
| Loops (count)              | do this 10 times              | `repeat 10 times ... end repeat`                                              | `for i in range(10)`                                     | `10.times do ... end` | Unified under `repeat`                |
| Loops (while)              | while health above 0          | `repeat while health is greater than 0 ... end repeat`                        | `while health > 0`                                       | same                  | Unified under `repeat`                |
| Loops (collection)         | for each enemy                | `repeat for each enemy in enemies ... end repeat`                             | `for enemy in enemies`                                   | same                  | Collection may be inferred            |
| Break/Continue             | stop / skip this              | `stop loop`, `skip this`                                                      | `break`, `continue`                                      | `break`, `next`       | Plain verbs                           |
| Parallel (single-line)     | at the same time              | `in parallel use X - ...`                                                     | async/gather                                             | threads               | No `do` keyword                       |
| Parallel (block)           | run these together            | `start in parallel ... end parallel`                                          | gather block                                             | threads               | Paragraph-style block                 |
| Wait                       | wait for both                 | `wait for a, b`                                                               | `await gather(a, b)`                                     | `join`                | Uses labels                           |
| Events                     | when player clicks npc        | `when player clicks npc ... end when`                                         | callbacks                                                | blocks                | Native trigger                        |
| Imports                    | use Unity                     | `use agent perplexity ai - browse`                                            | `import unity`                                           | `require`             | Unified import shape                  |
