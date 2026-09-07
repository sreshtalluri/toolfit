## Confusion Matrix

| Intended \ Called | add_note | create_contact | delete_contact | get_contact | list_contacts | search_contacts | send_email | update_contact | (no call) |
|---|---|---|---|---|---|---|---|---|---|
| add_note | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_contact | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| delete_contact | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_contact | 0 | 0 | 0 | 9 | 0 | 1 | 0 | 0 | 0 |
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
- add_note: 10/10 (100%), 95% CI [72%, 100%]
- create_contact: 6/10 (60%), 95% CI [31%, 83%]
- delete_contact: 10/10 (100%), 95% CI [72%, 100%]
- get_contact: 9/10 (90%), 95% CI [60%, 98%]
- list_contacts: 9/10 (90%), 95% CI [60%, 98%]
- search_contacts: 10/10 (100%), 95% CI [72%, 100%]
- send_email: 9/10 (90%), 95% CI [60%, 98%]
- update_contact: 4/10 (40%), 95% CI [17%, 69%]

## Argument Failures

Trials that reached the right tool with the wrong arguments, per parameter: `missing` = expected but not sent, `extra` = sent but not expected, `wrong` = value differs, `* malformed/duplicated argument JSON` = the argument text could not be parsed.

- create_contact: address wrong 2/10; tags extra 1/10; address extra 1/10
- list_contacts: limit extra 1/10
- update_contact: company extra 2/10; full_name extra 2/10

## No-Call Replies

- send_email (seed 10, other): I can do that. However, 'sample-send_at-212' is not a valid time format. Please provide the send time in a valid format.
- update_contact (seed 1, refused): I cannot update a contact's phone number. I can only update their company and full name.
- update_contact (seed 2, refused): I'm sorry, I cannot fulfill this request. The available tools lack the functionality to update a contact's phone number.

## Solvability Warnings
- get_contact (seed 6, passed anyway, after 2 regeneration(s)): Both get_contact and its recommended replacement search_contacts (using the id) could fulfill this request, so the single correct tool isn't clear.
- get_contact (seed 10, passed anyway, after 2 regeneration(s)): The request could be fulfilled by either get_contact (which directly matches fetching a contact by ID) or search_contacts (the recommended replacement per the deprecation note), so it's unclear which tool the assistant should use.
- search_contacts (seed 1, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which single tool should be called for this request.
- search_contacts (seed 2, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described as finding contacts, so it's unclear which single tool should be used for the query.
- search_contacts (seed 3, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can find contacts matching a query, so it's unclear which one tool the assistant should call.
- search_contacts (seed 4, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts matching a query, so it's unclear which single tool should be called.
- search_contacts (seed 5, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which one should handle the query-matching request.
- search_contacts (seed 6, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described as finding contacts, so it's unclear which single tool should be used to perform the search.
- search_contacts (seed 7, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which one should be called to match contacts by name.
- search_contacts (seed 10, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts matching a term, so it's not clear which single tool to call.
- list_contacts (seed 1, passed anyway, after 2 regeneration(s)): Both "search_contacts" and "list_contacts" can find contacts matching the "lead" criterion with a limit of 64, so it's unclear which tool to use.
- list_contacts (seed 2, failed, after 2 regeneration(s)): Both "list_contacts" and "search_contacts" are described identically ("Find contacts") and could return the full contacts list, so it's unclear which one to use.
- list_contacts (seed 3, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can find contacts by status, so it's unclear which of the two overlapping tools should be used to fetch churned contacts.
- list_contacts (seed 4, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts could be used to find contacts filtered by "lead" status, so it's unclear which one the assistant should call.
- list_contacts (seed 5, passed anyway, after 2 regeneration(s)): Both "list_contacts" and "search_contacts" are described identically ("Find contacts") and could return the full contacts list, so it's unclear which one to use.
- list_contacts (seed 6, passed anyway, after 2 regeneration(s)): Both "list_contacts" and "search_contacts" are described identically ("Find contacts") and could return the full contacts list, so it's unclear which one to use.
- list_contacts (seed 7, passed anyway, after 2 regeneration(s)): There are two overlapping tools (search_contacts and list_contacts) that could both be used to find contacts filtered by lead status and limited to 7, so it's unclear which one should be called.
- list_contacts (seed 8, passed anyway, after 2 regeneration(s)): Both search_contacts and list_contacts can retrieve a list of contacts, so it's unclear which of these two overlapping tools should be used to fulfill the request.
- list_contacts (seed 9, passed anyway, after 2 regeneration(s)): Both list_contacts and search_contacts could return a simple filtered list of "customer" status contacts, so it's unclear which single tool to use.
- list_contacts (seed 10, passed anyway, after 2 regeneration(s)): Both list_contacts and search_contacts (with no filters) could fetch an unfiltered list of contacts, so it's unclear which of the two "Find contacts" tools is intended.

## Metadata
- Model under test: google/gemini-2.5-flash
- Generator model: claude-sonnet-5
- Seeds per tool: 10
- Max steps per task: 3
