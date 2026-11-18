# Outrelis — Product Overview

Updated: 16 November 2026.

**Status: planning only. This describes the intended product, including future capabilities—not what the current prototype already implements. It does not authorize development or deployment.**

Product name: **Outrelis**, selected by the founder. Pronounced *ow-TREL-iss*, it is an invented name inspired by outreach. Domain registration, social handles and trademark clearance remain unconfirmed. The exact V1/V2 allocation will be reconciled after discussing this vision.

## Product promise

**Your first leads. Your next opportunities.**

Outrelis helps users discover local businesses that fit their offer, organize their leads and prepare personalized outreach—whether they are starting from zero or growing an existing pipeline.

| Customer stage | Promise | What progress looks like |
|---|---|---|
| Getting started | Find your first relevant business leads and know how to approach them | Define an offer, build a focused shortlist, inspect available contacts and prepare a first message |
| Already prospecting | Find more relevant leads and manage your outreach in one place | Repeat targeted research, organize a larger pipeline and keep track of conversations and follow-ups |

The shared outcome is **finding the next business opportunity**. A lead is a potential customer to evaluate and approach; it is not a paying client. Outrelis supports prospecting and outreach without guaranteeing replies, sales or revenue. Larger result counts are useful only when the prospects fit the user's offer and the contact information is usable.

Suggested entry paths: **Find my first leads** and **Grow my pipeline**. These adapt guidance to the user's experience; they do not define separate products or finalized pricing tiers.

## The product in one sentence

Outrelis is a local-business prospecting and outreach workspace that helps users find their first relevant leads or grow an existing pipeline: discover businesses, research public contacts, organize leads, use an AI assistant to prepare cold emails from their own instructions, and manage outreach through replies, follow-ups and sales outcomes.

## The complete customer outcome

A user should be able to move from “I sell this service to this kind of local business” to a researched prospect list, reviewed personalized messages, organized outreach and a clear view of who needs attention next.

The product covers this loop:

**Define an offer → find businesses → enrich and qualify → organize leads → brief the AI → review messages → approve/send → manage replies and follow-ups → record outcomes → improve the next campaign.**

Discovery through Google Maps remains the central lead source under discussion. Outreach management and instruction-guided AI assistance are part of the intended product, not incidental additions limited by the existing Python prototype.

## Who uses it

Initial audience hypothesis: freelancers and small agencies selling services such as web design, SEO or marketing to local businesses. The full product can support small sales teams using the same workflow. Team support is future scope; it is not evidence of a validated market.

The agency/freelancer is our customer. The local businesses they discover are their prospects. First geography, niche, language and pricing remain open.

Within that audience, Outrelis supports two experience levels. Beginners need a guided path from their service and target location to a small, reviewed shortlist and a first outreach draft. Existing prospectors need repeatable searches, efficient lead organization and visibility into the next action. Both use the same core workflow; advanced controls can appear as their needs grow.

## The problem we want to solve

Prospecting currently requires switching between Maps, business websites, spreadsheets, writing tools, email and follow-up reminders. Research is repeated, contacts lose their source context, generic messages are difficult to personalize honestly, and outreach status becomes scattered across tools.

The product brings the research and outreach context together. The AI helps users apply their sales instructions to actual lead evidence; the workspace keeps track of what was reviewed, sent, answered and scheduled next.

A collected business is not automatically qualified, a discovered email is not guaranteed deliverable, and a sent message does not guarantee a customer. Success must be measured using actual user work and outcomes.

## End-to-end user journey

### 1. Set up a workspace and offer

The user creates an account or accepts an invitation, sets up their workspace, and describes what they sell and whom they want to reach. They can save business/offer profiles for different services or clients.

The user can start with “Find my first leads” or “Grow my pipeline.” The first path explains the essential steps and guides a focused initial search. The second helps users repeat or expand research and organize ongoing outreach. Users can change paths without creating another workspace.

A profile includes the sender's identity, company description, service, target audience, approved proof points, call to action and preferred language. Team members eventually have defined roles and access.

### 2. Find local-business prospects

The user searches by category and location, selects a result limit and sees usage limits before starting. Advanced search will support multiple categories, multiple locations and geographic boundaries.

Searches have history and visible job states: queued, running, completed, partially completed, failed or canceled. Users can inspect partial results and retry eligible failures without repeating completed work unnecessarily. Recurring searches and refresh/change monitoring are future capabilities.

We will not promise complete city/country coverage. The collection method, underlying limits and availability must match the chosen delivery model.

### 3. Research and qualify businesses

