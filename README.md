## Amethyst AI

`Amethyst` is the first AI-native language and IDE to build agents. 

It optimizes human happiness by hiding complexity. We're taking "English is the next programming language" to its logical conclusion.

Internally, Amethyst takes care of reliability, accuracy (supports multi-agents) and provides enterprise level scale, so that builders don't have to write explicit code for them. It's inspired by the principles of Ruby and uses convention-over-configuration choices in many places to keep the developer experience simple.

This doc is a whitepaper and outlines the vision and specs. The code will follow soon.

<img src="/Amethyst.jpg" width="50%" height="50%">  

### Who is Amethyst For
Amethyst is for 2 user groups:
* **Consumers** – non-tech users who want to easily build powerful AI sidekicks to automate their lives; builders and tinkerers who want to automate their home, etc. They will get a very simple GUI editor that works on all devices. 
* **Developers** – technical or enterprise users who want to build sophisticated large scale agentic applications. They will get advanced IDE and tools for debugging, observability, deploying and managing globally at scale.

### Why Amethyst
Current multi-agent frameworks are great but still too complex.
* OpenAI Agent SDK, Crew.ai, MetaGPT, etc. solve the cruicial accuracy problem, but require devs to write a lot of code. Not for consumers. *Why write Python when you can just talk to the AI?*
* Langchain offers many features, but is a bit too convoluted and unintuitive for new devs. Definitely not for consumers. *(Sorry, Langchain, you're still the OG!)*
* Zapier AI Agent editor is too simplistic, doesn't offer code-like composability or debugging.
* Lindy.ai, MS Copilot, Botpress, etc. – they all need drag-and-drop workflows which can get messy pretty fast with enterprise use-cases.

We've used several agent frameworks and tried our hand at building two frameworks here at Fask – one workflow-based and one GUI – and we still don't like what we built.

At Amazon I've been in "workflow hell" where you stare down 1000s of "stuck" workflows with complicated branchings that are so big that they don't fit your GUI editor. You can't refactor them or test them. A small change can cause even worse downstream issues which you may find out weeks later. 🤮

We prefer composable code over GUI workflows. Primitive building `blocks` are much easier to test, maintain and scale. They can be used to compose composite `blocks` – i.e., applications – which are also easy to test, maintain and scale. *`blocks` all the way down!*

Composition uses abstractions. Good abstractions help us build complexity without making things complicated. 

Amethyst is the better solution for agent development. Its no-code for non-tech users, its language is literally plain English, is composable like Ruby and Python (without workflows), and performs powerful tasks under the hood, such as async processing and managing multiple agents.

### **Amethyst Language**

#### **Agent 1 – day planner**

File `day planner.amt`

```
agent day planner
plan a day depending on the weather
use get weather to check forecast
if weather is sunny then
use all trails to find hikes distance under 10k, view scenic
else
use open table to find restaurant cuisine pnw, location waterfront
end if

a: in parallel use browser to book parking
b: in parallel use todoist to plan todo packing list
wait for a, b

use email to send plan final
end agent
```

##### **Explanation**

* **agent** (instructions) — A block telling the AI agent what to do.
* **tools** — `get weather` is a tool.
* **agents** — `all trails`, `open table` are agents from AllTrails and OpenTable. `browser` automates web tasks; `email` sends messages; `todoist` manages to-dos.
* **execution** — The entire block is executed by the Amethyst orchestrator agent.

##### **Notes**

* **Labels** — Tasks like `a:` and `b:` are used to mark parallel or async actions. Labels begin before keywords and can be waited on using `wait for a, b`.
* **Parallel** — For single-line statements, `in parallel` is sufficient (no `start` or `end` needed). Use `start in parallel ... end parallel` only for multi-paragraph parallel actions.
* **Natural control flow** — Use natural words: `if`, `else`, `repeat`, `end if`.
* **No symbols or quotes** — Everything reads as plain English.

#### **Agent 2 – all trails**

```
agent all trails
use find trails to search description hike, distance under 10k, elevation moderate
use all trails verifier to verify trail match length, elevation gain, description lookout views
end agent
```

##### **Agent 2.1 – all trails verifier (optional)**

```
agent all trails verifier
verify that trail matches metrics length, elevation gain, description lookout views
end agent
```

This shows how multiple agents can work together for verification — useful for enterprise tasks like auditing or QA.

> 🔮 *Future:* Amethyst will abstract this multi-agent madness, so users won’t have to define cross-checking logic explicitly.

Use the new agent naturally in chat (Casual Language):

```
plan my saturday using day planner
```

Or execute the code in `1-click` right from the Amethyst IDE.

That's it! Amethyst agents will automatically handle the workflow and deliver results (e.g., an email with your final plan).

#### Under the Hood

`.amt` files are compiled into Python. The compiler orchestrates agent interactions, tools, and environment actions.

> 🧐 *Why not Ruby?* Python’s LLM and agent ecosystem is mature. The goal isn’t to mimic Ruby syntax but to achieve Ruby-like simplicity and readability.

#### Environments

Each agent runs in an **environment** such as MacOS, iOS, Browser, Docker, or Raspberry Pi. You can extend environments to create your own.

You can define tools, agents, functions and objects (analogous to classes) in `.amt` (amethyst) files:

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

#### Imports and External Resources

You can import external **agents**, **tools**, **models**, or **libraries** directly from the global Amethyst registry. Think of this as defining a `package.json` file in JS/TS. Amethyst will provide a package manager, similar to `npm` or `pip`.

* **No code**: Use the GUI IDE to browse, select and OAuth the tools and agents from a global repo.
* **Low code**: Imports are written in natural English using the canonical `use <type> <name> from <source>` pattern. Set the API keys in `.env`.

Examples:

```
use agent browse from perplexity ai
use tool get weather from open weather
use model GPT-4o from openai, temperature 0.3
use library finance utils from acme corp
```

* **use** introduces a dependency.
* **type** can be `agent`, `tool`, `model`, or `library`.
* **name** is the identifier for that resource.
* **from** defines the source (organization, company, or registry).
* Optional configuration follows as natural phrases or comma-separated arguments.

Example file:

```
agent campsite finder
use agent browse from perplexity ai
use model GPT-4o from openai, temperature 0.3
find campsites nearby using browse
end agent
```

These imported resources may run locally or remotely (using **MCP** and **A2A** protocols). 

You can also configure the LLM model per agent (GPT-4o, etc.).

campsite_finder.amt:
```
agent campsite_finder
use agent perplexity browse # third party agent
use model openai GPT-4o # model
find campsites nearby using agent
end agent
```

Environments determine available tools and agents (e.g., browsers can’t run on Raspberry Pi). The compiler raises errors for incompatible contexts.

Agents or tools may pause for user input (e.g., login, captcha). Amethyst resumes automatically once resolved.

#### **Bundled Resources**

Amethyst includes common agents and tools such as:

* `swe` — Software engineer agent
* `date time` — Date and time tool
* `browser`, `email`, `todoist`

These are available out of the box for rapid prototyping.

#### Formal and Casual Langs

Amethyst Formal Language (AFL) is designed to feel human — one canonical, readable way to instruct intelligent agents.

Amethyst Casual Language (ACL) is designed to feel even more casual — it doesn't require any syntax or grammar. The IDE will convert ACL to AFL.

### Coming Soon
As with any programming language there will be more docs and features aound:
* Error handling. By default Amethyst errors will be thrown with full details up the stack. Agents may try/catch them.
* Testing (tools, tasks, agents).
* Details on how to publish packages and importing from external repos.
* Looping: `Do until` condition is met within agents. *P.S. Aren't agents just big while loops with unreadable code?*
* Debugging agents – Amethyst IDE will provide breakpoints where you can step through each line of code or a whole `block`.
* Seamless code gen – Just type or talk freely, and the IDE will automatically edit-in syntaxes, correct tool and agent names.
* Deploying, monitoring, scaling.

Advanced agentic features coming soon (ish):
* Inputs and triggers – what starts an agent? API call, webhook, etc.
* Chat with amethyst – instead of writing .amt files, just send a message (`block` of amethyst code) and the agent will execute it.
* Live multimodal agents - Agents that run continuously and can see, hear and read by processing a stream of data (audio, video, XR, streaming text).

Now, this is where it gets more interesting:

* Dynamic `blocks`: Agents will be able to produce dynamic `blocks` from streaming input which will be executed by Amethyst at runtime. For example:
  * A video agent looking at a live security footage may produce blocks like `intruder alert, invoking @alarm_agent`, depending on what they see. The block will be executed at run time, thus enabling the agent to dynamically invoke another agents and tools.
  * The agent can also send dynamic blocks explicitly to other sub-agents for post-processing and verification. `@assistant_agent, double check @block`
  * Of course, the dynamic `blocks` will be logged for debugging. We're not insane.
* Fine-tuning: Live agents can be fine tuned to produce desired dynamic blocks (they're like thoughts). For example, the security agent can be fine tuned to raise alert only when someone unknown gets inside the property, and ignore known faces.

Agents calling agents calling agents in a big recursive agentic web! Now're we're on our way to digital superintelligence.