## Confusion Matrix

| Intended \ Called | add_note | create_contact | delete_contact | get_contact | list_contacts | search_contacts | send_email | update_contact | (no call) |
|---|---|---|---|---|---|---|---|---|---|
| add_note | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_contact | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| delete_contact | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_contact | 0 | 0 | 0 | 6 | 0 | 1 | 0 | 0 | 3 |
| list_contacts | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 |
| search_contacts | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| send_email | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 | 1 |
| update_contact | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 2 |

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
- add_note: 8/10 (80%), 95% CI [49%, 94%]
- create_contact: 9/10 (90%), 95% CI [60%, 98%]
- delete_contact: 10/10 (100%), 95% CI [72%, 100%]
- get_contact: 6/10 (60%), 95% CI [31%, 83%]
- list_contacts: 10/10 (100%), 95% CI [72%, 100%]
- search_contacts: 10/10 (100%), 95% CI [72%, 100%]
- send_email: 9/10 (90%), 95% CI [60%, 98%]
- update_contact: 6/10 (60%), 95% CI [31%, 83%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- add_note: body wrong 2/10; pinned missing 1/10
- create_contact: address wrong 1/10
- update_contact: contact_id wrong 2/10

## No-Call Replies

- get_contact (seed 7, other): ```json [ "get_contact(contact_id='sample-contact_id-332')" ] ```
- get_contact (seed 8, other): ```python [get_contact(contact_id='sample-contact_id-233')] ```
- get_contact (seed 10, refused): I am unable to directly fulfill this request. The `get_contact` function is deprecated and the documentation recommends using `search_contacts` instead. I do not have the functionality to directly "look up the full details...exactly as sto…
- send_email (seed 8, other): ```python [send_email(contact_id='sample-contact_id-233', subject='sample-subject-380', body='sample-body-986', send_at='sample-send_at-722')] ```
- update_contact (seed 1, other): I lack the parameters required to fulfill this request. The `update_contact` function requires a `contact_id`, `full_name`, and `company`. I only have the `contact_id`. I need the new `full_name` and `company` values.
- update_contact (seed 2, other): I lack the parameters required to fulfill this request. The `update_contact` function requires a `contact_id`, `full_name`, and/or `company`. While the `contact_id` is provided, `full_name` and `company` are optional and have a default val…

## Solvability Warnings
- get_contact (seed 3, passed anyway, after 2 regeneration(s)): The request could be fulfilled by the deprecated get_contact or by search_contacts with the id (as explicitly recommended), so it's unclear which single tool the assistant should call.
- get_contact (seed 4, passed anyway, after 2 regeneration(s)): Both get_contact and search_contacts (with the id) can fulfill this request, and since get_contact is explicitly deprecated in favor of search_contacts, it's unclear which single tool the assistant should use.
- get_contact (seed 5, passed anyway, after 2 regeneration(s)): Both get_contact and search_contacts (using the id) can fulfill this request, and since get_contact is explicitly deprecated in favor of search_contacts, it's unclear which single tool the assistant should call.
- get_contact (seed 8, failed, after 2 regeneration(s)): The request could be fulfilled by either get_contact (which matches "by that exact ID" but is deprecated) or search_contacts (the recommended replacement for ID lookups), so it's unclear which single tool should be called.
- search_contacts (seed 1, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described identically ("Find contacts."), so it's unclear which of the two tools should be used to fulfill the search request.
- search_contacts (seed 2, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which one the assistant should call for this search request.
- search_contacts (seed 4, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find matching contacts, so it's unclear which single tool should be called.
- search_contacts (seed 5, passed anyway, after 2 regeneration(s)): There are two overlapping tools for finding contacts (search_contacts and list_contacts) with no clear criterion for which to use, so it's not unambiguous which single tool should be called.
- search_contacts (seed 6, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described as tools to "find contacts," so it's unclear which one the assistant should use for the search request.
- search_contacts (seed 7, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described identically ("Find contacts."), so it's unclear which of the two is the intended tool for searching by query.
- search_contacts (seed 8, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described as "Find contacts," so it's unclear which one should be called to search for matching results.
- search_contacts (seed 9, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described as tools to "Find contacts," so it's unclear which one should be used for the search.
- search_contacts (seed 10, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can find contacts matching a query, so it's unclear which single tool should be called.
- list_contacts (seed 1, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically ("Find contacts.") and could fulfill filtering contacts by lead status with a limit of 64, so it's unclear which one is the intended single tool to call.
- list_contacts (seed 3, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could find contacts filtered by status "churned" with details, so it's unclear which of the two overlapping tools should be used.
- list_contacts (seed 4, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts with a "lead" status, so it's unclear which single tool should be called.
- list_contacts (seed 7, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts are described as "Find contacts," so it's unclear which tool should be used to filter contacts by "lead" status without a keyword search.
- list_contacts (seed 8, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts marked as customers, so it's unclear which single tool should be called.
- list_contacts (seed 9, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can find contacts matching a status filter with a limit, so it's unclear which of the two overlapping tools should be used.
- list_contacts (seed 10, passed anyway, after 2 regeneration(s)): Both list_contacts and search_contacts are described as "Find contacts," so it's unclear which one to use for a plain, unfiltered retrieval of 74 contacts.

## Metadata
- Model under test: google/gemma-3-27b-it
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