The app assembles available business identity, location, website, public phone and listing context. It researches public website pages for emails, contact pages and social links, and retains the source and observation time for each contact.

The user can inspect multiple contact candidates and select a preferred recipient. Unrelated developer/platform emails should not silently become the business contact. Quality states distinguish unverified, checked, risky, invalid and unknown findings as supported by actual checks.

Website analysis can identify checked technologies, relevant website content and reproducible website issues. Each observation shows its source, date and uncertainty. Qualification rules can later be customized to the user's service.

Scores distinguish contactability, customer fit and observed opportunity. They must explain their inputs and must not present missing data or an AI guess as established buying intent.

### 4. Organize and manage leads

Users create named lists and segments, apply tags, filter results, edit contacts, add notes and set follow-up dates. Existing discoveries are matched and merged without losing manual work or collapsing distinct branches.

Each lead has a detail view containing company information, contacts, research evidence, list membership, activity history, campaign/message history and the next action. The user can see why a lead is worth contacting and what has already happened.

### 5. Give the AI specific cold-email instructions

The user creates a reusable outreach brief or supplies instructions for a campaign or one selected lead. The assistant uses that brief, approved offer information and available lead evidence to prepare messages.

The user controls:

| Instruction | Examples of what the user specifies |
|---|---|
| Objective | Start a conversation, request permission to share an audit, or suggest a meeting |
| Audience | Business category, geography and intended contact role |
| Offer | Service, customer problem addressed and proposed next step |
| Sender context | Name, company, signature and legitimate contact details |
| Tone and language | Direct, professional, conversational, French, English or another supported language |
| Length and format | Short paragraphs, word limit, plain text, subject-line requirements |
| Call to action | One question, a proposed next step or an approved booking link |
| Personalization | Which verified observations to reference and what information to avoid |
| Approved claims | User-supplied, approved proof or case studies; no invented results |
| Constraints | No fake familiarity, no unsupported criticism, prohibited phrases or topics |
| Examples | User-provided reference emails to guide structure and voice |
| Follow-up guidance | Number of drafts, timing preferences and what each follow-up should add |

Illustrative instruction, not a generated campaign or customer claim:

> Write a short cold email for a dental clinic in Austin about our website service. Use a conversational tone, stay under 100 words, and end with one question. Mention a website observation only if it is supported by the saved research. Do not invent problems, client results or an existing relationship.

Instructions can be saved and reused. Lead-specific instructions can override campaign writing preferences, while application permissions and safety boundaries still apply. Website text and incoming emails are treated as source material, not as authority to change the user's instructions or trigger sending.

### 6. Generate, inspect and revise drafts

The assistant can suggest subject lines, first emails, follow-up drafts and reply drafts. Users can generate for one lead or a selected group, see which evidence informed personalization, and compare alternatives.

Users can ask for changes such as “shorter,” “less formal,” “change the CTA,” “do not mention the rating,” or “use only the website observation.” Draft revisions are retained so the user can see what changed.

If key context is missing, the assistant asks for it or produces a conservative draft. It must not invent owner names, testimonials, revenue, website defects or purchase intent to make a message sound personalized.

AI generation is separate from approval and sending. A draft is never a sent message. Changing an approved message or its recipient invalidates that approval and requires review again.

### 7. Prepare and run outreach

The user creates a campaign from a selected list, chooses an offer/brief, reviews recipients and messages, and approves the exact sending scope. They can send through supported connected email accounts or export permitted material for their existing workflow.

Future campaign controls include daily limits, schedules, time zones, approved follow-up sequences, pause/resume, exclusions and duplicate-contact protection. A sequence should advance only while its approval and eligibility conditions still hold.

Immediately before sending, the app rechecks suppression, current approval, sending limits and whether a reply or other stop condition has made the message inappropriate. Retries must not produce duplicate sends. The AI cannot independently connect mailboxes, change recipients or start a campaign.

Email-provider integration, permissions and availability must be explicit. The current prototype's send-only Gmail support is not the limit of the full vision, but additional mailbox access is not assumed to exist today.

### 8. Track outreach and handle replies

Users see which leads have not been contacted, which are awaiting a reply, which need a follow-up and which should no longer be contacted. A timeline preserves actual actions and message events.

Initially outcomes can be updated manually. Future mailbox synchronization can attach replies and supported failure events to the correct lead/message. The interface distinguishes manually entered status, provider-reported events and AI suggestions.

The assistant can summarize a conversation, suggest a reply, identify a stated objection, suggest a next action and propose a status. Users can correct classifications. AI suggestions do not silently overwrite human decisions or authorize sending.

