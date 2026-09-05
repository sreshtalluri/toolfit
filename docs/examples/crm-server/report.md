## Confusion Matrix

| Intended \ Called | add_note | create_contact | delete_contact | get_contact | list_contacts | search_contacts | send_email | update_contact | (no call) |
|---|---|---|---|---|---|---|---|---|---|
| add_note | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| create_contact | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| delete_contact | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| get_contact | 0 | 0 | 0 | 7 | 0 | 3 | 0 | 0 | 0 |
| list_contacts | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 |
| search_contacts | 0 | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| send_email | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 2 |
| update_contact | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 8 | 1 |

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
- create_contact: 8/10 (80%), 95% CI [49%, 94%]
- delete_contact: 10/10 (100%), 95% CI [72%, 100%]
- get_contact: 7/10 (70%), 95% CI [40%, 89%]
- list_contacts: 10/10 (100%), 95% CI [72%, 100%]
- search_contacts: 8/10 (80%), 95% CI [49%, 94%]
- send_email: 7/10 (70%), 95% CI [40%, 89%]
- update_contact: 5/10 (50%), 95% CI [24%, 76%]

## Solvability Warnings
- update_contact (seed 1): The request doesn't specify what "latest information" to update, so the update_contact call lacks the necessary field values/parameters needed to execute it.
- get_contact (seed 1): Both get_contact and search_contacts can fetch a contact by ID, and since get_contact is deprecated in favor of search_contacts, it's unclear which one the assistant should actually use.
- get_contact (seed 2): Both get_contact and search_contacts (using the id) could fetch the contact details, and get_contact is explicitly marked deprecated in favor of search_contacts, so it's unclear which one the assistant should use.
- get_contact (seed 3): Both get_contact and search_contacts (using the id) could fulfill this request, since get_contact is explicitly deprecated in favor of search_contacts for the same purpose.
- get_contact (seed 4): Both get_contact (matching the direct "fetch one contact by id" purpose) and search_contacts (explicitly recommended as its replacement for looking up by id) could be used, so it's not clear which single tool should be called.
- get_contact (seed 5): Both get_contact and search_contacts (using the id) could fulfill this request, and get_contact is explicitly marked deprecated in favor of search_contacts, leaving it unclear which single tool should be called.
- get_contact (seed 6): Both get_contact and search_contacts (which is explicitly recommended as its replacement) can fetch a contact by ID, so it's unclear which single tool should be used.
- get_contact (seed 7): Both get_contact and search_contacts could fetch the contact by ID, and since get_contact is explicitly deprecated in favor of search_contacts, it's unclear which one the assistant should use.
- get_contact (seed 8): Both get_contact and search_contacts can retrieve a contact by ID, and since get_contact is explicitly marked deprecated in favor of search_contacts, it's unclear which one the assistant should actually call.
- get_contact (seed 9): Both get_contact and search_contacts (with the id) could fulfill this request, and since get_contact is explicitly deprecated in favor of search_contacts, it's unclear which one the assistant should actually call.
- get_contact (seed 10): Both get_contact and search_contacts (recommended replacement) can fetch a contact by ID, so it's unclear which one should be used.
- search_contacts (seed 1): Both "search_contacts" and "list_contacts" are described as finding contacts, so it's unclear which single tool should be used to fulfill the request.
- search_contacts (seed 2): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which one is the intended tool for this query.
- search_contacts (seed 3): Both search_contacts and list_contacts are described as tools to "Find contacts," so it's unclear which one should be used for the lookup.
- search_contacts (seed 4): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which single tool should be called to fulfill the search request.
- search_contacts (seed 5): Both search_contacts and list_contacts could fulfill this request, so it's unclear which single tool to call.
- search_contacts (seed 6): Both search_contacts and list_contacts are described as tools to "find contacts," so it's unclear which one should be used for the query.
- search_contacts (seed 7): Both "search_contacts" and "list_contacts" are described identically as tools to "Find contacts," so it's unclear which one should handle the lookup request.
- search_contacts (seed 8): Both "search_contacts" and "list_contacts" are described identically as tools to find contacts, so it's unclear which one should be called.
- search_contacts (seed 9): Both search_contacts and list_contacts are described as tools to "find contacts," so it's unclear which single tool should be used for the lookup.
- search_contacts (seed 10): Both search_contacts and list_contacts can find contacts matching a query, so it's unclear which single tool should be called.
- list_contacts (seed 1): Both search_contacts and list_contacts are described identically as "Find contacts," so it's unclear which one should be called to filter leads and limit to 64.
- list_contacts (seed 2): Both "search_contacts" and "list_contacts" are described identically ("Find contacts."), so it's unclear which one tool should retrieve the user's contact list.
- list_contacts (seed 3): There are two overlapping tools (search_contacts and list_contacts) that could both be used to find contacts matching a "churned" filter, so it's not clear which single tool to call.
- list_contacts (seed 4): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which one should be used to filter contacts by lead status.
- list_contacts (seed 5): Both "search_contacts" and "list_contacts" are described identically ("Find contacts."), so it's unclear which one tool should retrieve the user's contact list.
- list_contacts (seed 6): Both "search_contacts" and "list_contacts" are described identically ("Find contacts."), so it's unclear which one tool should retrieve the user's contact list.
- list_contacts (seed 7): Both search_contacts and list_contacts can find contacts by lead status, so it's unclear which one should be called.
- list_contacts (seed 8): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so there's no clear way to determine which single tool should be called for this filtering/listing request.
- list_contacts (seed 9): Both "search_contacts" and "list_contacts" are described identically as "Find contacts," so it's unclear which single tool should be used to fulfill the filtering/listing request.
- list_contacts (seed 10): Both "list_contacts" and "search_contacts" are described as finding contacts, so it's unclear which single tool should be used to pull up the first 74 contacts.
- send_email (seed 9): The request mixes "update" language with email-specific fields (subject, body, scheduled send), making it unclear whether to call update_contact or send_email.
- send_email (seed 10): The request mixes "update" wording with email-specific fields (subject, body, scheduled send_at), making it unclear whether to call update_contact or send_email.

