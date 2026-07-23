# Third-Party Integrations Catalog

This catalog is a set of optional leads, not a compatibility or security
allowlist. Every item below is **uninstalled and disabled by default**. The
zero-dependency template, validator, and FAST_INIT path do not require any of
them.

## Evidence and compatibility policy

Last catalog review: **2026-07-23**

Unless an entry is updated with stronger evidence, its **last-verified state is
"not independently verified" as of that review date**. When adopting an item,
record the verification date, tested version, target client, and official
source in project documentation; a review date alone is not compatibility
evidence.

Evidence labels describe only the link quality recorded in this repository:

- **Direct upstream**: a direct project or service URL is available. Review its
  current documentation, license, release status, data handling, and install
  instructions before use.
- **Discovery lead**: the entry uses a shortened or otherwise indirect URL.
  Treat its destination, ownership, claims, and compatibility as unverified
  until checked against an official upstream source.
- **Protocol watch**: a developing interoperability option to monitor, not a
  component of the template.

Confidence is deliberately conservative:

- **Medium** means the repository records a direct upstream URL, but no current
  cross-client smoke test is maintained here.
- **Low** means the entry is only a discovery lead or its detailed claims have
  not been independently verified.

No entry is assumed to work unchanged across Gemini, Codex, Claude, Cline, or
other agents. MCP hosts, skill discovery paths, authentication, permissions,
hook semantics, and CLI availability differ by client and version. Before
activation:

1. Resolve the official upstream documentation and pin a reviewed version.
2. Confirm support in the exact agent/client version being used.
3. Review requested filesystem, shell, network, account, and telemetry access.
4. Test in a disposable project with non-production data.
5. Document rollback and removal steps.

## 1. Developer productivity and general plugins

### [gstack](https://github.com/garrytan/gstack)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: A collection of developer-agent workflows. Verify the
  current tool count, supported agents, installation method, and commands
  upstream before adopting it.

### [superpowers](https://lnkd.in/eppbgRaK)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: A software-development methodology and skill collection.
  Resolve the official repository and verify its contents before importing any
  instructions.

### [codex-plugin-cc](https://lnkd.in/eTweEPmw)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: A claimed Codex integration. Ownership, supported
  endpoints, and the claim that it is official require upstream verification.

### [claude-skills](https://lnkd.in/eYXHrn27)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: A broad skill collection. Verify the official source,
  current inventory, license, and each imported skill; do not bulk-install
  unreviewed instructions.

## 2. Domain and vertical-specific plugins

Domain packs are advisory automation, not substitutes for qualified financial,
legal, privacy, or compliance review.

### [financial-services](https://lnkd.in/e9fpC2XF)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Finance-oriented workflows. Verify the publisher,
  jurisdictional fit, data handling, and current content before use.

### [claude-for-legal](https://lnkd.in/eYgW_QUy)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Legal-document workflows and review aids. Verify the
  source and require professional review for legal conclusions.

### [marketingskills](https://lnkd.in/egt-7ZwM)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Marketing and growth workflows. Verify the source,
  supported platforms, and any claims about included tools.

### [social-media-skills](https://lnkd.in/emDvetxm)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Social-content drafting and scheduling workflows. Review
  account permissions and require approval before publishing.

## 3. Specialized agent skills

Third-party Markdown is not automatically portable merely because an agent can
read it. Skill metadata, discovery paths, tool assumptions, and instruction
precedence vary. Import only reviewed content into the template's canonical
skill layout and test it separately in each target agent.

### [frontend-design](https://lnkd.in/eMpNx__b)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: UI-design guidance. Treat aesthetic and quality claims as
  subjective until tested against project requirements.

### [hyperframes](https://lnkd.in/ed-wSdsx)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: HTML authoring and media-rendering workflows. Verify
  runtime dependencies and output licensing.

### [ai-second-brain](https://lnkd.in/et2waZ79)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Local knowledge and history tooling. Review what data it
  stores or transmits. It must not replace the checked-in Memory Bank as the
  template's cross-agent source of truth.

### [notebooklm-skill](https://lnkd.in/edUnrPTe)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Research-source and document-query workflows. Verify
  service requirements, upload behavior, and source-citation handling.

