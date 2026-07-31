<div align="center">

<img src="assets/build-with-gemini-banner.png" alt="Build with Gemini" width="100%" />

</div>

# Build with Gemini · Track 3

Starter kit for the **Build with Gemini** (Gemini World Tour, Track 3) lab. Clone it, open [Antigravity](https://antigravity.google), and go from an empty folder to a deployed, agent-first application on Google Cloud.

> 📖 **New here? Start with the lab guide → https://cszhu.github.io/build-with-gemini/**
>
> This repo is the companion starter kit the guide tells you to clone. It ships the Antigravity **skills** and **tool config** that make the lab work.

## 🚀 What you'll build

The lab walks you through turning a bare chatbot into a full agentic app, one capability at a time:

- **Memory & sessions** so your agent remembers users across conversations (Agent Platform Memory Bank)
- **Function tools** so it takes real actions and looks up real data
- **Persistent storage** in Firestore (structured data) and Cloud Storage (images and files)
- **RAG** to ground answers on your own documents
- **Image generation** with Gemini
- **A code sandbox** for safely running model-written code
- **Rich UI** replies with A2UI cards
- **A web frontend** on Cloud Run, plus a shareable demo video

You build all of it with Antigravity, then deploy the agent to [Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform) and the frontend to [Cloud Run](https://cloud.google.com/run).

## ✅ Prerequisites

The lab workstation comes with all of this pre-installed. To run it on your own machine you'll need:

- A **Google Cloud project** with billing enabled
- **[Antigravity](https://antigravity.google)** (`agy`), the coding agent that loads the skills below
- **[agents-cli](https://google.github.io/agents-cli/guide/getting-started/)**, Google's agent-development CLI, built on the [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Authenticated gcloud: `gcloud auth login` and `gcloud auth application-default login`
- A personal **GitHub account** for the final publish-and-submit step

## ⚡ Quickstart

```bash
git clone https://github.com/cszhu/build-with-gemini
cd build-with-gemini
agy
```

On startup, Antigravity scans the `.agents/` folder and loads the workshop skills and tools automatically. In the AGY prompt:

```text
/skills            # see the installed skills
/mcp               # confirm the firebase + google-developer-knowledge tools are connected
Verify my setup.   # runs the troubleshoot-lab-setup skill to check your environment
```

Then follow the [lab guide](https://cszhu.github.io/build-with-gemini/) to build, deploy, and share your agent.

## 🧠 What's in this repo

The repo is a single `.agents/` folder that teaches Antigravity how to build agents on Google Cloud.

### Skills

A **skill** is a bundle of instructions that loads automatically when it's relevant, so the agent gets the workflow right in fewer steps instead of rediscovering it each time.

| Skill | What it does |
| --- | --- |
| [`pick-your-agent-project`](.agents/skills/pick-your-agent-project/SKILL.md) | Brainstorm your app idea and write a project brief |
| [`troubleshoot-lab-setup`](.agents/skills/troubleshoot-lab-setup/SKILL.md) | Verify your environment and fix common setup errors |
| [`rag-engine-setup`](.agents/skills/build-rag/SKILL.md) | Ground your agent on documents with a serverless Vertex AI RAG corpus |
| [`enable-a2ui`](.agents/skills/enable-a2ui/SKILL.md) | Make your agent reply with rich UI cards (A2UI) in the ADK dev UI |
| [`build-agent-frontend`](.agents/skills/build-agent-frontend/SKILL.md) | Generate a FastAPI chat frontend and ship it to Cloud Run |
| [`record-demo`](.agents/skills/record-demo/SKILL.md) | Record a branded demo video of your agent, with an optional AI soundtrack |
| [`publish-to-github`](.agents/skills/publish-to-github/SKILL.md) | Publish your finished project to your own GitHub and submit it for swag |

### Pre-configured tools (MCP)

[`.agents/mcp_config.json`](.agents/mcp_config.json) wires up two [Model Context Protocol](https://modelcontextprotocol.io/) servers that authenticate with your gcloud credentials, so the agent can look things up instead of guessing:

- **Firebase**: work directly with Firestore and other Firebase services
- **Google Developer Knowledge**: grounded access to Google's official docs (Cloud, Firebase, ADK, Agent Platform)

### Layout

```text
.agents/
├── mcp_config.json    # Firebase + Developer Knowledge MCP servers
└── skills/            # the workshop skills listed above
```

## 🏆 Project Gallery

A showcase of what workshop participants built with this lab. Every project here was built end-to-end on Google Cloud: prototyped with Antigravity and `agents-cli`, equipped with Memory, tools, storage, and RAG, deployed to Agent Platform, and given a face on Cloud Run.

Projects are added from the swag & gallery submission form after each event, so this section starts empty and fills in over time. Browse them for inspiration, or [submit your own](#-contributing) once you've published your project with the `publish-to-github` skill.

<!--
Add one entry per project, in this format:
- 🌿 **[Project Name](https://github.com/their-handle/their-repo)**: one-line description of what it does. <br/> <sub>`🗄️ Firestore` · `🎨 Image Gen` · `🪟 A2UI`, by [@handle](https://github.com/handle)</sub>

Capability tags: `🧠 Memory` · `🗄️ Firestore` · `🖼️ Storage` · `🔧 Tools` · `📖 RAG` · `🎨 Image Gen` · `🎬 Video` · `🧪 Sandbox` · `🪟 A2UI` · `🌐 Cloud Run`
-->

*No projects yet. Check back after the next event!*

## 📚 Resources

- **[Lab guide](https://cszhu.github.io/build-with-gemini/)**: the step-by-step workshop
- [Antigravity](https://antigravity.google)
- [agents-cli](https://google.github.io/agents-cli/guide/getting-started/)
- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform)

## 🤝 Contributing

**Built something?** Publish it with the `publish-to-github` skill and submit it through the form it gives you. Submissions get you swag, and standout projects get added to the [Project Gallery](#-project-gallery) above.

**Found a bug?** If you hit a rough edge in a skill or the lab, please [open an issue](https://github.com/cszhu/build-with-gemini/issues).

## 📄 License & disclaimer

This is not an officially supported Google product and is provided for the Build with Gemini workshop for demonstration purposes only.
