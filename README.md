## Amethyst AI

`Amethyst` is the first no-code, AI-native programming language and IDE. It's the simplest way to build apps and feels like talking to a human. We're taking "English is the next programming language" to its logical conclusion.

This doc is a whitepaper and outlines the vision and specs. The code will follow soon.

<img src="/Amethyst.jpg" width="50%" height="50%">  

### Who is Amethyst For
Amethyst is for 2 user groups:
* **Consumers** – Amethyst Casual Language (ACL) is free-flowing chat with no grammar rules or syntax. It's meant for non-tech casual users to easily build powerful AI agents and apps to automate homes, tasks, etc. They will get a simple GUI editor that works on all devices.
* **Developers** – Amethyst Formal Language (AFL) is structured, precise and scalable, but still is dead-simple and reads like natural English. It's meant for non-tech enterprise users. They will get an IDE and tools for managing Amethyst applications globally at scale.

Both ACL and AFL supports debugging with breakpoints, uses abstractions and composability. The IDE will convert ACL to AFL.

### Why Amethyst
Current multi-agent frameworks are great but still too complex.
* Crew.ai, MetaGPT, Langchain, etc. solve the accuracy problem, but require devs to write a lot of code. Not for consumers. *Why write code when you can just talk to the AI?*
* Lindy.ai, OpenAI Agent Builder, MS Copilot, Botpress, Zapier AI, etc. – they all need drag-and-drop workflows which can get messy pretty fast with enterprise use-cases. They don't offer code-like composability or debugging.

We've used several agent frameworks and tried our hand at building two frameworks here at Fask – one workflow-based and one GUI – and we still don't like what we built.

At Amazon I've been in "workflow hell" where you stare down 1000s of "stuck" workflows with complicated branchings that are so big that they don't fit your GUI editor. You can't refactor them or test them. A small change can cause even worse downstream issues which you may find out weeks later. 🤮

Instead of workflows, with Amethyst you build teams of agents, and you instruct them in plain English like you'd talk to your human assistant or employees. Using them as abstractions, you can *compose* software applications and hierarchies of agents for high-level tasks, without being bogged down by low-level details. Abstractions help us build complexity without making things complicated. 

Amethyst is inspired by Ruby, and gives you radical simplicity while taking care of all the necessary complexity under the hood:
- Guardrails for accuracy
- Executing large business workflows reliably
- Auto-scaling for high availability
- Parallel processing

### Amethyst Language