## Metadata
- Model under test: claude-sonnet-5
- Generator model: claude-sonnet-5
- Seeds per tool: 10

## Mutation Results

### search_contacts
- New description: 'Full-text search across contacts by name, email or company; returns up to limit matches.'
- Before: 8/10 (80%), 95% CI [49%, 94%]
- After:  10/10 (100%), 95% CI [72%, 100%]
- p-value: 0.2500
- Verdict (Bonferroni-corrected): not significant

## Proposed Fixes

### update_contact — REJECTED
- Before: 'Update contact.'
- After:  "Update an existing contact's stored details by specifying its contact_id, optionally changing full_name and/or company, without creating, fetching, searching, listing, deleting, emailing, or adding notes to the contact."
- Pass rate: 5/10 → 4/10, p-value 1.0000
- Reason: rejected: made things worse

### search_contacts — REJECTED
- Before: 'Find contacts.'
- After:  'Search for existing contacts whose fields match a given text query, returning up to an optional limit of results, unlike get_contact (which fetches a single contact by its id) or list_contacts (which browses/lists contacts rather than matching a query).'
- Pass rate: 8/10 → 9/10, p-value 0.5000
- Reason: rejected: improvement not significant after correction (p=0.500 vs corrected α=0.0125)

### send_email — REJECTED
- Before: 'Send an email to the contact, optionally scheduled for a later send_at time.'
- After:  'Sends an email (with required subject and body) to an existing contact identified by contact_id, optionally deferring delivery until the specified send_at time instead of sending immediately.'
- Pass rate: 7/10 → 5/10, p-value 1.0000
- Reason: rejected: made things worse