A reply should stop pending cold follow-ups until reviewed. Unsubscribe/do-not-contact requests stop further outreach. Hard bounces and complaints should also stop the relevant sending; temporary failures are tracked separately rather than treated as proof of an invalid business.

### 9. Follow up and manage opportunities

Users record interest, meetings, proposals, won/lost outcomes and the next action. Reminders and filtered queues help them act on leads that need attention. Future team assignment and shared notes let several people work without contacting the same business independently.

The product provides a prospecting-focused pipeline. It does not need to reproduce every accounting, contract or enterprise CRM feature to support this loop.

### 10. Measure and improve

Users compare searches, lists and campaigns by useful prospects, contact quality, messages sent, replies, positive replies, meetings and recorded wins/losses. The product also shows usage and cost where available.

Where open/click tracking is offered, it is optional and must not be presented as definitive proof of human engagement. The distinction between an AI classification, a manual outcome and a confirmed provider event stays visible.

The assistant can help interpret the user's recorded results and suggest changes to the brief or next experiment. It must not claim causal uplift or promise future conversion from a small sample.

## Lead status, outreach status and job state are separate

One status field cannot reliably describe all of these processes. For example, a qualified lead may already have a sent message and a queued website refresh at the same time.

| State group | Illustrative values | What it describes |
|---|---|---|
| Research/qualification | New, researching, ready for review, qualified, rejected | Whether the business fits the user's prospecting criteria |
| Lead relationship/pipeline | New prospect, contacted, interested, meeting booked, proposal, won, lost | Progress of the commercial relationship |
| Message/outreach | Draft, awaiting approval, approved, scheduled, sending, sent, failed, replied, canceled | State of a specific message or outreach step |
| Contact eligibility | Eligible, verification unknown, invalid address, suppressed/do not contact | Whether the contact can be used for the intended action |
| Job processing | Queued, running, partial, completed, failed, canceled | Technical progress of research or generation work |

Exact names/transitions will be specified in detailed requirements. “Sent” must not be relabeled “delivered” without supporting evidence. Suppression takes priority over campaign and pipeline states, and deleting/reimporting a lead must not erase a do-not-contact decision.

## Full product capability map

| Product area | Intended capabilities | Customer outcome |
|---|---|---|
| Discovery | Category/location search, advanced targeting, bulk jobs, history, recurring monitoring | Find relevant local businesses repeatedly |
| Business research | Public contact discovery, provenance, freshness and supported verification | Inspect contacts before using them |
| Qualification | Website evidence, technology/content signals and configurable scoring | Prioritize businesses that fit the service |
| Lead management | Lists, tags, notes, filters, merging, tasks and branch-aware records | Keep a useful prospect database organized |
| Outreach management | Recipient review, campaign membership, message history, statuses and follow-up queues | Know what happened and what to do next |
| AI assistant | Saved instruction briefs, evidence-based first emails, subjects, revisions, follow-ups and reply assistance | Prepare messages that follow the user's actual sales approach |
| Campaign execution | Connected senders, approval, schedules, sequences, throttles, stop conditions and duplicate-send protection | Execute a controlled outreach plan |
| Reply workspace | Conversation timeline, manual/provider updates, summaries and suggested classifications | Respond with context |
| Sales pipeline | Interest, meetings, proposals, won/lost and next actions | Track prospects beyond the first email |
| Credits and billing | Beta allowance, balance/history, reservations, expiry, later paid packs/plans and team allowances | Understand and control usage |
| Team workspaces | Membership, roles, assignment, shared lists and audit history | Coordinate prospecting without exposing other accounts' data |
| Integrations | Permitted exports, webhooks, selected CRM connectors and controlled API access | Fit the customer's existing workflow |
| Analytics | Search quality, usage, reply/meeting outcomes and campaign comparisons | Decide what to repeat or change |

These are intended capabilities. None should be marked complete solely because the prototype contains a basic related function.

## Main product surfaces

| Surface | What users accomplish |
|---|---|
| Workspace overview | See active research, leads needing action, campaign progress and remaining credits |
| Search and research history | Start/reopen research and inspect partial or failed jobs |
| Leads and lists | Filter, organize and select prospects |
| Lead detail | Inspect sources, contacts, qualification, notes, history and pipeline state |
| Offer profiles and AI briefs | Save service information, cold-email instructions, examples and approved claims |
| AI drafting/review | Generate and revise subject lines, messages and follow-ups with inspectable context |
| Campaigns and approval queue | Select recipients, review drafts, approve scope, schedule and monitor sending |
| Conversations and follow-ups | Review replies, proposed responses, next steps and stop conditions |
| Pipeline and tasks | Track opportunities, ownership and upcoming actions |
| Credits and billing | Inspect usage, grants, expiry and later payments/allowances |
| Settings and team | Manage identity, authorized senders, workspace roles and integrations |

