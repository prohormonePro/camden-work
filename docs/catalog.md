# Agent failure catalog

The unchanged research snapshot contains 283 canonical mechanisms across 25 families, 57 source records, 12 aliases, 208 source-crosswalk rows and 120 supplied-label crosswalk rows. Its research date is September 22, 2026.

The count describes a chosen mechanism taxonomy. It is not an incident census, a set of mutually exclusive causes or 283 independently reproduced failures. One workflow can exhibit several mechanisms and several outcomes.

## Read the axes separately

- **Research basis:** R (123 entries), E (96), or D (64), with the original evidence legend retained in the data.
- **Applicability:** whether the released local controller has the affected boundary. Physical systems and production provider connectors are not implemented here.
- **Verification:** an exact test and version, a documented limitation, or no exercised test. A source citation is not a passing runtime test.
- **Outcome:** EFFECT, CLAIM, LINEAGE, AUTHORITY, CONTINUATION, VERIFICATION, OBJECTIVE, BINDING, CONFIDENTIALITY or RESOURCE. These are consequences, not substitutes for the mechanism.

Each full record preserves its trace, invariant, mitigation, residual limit, source IDs and mapping qualifications. Alias resolution never creates another canonical mechanism. The crosswalks preserve unmapped labels instead of forcing a false equivalence.

## Query small slices

The browser combines text, family, basis and outcome filters. Deep links use the canonical entry ID or a retained alias. The JSON download preserves the original metadata, including its false runtime-audit and publication flags. A later software release does not retroactively change those research flags.

From Python:

```python
from camden_work.catalog import search, entry
print(search(family='TX', outcome='EFFECT', limit=5))
print(entry('AF-TX-01'))
```

The [tool contract](tools.md) documents the same bounded queries over MCP. Search may return zero matches without establishing that no such failure exists outside this catalog.

## Source review and corrections

Read the complete [source register and 22 retained corrections](sources.md), [aliases and both crosswalks](crosswalks.md), and [related-work comparison](related-work.md). The [coverage matrix](coverage.json) keeps local subcase tests separate from unexercised mechanisms.

HTTP success is not a source audit. Titles, authors, versions, supporting passages and source scope require separate checks. The public corrections layer must retain the original record and identify the newer observation. Do not silently rewrite the research snapshot.

Rendered review found that AgentEval Table 8 labels its taxonomy as 21 Level 3 subcategories while 20 rows are visible. The RIFL PDF at the supplied URL is a paper, although its supplied record describes a presentation. These observations do not invalidate every related mechanism or prove the proposed mitigations.

The source papers remain at their publishers' URLs. Full third-party PDFs are not bundled. Licensing and final claim-support review remain release gates for this private candidate.
