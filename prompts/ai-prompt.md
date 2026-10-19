# AI Prompt: Draft A Review

Use this with any AI chat your company allows. Paste everything in the box below, then attach or paste your document. The AI writes only the review content (a small `review.json`), not the whole page, which keeps token use low.

When it's done:

1. Save the AI's answer as `review.json`.
2. Open `builder.html`, choose **Open: Existing Review**, and pick `review.json`.
3. Check every change against your real document, then choose **Download: Review**.

```text
You are helping me build a document review page. Read the document I provide and
return ONLY a JSON object, with no other text, in exactly this shape:

{
  "company": "",            // company name as written in the document
  "docType": "",            // for example Procedure, Work Instruction, Policy
  "docName": "",            // document title, plain words, no document codes
  "fromRev": "",            // current revision, or "" if this is a new document
  "toRev": "",              // new revision, for example "Rev C"
  "author": "",             // person who wrote the change, if known
  "authorRole": "",         // their team, if known
  "approverRole": "",       // leave "" unless the document names one
  "effective": "On release",
  "keepAnswersDays": 7,
  "fictional": false,
  "lede": "",               // one or two sentences: what is ready and how long the review takes
  "summary": [["What It Does", ""], ["What Changes", ""], ["Impact On ...", ""]],
  "steps": [
    "Walk each change. Tap any page to see it full size.",
    "Answer the questions and pick your decision.",
    "Copy your response or save it as a PDF, and send it back."
  ],
  "stops": [
    {
      "id": "c1",
      "section": "",        // section number or name as written
      "page": 1,
      "title": "",          // short plain-language title, Title Case
      "text": [""],         // the NEW wording, copied exactly, one string per paragraph
      "around": [],         // optional nearby text for context, copied exactly
      "look": [""],         // 2 or 3 short points: what changed and what to check
      "bottom": ""          // one sentence: why this change matters
    }
  ],
  "questions": [
    { "stop": "c1", "q": "", "why": "" }   // one decision question per important change
  ]
}

Rules:
- Copy document wording exactly in "text" and "around". Never reword it.
- Everything you write yourself uses plain language: short words, no acronyms,
  no document codes, no ticket numbers, Title Case for titles.
- No em dashes. Use commas, colons, or separate sentences.
- 3 to 6 changes, ordered as they appear in the document.
- 3 to 5 questions, each linked to a change by its id, each answerable with
  Agree, Agree With Minor Adjustments, or Needs A Change.
- If something is unclear or missing, leave the field "" rather than guessing,
  and do not invent facts.
- Return valid JSON only. No comments, no code fences, no explanation.
```

Tip: remove the `//` notes above if your AI copies them into its answer. The Builder will tell you if the file can't be opened.
