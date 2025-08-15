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
* Crew.ai, MetaGPT, etc. solve the cruicial accuracy problem, but require devs to write a lot of code. Not for consumers. *Why write Python when you can just talk to the AI?*
* Langchain offers many features, but is a bit too convoluted and unintuitive for new devs. Definitely not for consumers. *(Sorry, Langchain, you're still the OG!)*
* Zapier AI Agent editor is too simplistic, doesn't offer code-like composability or debugging.
* Lindy.ai, MS Copilot, Botpress, etc. – they all need drag-and-drop workflows which can get messy pretty fast with enterprise use-cases.

We've used several agent frameworks and tried our hand at building two frameworks here at Fask – one workflow-based and one GUI – and we still don't like what we built.

At Amazon I've been in "workflow hell" where you stare down 1000s of "stuck" workflows with complicated branchings that are so big that they don't fit your GUI editor. You can't refactor them or test them. A small change can cause even worse downstream issues which you may find out weeks later. 🤮

We prefer composable code over GUI workflows. Primitive building `blocks` are much easier to test, maintain and scale. They can be used to compose composite `blocks` – i.e., applications – which are also easy to test, maintain and scale. *`blocks` all the way down!*

Composition uses abstractions. Good abstractions help us build complexity without making things complicated. 

Amethyst is the better solution for agent development. Its no-code for non-tech users, its language is literally plain English, is composable like Ruby and Python (without workflows), and performs powerful tasks under the hood, such as async processing and managing multiple agents.

Here's a sample "code":
#### Agent 1 – day_planner
File day_planner.amt:
> agent day_planner
Plan a day dependeing on the weather. Check weather from `@get_weather`. 
`If` sunny find good hikes nearby under 10K with views using `@all_trails`
`Else if` rainy find & book any nice waterfront restaurant with PNW food using `@open_table`  
`go do a` Book rezos / parking if needed using `@browser`. 
`go do b` Plan todo, things to carry and pack using `@todoist`
`await a` `await b`
Send `@email` with the final plan
end agent


In this example:
* An `agent` is composed of a `block` of code (instructions).
* Tools:  `get_weather` is a tool.
* Agents: `all_trails`, `open_table` are agents provided by AllTrails, and OpenTable respectively. `browser` is a general browser use agent that can open up the browser, navigate sites and perform actions such as book parking. `email` is an email agent that can read and send emails. `@todoist` manages todo lists.
* The whole block will be executed by an amethyst orchestrator agent. (*It's sentient.* ;))
* Loose syntax:
  * Typical `if`, `else` blocks used in programming.
  * `go do {task_name}` is an **async** `block` of code. By default they're fire and forget. If used like `await task_name` the program blocks until the task is done.
  * They're all optional and non-rigid. Instead of "else" if you say "otherwise" the code will still work.

#### Agent 2 – all_trails
> Find trails from description using `@find_trails`. Verify using `@all_trails_verifier`.
##### Agent 2.1 – all_trails_verifier (Optional)
> Verify that the trail matches the exact metrics such as length, elevation gain, etc., and description such as "lookout views".

Agent 2.1 shows how multi-agents can be used to review each other in a single block for accuracy. This could be important for enterprise workflows, such as financial accounting. 

> 🔮 Note: We believe that in the future multi-agent madness will be abstracted, and developers won't have to do this explicitly.

And so on... (other agents not described for brevity).

Use the new agent like this in a chat thread:

> Plan my saturday `@day_planner`

Or execute the code in `1-click` right from the Amethyst IDE.

That's it! The agents will do all the tasks, and you'll get an email with all the details for your day trip.

We believe this will be the obvious way to talk to and scale agents in the near future.

#### What's Happening Under the Hood

The `.amt` file is compiled in Python. The amethyst agent will break it down into a sequence of tasks and the compiler will execute them.

> 🧐 Note: We didn't choose Ruby for practical reasons. Python currently has extensive support for LLM and Agent ops. And let's be honest – it doesn't have to be Ruby to *feel like* Ruby. 

#### Environments
Every agent gets compiled for and is run in a specific `environment` such as `MacOS`, `iOS`, `Browser`, `Docker Container`, `Raspberry Pi`, etc. You can extend environments to create your own. This is very similar to extending a docker image.

You can define tools (analogous to functions) and agents (analogous to classes) in an application by creating/editing new `.amt` (amethyst) files:

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

You can also import resources (tools and agents) from other repositories (packages). Think of this as defining a `package.json` file in JS/TS. Amethyst will provide a package manager like `npm` or `pip`.

When writing a class (.amt) you can import these resources:
* [No code] Both consumers and devs can use the GUI IDE to find and simply select the tools and agents they would like to add from a global repo. If connecting with an external app you'll have to provide OAuth permission (standard sign in flow).
* [Low code] Devs can also import via code like `use company_name/package_name` and set the API keys in `.env`.

These imported resources may run locally or remotely (using **MCP** and **A2A** protocols).

You can also configure the LLM model per agent (GPT-4o, etc.).

campsite_finder.amt:
```
agent campsite_finder
use perplexity/browse_agent # third party agent
use model openai/GPT-4o # model
find campsites nearby using @browse_agent
end agent
```

Depending on the environment some agents / tools may not be compatible. E.g., you cannot run a `browser` (agent) on a `RaspberryPi`. The compiler will throw an error if this happens.

The agent may get stuck sometimes and ask for user help, such as login or anti-AI captcha. Amethyst will make sure the program resumes from that point.

#### Bundled Resources
Amethyst will include a library of common tools and agents such as `@swe` (coder agent), `@date_time` (tool), etc. You can expect all common utilities that a programing language provides.


#### Coming Soon
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