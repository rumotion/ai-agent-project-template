# Third-Party Integrations Catalog

This document details the recommended third-party extensions, plugins, skills, and Model Context Protocol (MCP) servers. 

To maintain the template's **strict zero-dependency core**, these tools are classified as **on-demand integrations** and are not pre-installed. You can install them when required for your project.

---

## Agent Compatibility & Interoperability

All listed tools, plugins, and MCP servers are compatible across various AI coding agents. They are implemented using standardized formats:

1. **Model Context Protocol (MCP) Servers** (e.g., Perplexity, Slack, Notion, Zapier, Agent-Browser):
   - **Claude Code**: Supported natively via server configurations in user configs.
   - **Cline / VS Code Extensions**: Supported natively via the built-in MCP configuration manager.
   - **Gemini / Google Antigravity**: Supported using standard MCP connection adapters.
   - **Codex / ChatGPT**: Supported via MCP host gateways or proxy tools.

2. **Instructional Skills & Methodology Rules** (e.g., `frontend-design`, `caveman`, `superpowers`, `claude-for-legal`):
   - Because these are structured markdown files, they are LLM-agnostic.
   - **Claude Code**: Loaded dynamically or appended to session prompts.
   - **Cline**: Copied directly into `.clinerules` or workspace instructions.
   - **Antigravity / Gemini**: Copied to `.agents/` or referenced in system prompts.
   - **Codex / ChatGPT**: Imported into custom system instructions or playground prompts.

3. **CLI & Shell-Based Tools** (e.g., `gstack`):
   - Standard shell utilities that run directly on the host system. Any agent with shell execution capabilities can run these tools natively.

---

## 1. Developer Productivity & General Plugins
These plugins enhance agent capabilities with prepackaged tools, commands, or methodologies.

### [gstack](https://github.com/garrytan/gstack)
- **What it is**: 23 specialist developer tools bundled into a single installation.
- **When to use**: To give your agent robust git workflows, code refactoring support, and diagnostics.
- **Activation**: Run `npm install -g gstack` or load it via agent configuration.

### [superpowers](https://lnkd.in/eppbgRaK)
- **What it is**: A complete software development methodology containing 14 skills.
- **When to use**: For complex projects needing disciplined planning, testing, and implementation cycles.
- **Activation**: Follow installation steps at [superpowers](https://lnkd.in/eppbgRaK).

### [codex-plugin-cc](https://lnkd.in/eTweEPmw)
- **What it is**: OpenAI's official Codex integration plugin.
- **When to use**: When utilizing Codex models or legacy OpenAI endpoints.
- **Activation**: Configure via plugin settings.

### [claude-skills](https://lnkd.in/eYXHrn27)
- **What it is**: 263+ skills covering a wide array of platforms and APIs.
- **When to use**: When you need a generic, swiss-army-knife set of tools for system management.
- **Activation**: See instructions at [claude-skills](https://lnkd.in/eYXHrn27).

---

## 2. Domain & Vertical-Specific Plugins
These should only be loaded when building apps in specific industries.

### [financial-services](https://lnkd.in/e9fpC2XF)
- **What it is**: Workflows and integrations tailored for Investment Banking, Private Equity, and Wealth Management.
- **Activation**: Load the schema/instructions when building fintech/finance systems.

### [claude-for-legal](https://lnkd.in/eYgW_QUy)
- **What it is**: Workflows, citation parsers, and review gates for legal practice areas.
- **Activation**: Import target templates when dealing with legal compliance or document analysis.

### [marketingskills](https://lnkd.in/egt-7ZwM)
- **What it is**: 40 marketing tools covering growth ops, email templates, and analytics.
- **Activation**: Mount these skills when writing growth automation or marketing funnels.

### [social-media-skills](https://lnkd.in/emDvetxm)
- **What it is**: Content OS for drafting, formatting, and scheduling posts and video reels.
- **Activation**: Enable when building social integration pipelines.

---

## 3. Specialized Agent Skills
Custom instruction sets that agents load dynamically to solve specific technical problems.

### [frontend-design](https://lnkd.in/eMpNx__b)
- **What it is**: Premium UI design rules that eliminate generic, boring AI-generated interfaces.
- **When to use**: During UI development phases to enforce glassmorphism, harmonious HSL palettes, and micro-animations.

### [hyperframes](https://lnkd.in/ed-wSdsx)
- **What it is**: Agent-native HTML writing and video rendering skill.
- **When to use**: When generating dynamic media content or rich interactive prototypes.

### [ai-second-brain](https://lnkd.in/et2waZ79)
- **What it is**: Karpathy-style local wiki and AI memory/history parser.
- **When to use**: To keep track of deep project history and long-term knowledge across sessions.

### [notebooklm-skill](https://lnkd.in/edUnrPTe)
- **What it is**: Skill optimized for querying research sources and documents.
- **When to use**: When onboarding complex academic papers or massive PDFs.

### [humanizer](https://lnkd.in/eekWNVYm)
- **What it is**: Text style modifier that strips typical AI writing tells.
- **When to use**: Generating user-facing docs, copy, or markdown explanations.

### [claude-seo](https://lnkd.in/ec5AZ_pW)
- **What it is**: GEO-first (Generative Engine Optimization) SEO audit skill.
- **When to use**: Optimizing web landing pages for search engines and AI answer engines.

### [antfu-skills](https://github.com/antfu/skills)
- **What it is**: Skills designed by Vue/Vite core team members.
- **When to use**: When developing projects on the Vue/Vite stack.

### [caveman](https://lnkd.in/e4nxpEJi)
- **What it is**: Token-saving instruction set that forces the agent to talk like a caveman.
- **When to use**: During fast, iterative coding rounds to cut token usage by up to 65%.

---

## 4. MCP Servers (Live System & App Connections)
Model Context Protocol (MCP) servers allow agents to safely read/write to your apps.

### [perplexity](https://lnkd.in/ejdkVnes)
- **What it is**: Live web search integration.
- **When to use**: Fetching current documentation, live package versions, or online solutions.

### [agent-browser](https://lnkd.in/eUS4cxjs)
- **What it is**: Playwright/Puppeteer-based browser automation server.
- **When to use**: Visual testing, UI audits, or scraping internal web pages.

### [slack](https://lnkd.in/exz5AtNM)
- **What it is**: Read/write slack channel context.
- **When to use**: Reporting build failures or posting task completion notifications.

### [notion](https://lnkd.in/e6HXirqR)
- **What it is**: Read/write Notion workspaces.
- **When to use**: Syncing specs or updating project wikis directly from the agent.

### [zapier](https://mcp.zapier.com)
- **What it is**: Integrates Zapier’s 9,000+ app connectors.
- **When to use**: Triggering workflows, CRM additions, or cross-app automation.

### [granola](https://lnkd.in/e23ayrFh)
- **What it is**: Meeting transcription feed.
- **When to use**: Importing meeting action items into the active project context.

### [kondo](https://relay.trykondo.com/mcp)
- **What it is**: LinkedIn DM triaging and inbox connection.
- **When to use**: Automating communication or fetching incoming business leads.

### [higgsfield](https://higgsfield.ai/mcp)
- **What it is**: Cinematic video generation from prompts.
- **When to use**: Dynamically generating visual media assets.
