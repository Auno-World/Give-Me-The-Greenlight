# Browser Checks For Version 1.1

Checked in headless Chromium at 1280px and 390px. The four comparison screenshots are in [`docs/v1.1`](../docs/v1.1/). The sample review's walkthrough retains its layout. The response preview grows when the new draft notice is shown, as intended.

| Fix | Steps | Result |
| --- | --- | --- |
| Safe imports and embedding | Open the Builder; import an HTML file whose review block contains a function call; then import review text containing `</script><img src=x onerror=alert(1)><!--`. Check the preview and generated HTML. | The import shows the existing no-review message. The review text appears as text. No injected image or script runs, and the browser reports no page errors. The preview iframe has script permission without same-origin permission and cannot use browser storage. |
| Completion rules | Copy with no answers; answer every question, choose Approve, and enter a name; then set one answer to Needs A Change. | The blank response starts with `DRAFT: Not A Sign Off`. A complete consistent response has no draft line. Approve with Needs A Change shows the amber inline note and stays a draft until General Comments is filled. The blank PDF also starts with the draft line. |
| Answer identity | Open two reviews with the same name and revision but different review IDs. Answer one, reorder its questions, and change one question's text in another copy. | Answers stay separate by review ID, follow question IDs after reordering, and disappear when content changes. A version 1.0 review without IDs still reads its old answer key. |
| Reliable saving | Block browser storage writes, then edit answers and a Builder draft. Make a Builder draft larger than 4 MB and download its backup. | Both pages show inline save warnings. The Builder shows the size warning and downloads JSON backup. |
| Navigation and validation | Open a review without a full-document link, inspect page labels, then set total pages and a valid web link. Enter an invalid page in the Builder. | The button says Open: First Change without a link. Page labels use total pages only when provided. The Builder lists the invalid page and blocks review download. |
| Print | Print a completed review containing a comment using Chromium, then inspect extracted PDF text and print CSS. | PDF includes title, summary, all five changes, answer and comment, name, decision, and General Comments. Wallpaper, picker, and buttons are hidden. |

Safari and Playwright WebKit were unavailable in this cloud machine, so print was checked in Chromium only.
