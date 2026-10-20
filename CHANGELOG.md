# Changelog

## 1.1 (October 2026)

- Read imported reviews as JSON, escape embedded review text, and isolate the Builder preview.
- Mark incomplete or conflicting sign offs as drafts in copied and printed responses.
- Keep answers tied to a review and question IDs, with a content hash to prevent stale answers.
- Warn when browser storage fails or Builder drafts grow large, and offer a JSON draft backup.
- Correct document navigation and page labels with optional full document link and total page count.
- Check required content and image paths before producing reviews; clarify print records, retention, and privacy.
- Store answers in prototype-free maps so any question ID loads safely, and give the printed sign off record the same date fallback as the copied response.
- Note for older reviews: the Builder now opens a review only when its data block is strict JSON. Reviews made by the 1.0 Builder or Python script open as before. If you edited a 1.0 page by hand and the Builder says it has no review in it, put double quotes around every key and remove any comments in the review block, or rebuild it from `review.json`.

## 1.0 (October 2026)

First release.

- Review page: summary, page-by-page walkthrough with Zoom and Full Page, three-answer questions, sign off, Copy: My Response, Save As PDF, answers that clear after 7 days.
- Review Builder: fill in a review with a live preview and download the finished page, named after the document and revision.
- Python script: build a review from `review.json` and a folder of page images.
- AI prompt: let an AI draft `review.json` from your document.
- Every page shows its version, and each downloaded review is stamped with the version that built it.
