## Failure Attribution

10/80 trials failed.
- Description confusion: 0 (0%)
- Author-clarifiable arguments: 9 (90%)
- Model output mechanics: 1 (10%)
- Correct deprecated-tool avoidance: 2 (excluded above — the model routed away from a tool the catalog itself says not to use)

## Mechanics Floor

0/80 trial(s) failed for reasons no description edit can change: 0 malformed/duplicated argument JSON, 0 called a tool name that isn't in the catalog.

## Confusion Matrix

| Intended \ Called | add_note | create_contact | delete_contact | get_contact | list_contacts | search_contacts | send_email | update_contact | (no call) |
|---|---|---|---|---|---|---|---|---|---|
| add_note | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_contact | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| delete_contact | 0 | 0 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| get_contact | 0 | 0 | 0 | 8 | 0 | 2 | 0 | 0 | 0 |
| list_contacts | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 3 |
| search_contacts | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| send_email | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 2 |
| update_contact | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 1 |

## Trial Diversity
- add_note: 10/10 distinct
- create_contact: 10/10 distinct
- delete_contact: 10/10 distinct
- get_contact: 10/10 distinct
- list_contacts: 8/10 distinct (some seeds sampled identical arguments)
- search_contacts: 10/10 distinct
- send_email: 10/10 distinct
- update_contact: 10/10 distinct

## Pass Rates
- add_note: 10/10 (100%), 95% CI [72%, 100%]
- create_contact: 9/10 (90%), 95% CI [60%, 98%]
- delete_contact: 10/10 (100%), 95% CI [72%, 100%]
- get_contact: 8/10 (80%), 95% CI [49%, 94%]
- list_contacts: 7/10 (70%), 95% CI [40%, 89%]
- search_contacts: 10/10 (100%), 95% CI [72%, 100%]
- send_email: 7/10 (70%), 95% CI [40%, 89%]
- update_contact: 7/10 (70%), 95% CI [40%, 89%]

## Preconditions (observed)

Tools the model called *before* correctly calling the intended one, per trial:

- get_contact → delete_contact: 1/10 trials

```mermaid
graph LR
  t0["get_contact"]
  t1["delete_contact"]
  t0 -->|1/10| t1
```

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- create_contact: address wrong 1/10
- send_email: body wrong 1/10
- update_contact: full_name extra 2/10

## No-Call Replies

- list_contacts (seed 2, refused): I don't have a way to pull a truly unfiltered list — the `list_contacts` tool requires a `status` filter and only accepts one of three values: **lead**, **customer**, or **churned**. There's no "all statuses" option available to me. Here's…
- list_contacts (seed 5, refused): I don't have a way to pull a truly unfiltered list — the `list_contacts` tool requires a `status` filter and only accepts one of three values: **lead**, **customer**, or **churned**. There's no "all statuses" option available to me. Here's…
- list_contacts (seed 6, refused): I don't have a way to pull a truly unfiltered list — the `list_contacts` tool requires a `status` filter and only accepts one of three values: **lead**, **customer**, or **churned**. There's no "all statuses" option available to me. Here's…
- send_email (seed 7, asked): I can't schedule the email as requested because the send_at value "sample-send_at-75" isn't a valid date-time — the field requires an ISO 8601 format (e.g., "2025-06-15T14:30:00Z"). Could you provide a valid date/time for scheduling? Alter…
- send_email (seed 8, other): The value provided for the scheduled send time — "sample-send_at-722" — isn't a valid date-time format. To schedule this email, I need a proper timestamp, for example: `2025-06-15T14:30:00Z` (ISO 8601 format). Could you provide the actual …
- update_contact (seed 2, refused): I wasn't able to complete this request as specified. Looking at the `update_contact` tool available to me, it only supports updating these fields: - `full_name` - `company` There is no parameter for updating a phone number, so I'm unable t…

## Solvability Warnings
- update_contact (seed 1, passed anyway, after 2 regeneration(s)): The request asks to "update" the contact but with no actual changes specified, so it's unclear whether the assistant should call update_contact (with no-op/empty changes) or simply not call any tool since no real update is being made.
- get_contact (seed 4, passed anyway, after 2 regeneration(s)): Both get_contact and search_contacts (recommended replacement) can fetch a contact by ID, so it's unclear which one the assistant should use.
- search_contacts (seed 1, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could plausibly fulfill a search/filter request, so it's unclear which one tool should be called (and get_contact's deprecation note explicitly suggests search_contacts, adding further overlap).
- search_contacts (seed 2, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described as finding contacts, so it's unclear which one should be used to fulfill the search request.
- search_contacts (seed 3, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as tools to "Find contacts," making it unclear which one should be used for this query.
- search_contacts (seed 4, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described as finding contacts, so it's unclear which one should be called for this query-matching request.
- search_contacts (seed 6, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as tools to "Find contacts," so it's unclear which one should be called to look up the entry matching "sample-query-813".
- search_contacts (seed 7, passed anyway, after 2 regeneration(s)): There are two overlapping tools, search_contacts and list_contacts, both described as "Find contacts," so it's unclear which single tool should be called to search for the matching contact.
- search_contacts (seed 8, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described identically as "Find contacts," so it's unclear which one should handle the query-matching search.
- search_contacts (seed 9, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which one should be used to fulfill the search request.
- search_contacts (seed 10, passed anyway, after 2 regeneration(s)): Two overlapping tools (search_contacts and list_contacts) can both find contacts matching a query, so it's unclear which single tool should be called.
- list_contacts (seed 1, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can find contacts matching the "leads" criteria, so it's unclear which of the two is the intended single tool to call.
- list_contacts (seed 2, failed, after 2 regeneration(s)): Both "list_contacts" and "search_contacts" are described as finding contacts, so it's unclear which one to use for retrieving the full unfiltered list.
- list_contacts (seed 3, passed anyway, after 2 regeneration(s)): There are two overlapping tools (search_contacts and list_contacts) that could both be used to find churned contacts, so it's not clear which single tool should be called.
- list_contacts (seed 4, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts with status "lead", so it's unclear which one the assistant should call.
- list_contacts (seed 5, failed, after 2 regeneration(s)): Both "list_contacts" and "search_contacts" are described as finding contacts, so it's unclear which one to use for retrieving the full unfiltered list.
- list_contacts (seed 6, failed, after 2 regeneration(s)): Both "list_contacts" and "search_contacts" are described as finding contacts, so it's unclear which one to use for retrieving the full unfiltered list.
- list_contacts (seed 7, passed anyway, after 2 regeneration(s)): There are two overlapping tools (search_contacts and list_contacts) both described as "Find contacts," so it's unclear which one should be used for this request.
- list_contacts (seed 8, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can "find contacts," so it's unclear which one should be used to pull up the first 91 customer contacts.
- list_contacts (seed 9, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts filtered by "customer" role, so it's unclear which one tool applies.
- list_contacts (seed 10, passed anyway, after 2 regeneration(s)): Both list_contacts and search_contacts can retrieve contacts, and since the user wants a plain listing without search criteria, it's unclear whether to use list_contacts or search_contacts (with empty/default parameters) to fulfill the request.

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
