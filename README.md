## Amethyst

`Amethyst` is a minimalistic language and IDE to build AI agents. It optimizes human happiness by abstracting complexity. Internally, it takes care of reliability, accuracy (multiple agents) and provides enterprise level scale, so that developers don't have to write explicit code for them. It's inspired by the principles of Ruby and uses convention over configuration choices in many places to keep the developer experience simple.

### Why Amethyst
Current multi-agnet frameworks are great but still too complex.
* Crew.ai requires devs to write a lot of python code.
* Langchain is overly configurable and kind of messy.
* We prefer composable code over GUI workflows. Lindy.ai, Zapier, MS Copilot, Botpress, etc. – they all need drag-and-drop workflows which can get convoluted pretty fast for complex processes. In my experience, composable code, i.e., primitive building `blocks` are much easier to test, maintain and scale; and can be used to compose more complex applications, i.e., composite `blocks` – which are also easy to test, maintain and scale. `blocks` all the way down!


Amethyst code reads like plan english, is composable like Ruby and Python (no workflows) and does a lot of powerfull stuff under the hood, like parallel processing, multiple agents, etc.

Here's a sample "code" block:
#### Agent 1 – day_planner
File day_planner.amt:
> agent day_planner
Plan a day dependeing on the weather. Check weather from `@get_weather`. 
`If` sunny find good hikes nearby under 10K with views using `@all_trails`
`Else if` rainy find & book any nice waterfront restaurant with PNW food using `@open_table`  
`task a` Book rezos / parking if needed using `@browse_agent`. 
`task b` Plan todo, things to carry and pack using `@todoist`
`await a` `await b`
Send `@email` with the final plan
end day_planner


In this block:
* An `agent` is essentially a `block` of code (instructions). They're the same thing, and you can call them either.
* Tools:  `get_weather` is a tool.
* Agents: `all_trails`, `open_table` are agents provided by AllTrails, and OpenTable respectively. `browse_agent` is a general browser use agent that can open up the browser, navigate sites and perform actions such as book parking. `email` is an email agent that can read and send emails. `@todoist` manages todo lists.
* Syntax:
  * Typical `if`, `else` blocks used in programming.
  * `task {task_name}` is an async `block` of code. By default they're fire and forget. If used like `await task_name` the program blocks until the task is done.
  * They're all case insensitive.

#### Agent 2 – all_trails
> Find trails from description using `@find_trails`. Verify using `@all_trails_verifier`.
##### Agent 2.2 – all_trails_verifier (Optional)
> Verify that the trail matches the extact metrics such as length, elevation gain, etc., and description such as views.

Agent 2.2 shows how multiple agents can be used to review each other in a single block or task for accuracy. This is important for enterprise workflows, such as financial accounting.

And so on... (other agents not described for brevity)

Use it like this in a chat thread:

> Plan my saturday `@day_planner`

Or execute the code in `1-click` right from the Amethyst IDE.

That's it! The agents will do all the tasks, and you'll get an email with all the details for your day trip.

This seems like magic in July-2025 (at the time of writing), but I'm pretty sure this will be the obvious way to build and scale agents very soon.

#### What's Happening Under the Hood

The `block` (i.e. `agent`) is compiled by the Amethyst Compiler and is converted to Python code.

> 🤨 Note: We didn't choose Ruby for practical reasons. Python currently has extensive support for LLM and Agent ops. And let's be honest – it doesn't have to be Ruby to *feel like* Ruby. 

#### Environments
Every agent gets compiled for and is run in a specific `environment` such as `MacOS`, `iOS`, `browser`, `docker container`, `raspberry pi` etc.

You can extend environments to create your own. This is very similar to extending a docker image.

You can define tools and agents (like classes) in an application by creating/editing new `.amt` (amethyst) files:

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

When writing a class (.amt) you can import these resources like `use company_name/package_name`.
These imported resources may run locally or remotely (using **MCP** and **A2A** protocols).

You can also configure the LLM model per agent (GPT-4o, etc.).

campsite_finder.amt:
```
agent campsite_finder
use perplexity/browse_agent # third party agent
use model openai/GPT-4o # model
find campsites nearby using @browse_agent
end campsite_finder
```

Depending on the environment some agents / tools may not be compatible. E.g., you cannot run a `browse_agent` on a `raspberry pi`. The compiler should throw error if this happens.


#### Coming Soon
As with any programming language there will be more details aound:
* Testing (tools, tasks, agents)
* Details on how to publish packages and importing from external repos
* `Loop until` condition is met within agents
* Debugging agents
* Deploying, monitoring, scaling

Agent-specific features:
* Inputs and triggers - what starts an agent? Chat message (UI), API call, webhook, etc.
* Live multimodal agents - Agents that run continuously and can see, hear by processing a stream of data (audio, video, XR)