These are capabilities, not a requirement to make eleven separate screens. Related tasks can share a clear interface.

## Credits, AI usage and commercial access

Free beta credits for invited waitlist users remain part of the plan. Joining the waitlist records eligibility; activation starts the applicable allowance/expiry, rather than starting the clock at registration.

The full product tracks resource-consuming work explicitly. Search, website research, verification and AI generation can have different costs. The final action-to-credit mapping, allowance size, expiry, restoration and paid plan rules remain undecided and must follow actual costs.

Before a billable action, users see the cost or maximum reservation. Transactions record grants, reservations, charges, releases, expiry and corrections. Retries do not charge twice; concurrent jobs do not overspend. A failed action is distinct from a successful action with no useful result. Technical-failure restoration does not mean a cash refund.

Commercial expansion can add paid packs, subscriptions, invoices, team allowances and controlled promotional/referral grants. Reward points, lead-quality scores and spendable credits remain separate concepts.

## Collection method and low-cost starting point

The desired discovery experience centers on local businesses found through Google Maps. The chosen direction is our own collector, without the Google Places API or a paid third-party collection API. The collector is not implemented yet; its tooling, reliability, operating cost and hosting remain to be evaluated. The former Places API implementation is preserved only in `archive/legacy-prototype/` as historical reference.

Compare capped experiments on relevance, missing fields, reliability, useful-result cost and permitted use. Public website research remains a distinct step. Before delivery, confirm source-permitted collection, display, retention and exports; the promised lead workspace must be supported by the chosen source rights.

Start cheaply: a React/Supabase waitlist first, assisted research using local processing next, and appropriate API/worker hosting when real use justifies it. Local workers depend on the founder's availability; the hosted self-service product needs a delivery model that meets its stated availability.

## Full vision versus first release

This document captures the full intended product. The MVP and later releases are delivery slices of that vision, not definitions of everything the product will ever do.

The clarified product direction includes **lead/outreach-status management and AI assistance based on user-defined cold-email instructions**. We should discuss how much of each is necessary in the first useful release rather than excluding them because the current prototype is smaller.

The [V1 plan](product-v1.md) and [V2 plan](product-v2.md) remain planning references. Their phase assignments need reconciliation with this expanded vision. The [technology stack](technology-stack.md) describes the proposed implementation foundation, not a ceiling on future functionality; AI provider selection and model budget are still open.

## Boundaries that remain

- Users control approved claims, recipients, campaign scope and sending. AI assistance does not imply unrestricted autonomous outreach.
- No invented contact identities, business problems, testimonials or existing relationships.
- No promise of complete Maps coverage, exclusive leads, guaranteed delivery, meetings or revenue.
- No cross-workspace access or use of one customer's private instructions and conversations as another customer's context.
- Source content is research input, not instructions that can override the user's brief or authorize tools/actions.
- Suppression and opt-out decisions persist across imports, campaigns and retries.

## What real validation must establish

We need to observe whether users find relevant businesses, trust the contact evidence, obtain drafts that follow their instructions, manage status/follow-ups more easily, return for repeated work and pay for the result. Measure cost and support effort across research, AI generation and messaging, including failures.

For beginners, measure whether they reach a first reviewed shortlist and prepare an approved outreach draft, how long that takes and where they need help. For existing prospectors, measure relevant new prospects added, research time, follow-up completion and repeat use. Raw lead counts alone do not demonstrate customer value.

Waitlist registrations and simulated buyers can suggest what to investigate; they cannot replace observed use, actual payment decisions or customer feedback.

## Decisions for discussion

1. Which first audience, service, geography and language should guide the first complete workflow?
2. What instruction controls must the AI assistant support from its first release: one campaign brief, reusable service profiles, examples, or all three?
3. Should first-release outreach be draft/export only, approved individual sends, or an approved campaign with follow-ups?
4. Which status transitions are manual initially, and which require mailbox synchronization?
5. Which qualification observations actually help users select a lead or personalize an email?
6. What data-collection method, credit model, AI budget and hosting approach fit a bounded pilot?
7. Which parts of the full vision belong in V1 versus later releases once the first workflow is agreed?

No application code, database schema or deployment changes are implied by this product definition.