### [humanizer](https://lnkd.in/eekWNVYm)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: User-facing prose editing. Review for unwanted meaning
  changes and do not use it to conceal required AI disclosures.

### [claude-seo](https://lnkd.in/ec5AZ_pW)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: SEO and generative-search review. Verify the source and
  benchmark recommendations against current first-party search guidance.

### [antfu-skills](https://github.com/antfu/skills)

- **Default state**: Not installed; opt-in only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: Skills that may be useful in Vue/Vite projects. Review
  individual skill contents and supported discovery layouts before importing.

### [Caveman](https://github.com/JuliusBrussee/caveman)

- **Default state**: Not installed; opt-in experiment only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: Compact response-style instructions intended to reduce
  output tokens.
- **Caveat**: Do not assume a universal savings percentage. Compression can
  remove qualifiers, paths, evidence, or safety context, and may be
  **net-negative on already-terse coding workloads**. Benchmark total session
  input/output and correctness before adoption; keep it disabled for incidents,
  security work, architecture decisions, and handoffs unless proven safe.

## 4. MCP servers and live app connections

MCP servers can expose local data or perform external writes. Each server is
**unconfigured and inactive by default**. A server supporting MCP does not mean
every host supports the same transports, authentication, approvals, or tool
schema. Use the native configuration for the selected client and require
explicit confirmation for material writes.

### [perplexity](https://lnkd.in/ejdkVnes)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Live web research. Resolve the official server, review
  query/data retention, and verify citation behavior.

### [agent-browser](https://lnkd.in/eUS4cxjs)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Browser automation for tests or audits. Review browser
  profile access, downloads, credentials, and destructive actions.

### [slack](https://lnkd.in/exz5AtNM)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Slack search or messaging. Verify the official provider,
  minimize scopes, and require confirmation before posting or modifying data.

### [notion](https://lnkd.in/e6HXirqR)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Notion workspace access. Verify the official provider,
  minimize scopes, and require confirmation before writes.

### [Zapier MCP](https://mcp.zapier.com)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: Cross-application automation. Verify current connector
  coverage and approval controls; broad account access can amplify mistakes.

### [granola](https://lnkd.in/e23ayrFh)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Discovery lead (short link) / Low.
- **Potential use**: Meeting-note ingestion. Verify consent, retention,
  workspace access, and the official integration.

### [Kondo relay](https://relay.trykondo.com/mcp)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: Claimed LinkedIn inbox access. Verify the service,
  platform-policy compliance, authentication, and write controls.

### [Higgsfield MCP](https://higgsfield.ai/mcp)

- **Default state**: Not installed or configured; opt-in only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: Media generation. Verify current MCP support, costs,
  asset rights, privacy terms, and output restrictions.

## 5. Optional performance integration

### [Headroom](https://github.com/headroomlabs-ai/headroom)

- **Default state**: Not installed; opt-in benchmark only.
- **Evidence / confidence**: Direct upstream / Medium.
- **Potential use**: A context-optimization proxy for selected workloads.
- **Caveat**: It adds a runtime/proxy dependency and may change or transmit
  prompt/tool context. Review telemetry, privacy, failure behavior, and rollback
  before testing. Do not adopt headline savings claims without measuring total
  session cost and correctness on this template.

## 6. Protocol and native-feature watch list

These are not bundled dependencies and do not replace `AGENTS.md`, MCP, skills,
workflows, or the Markdown Memory Bank:

- **ACP**: Watch as an editor-to-agent transport. Client availability does not
  establish template-wide behavior.
- **A2A**: Watch as a remote agent-to-agent transport. It is not the template's
  delegation contract or a replacement for MCP.
- **Provider-native memory**: Claude-, Gemini-, or Codex-specific memory may be
  useful as optional local recall. Treat it as advisory, verify facts against
  the repository, and never make it the only durable project state.

Adopt a watch item only after stable specifications, target-client support, a
portable fallback, and a documented conflict-resolution policy exist.

Exact statuses, first-party sources, adoption triggers, and verification dates
live in `docs/protocol-watch.md`. Optional compressor/proxy trials use
`docs/performance-experiments.md` and the local benchmark harness; none is
installed or activated by this catalog.
