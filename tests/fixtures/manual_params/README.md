# Official PDF regression inputs

Three original, unmodified Mi Home introduction PDFs. `sources.json` records
source endpoint, full CDN URL and SHA-256. Tests run Poppler `pdftotext -layout`
on these actual binaries; the asserted page is the one-based physical PDF page,
which may differ from printed page numbers or contain two facing printed pages.
No OCR, generated PDF, or inferred numeric fixture is used.