[See the full spec.](https://github.com/faskai/amethyst/blob/main/docs/amethyst-syntax.md)

#### Example: day planner

File `day planner.amt`
```
agent day planner
plan a day depending on the weather
use get weather to check forecast
if weather is sunny
use all trails to find good hikes nearby under 10k with views
else if rainy
use open table to find and book any nice waterfront restaurant with PNW food
end if

a: in parallel use browser to book parking
b: in parallel use todoist to plan todo and packing list
wait for a, b

use email to send the final plan
end agent
```

##### How to Read This

* Every **agent** is a smart assistant that follows your instructions. `all trails`, `open table` are agents from AllTrails and OpenTable. `browser` automates web tasks; `email` sends messages; `todoist` manages to-dos.
* **tools** — `get weather` is a tool.
* You don’t need punctuation, brackets, or symbols — just sentences.
* **Parallel tasks**: Add `a:` or `b:` before lines to label them, use `in parallel` key phrase, then `wait for a, b` to continue after both finish.
* **Conditions**: Use natural phrases like `if weather is sunny` or `else if rainy`.

#### Multi-Agents

**All Trails agent**
```
agent all trails
use find trails to search for hiking spots
use all trails verifier to double check trail distance and elevation
end agent
```

**Verifier agent (optional)**
```
agent all trails verifier
verify that each trail matches distance and elevation requirements
end agent
```

This shows how multiple agents can work together for verification — useful for enterprise tasks like auditing or accounting.

> 🔮 *Future:* Amethyst will abstract this multi-agent madness, so users won’t have to define cross-checking logic explicitly.

#### Using the Agents

Use agents:
* naturally in chat (Casual Language)
```
plan my saturday using day planner
```
* on schedules, events, user inputs or API calls

That's it! Amethyst agents will follow instructions and deliver results (e.g., an email with your final plan).

#### Behind the Scenes

Amethyst converts ACL into ASL and AFL, that runs as Python code. The same file can be read like English, debugged like code, and executed by an intelligent engine.

> 🧐 *Why not Ruby?* Python’s LLM and agent ecosystem is mature. The goal isn’t to mimic Ruby syntax but to achieve Ruby-like simplicity and readability.

#### Imports

You can bring in external agents or tools easily, just like adding apps to your phone.
* **No code**: Use the GUI IDE to browse, select and OAuth the tools and agents from a global repo.
* **Low code**: Imports are written using the `use <type> <provider> - <name>` pattern. Amethyst will provide a package manager, similar to `npm` or `pip`.

```
agent campsite finder
use agent perplexity ai - browse
use model openai - GPT-4o temperature: 0.3
find campsites nearby using browse
end agent
```

##### Notes
* These imported resources may run locally or remotely (using **MCP** and **A2A** protocols). 
* You can also configure the LLM model per agent (GPT-4o, etc.).
* Agents or tools may pause for user input (e.g., login, captcha). Amethyst resumes automatically once resolved.

#### Environments

Each agent runs in an **environment** (env) such as MacOS, iOS, Browser, Docker, or Raspberry Pi. You can extend environments to create your own. Environments determine available tools and agents (e.g., browsers can’t run on Raspberry Pi). The compiler raises errors for incompatible contexts.

You can define tools, agents and other entities (analogous to classes) in `.amt` (amethyst) files:

example_file.amt:
```
tool get_weather
{
  # JSON schema of tool
}

agent day_planner
# agent code...
end day_planner
```

#### Built-in Agents and Tools

Amethyst comes ready with:

* `swe` — coding assistant
* `browser` — for browsing and booking
* `date time` — for scheduling

### Coming Soon
As with any programming language there will be more docs and features around:
* Error handling: By default, Amethyst errors will be thrown with full details up the stack. Devs may try/catch them.
* Testing agents, tools, blocks and entity and functions.
* Details on how to publish packages and importing from external repos.
* Looping: E.g., `Repeat while` condition is met.
* Debugging: Amethyst IDE will allow breakpoints where you can step through each line of code or a whole `block`.
* Seamless code gen: Just type or talk freely, and the IDE will automatically convert Casual Language to Formal Language.
* Deploying, monitoring, scaling.
* Inputs and triggers: what starts an agent or application? API call, webhook, user input, etc.
* Chat with amethyst: Instead of writing .amt files, just send a message (ACL) and the agent will execute it.
* Multiplayer chat with humans and agents for group collaborative editing.
* Live multimodal agents: Agents that run continuously and can see, hear and read by processing a stream of data (audio, video, XR, streaming text).
* Dynamic `blocks`: Agents will produce dynamic Amethyst `blocks` from streaming input which will be executed at runtime. It's basically like an Agent dynamically coding and executing it. You don't even need to write the Agent logic beforehand. For example:
  * A video agent looking at a live security footage may produce blocks like `intruder alert, invoking @alarm_agent`, depending on what they see. The block will be executed at run time, thus enabling the agent to dynamically invoke another agents and tools.
  * The agent can also send dynamic blocks explicitly to other sub-agents for post-processing and verification. `@assistant_agent, double check @block`
  * Of course, the dynamic `blocks` will be logged for debugging. *We're not insane.*
* Fine-tuning: Live agents can be fine tuned to produce desired dynamic blocks (they're like thoughts). For example, the security agent can be fine tuned to raise alert only when someone unknown gets inside the property, and ignore known faces.

Agents calling agents calling agents in a big, recursive agentic web! Now're we're on our way to digital superintelligence.