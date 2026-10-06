# findings-analyst memory (how to do the work only; never evidence)

- Completed-work appendices (2026-10-06): plain text reorders table rows (titles, opinions and directorate
  headings come out of sequence; two rows can run together). Read row/opinion pairing from the .layout.txt,
  then quote the contiguous "<title> <opinion>" string from plain text; it usually verifies.
- Verifier normalisation (2026-10-06): hyphens, en dashes and bullets all become spaces, so "Advisory - no
  opinion" and "15 -25" verify as typed. Quotes may cross table cells if the plain-text order is contiguous.
- Risk strategy (2026-10-06): pdf_page equals printed page in the appendix part. Impact table (p.14) and
  appetite table (pp.16-17) garble in plain text; matrix (p.18) row labels are scrambled in plain text but
  each row's "labels + scores" run is contiguous and quotable. Appetite shading is not in the text layer:
  render p.16-17 with pdftoppm to see which cells are shaded.
- Plan covering report is the covering report only; appendices are not in the file (check each run).
- Building history.json with a small Python script in the scratchpad (helper that returns
  {source, pdf_page, quote}) made it easy to fix quotes and re-run the verifier.
