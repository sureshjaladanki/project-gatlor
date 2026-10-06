# Gatlor: brief vision

Owner: Suresh Jaladanki. Design date: 5 October 2026.

**Aim.** Give a small maker selling a connected device or installable software into the EU one place where every release has a true SBOM, every known vulnerability that touches it has a recorded decision, every exploited one has its reports drafted inside the clock, and the technical file builds itself from that history.

**How it runs.** Engineering working EU business hours. A free Apache-2.0 CLI and CI action wraps existing SBOM generators and OSV, so a maker can see their own gaps for free. A fixed-price build-in sprint wires the maker's pipeline into the evidence ledger and runs a reporting drill with the maker's own people. The ledger subscription keeps it running. The ledger source is FSL-1.1-ALv2 (source-available, not OSI open source). CI uploads each release's SBOM, stored by content hash. Gatlor re-matches it against public vulnerability feeds every day. The maker's named people record a VEX decision for each match. When a vulnerability is actively exploited, Gatlor starts the Article 14 clock and drafts the 24-hour, 72-hour and 14-day texts. The technical-file export is assembled from that history. A failed check blocks the export. Software drafts and alerts. A named human at the maker presses and files.

**Not this.** Gatlor does not say a product is compliant or certified. It gives no legal opinions, does not act as a notified body, and never files to ENISA for a customer. It does not run 24/7 cover, analyse binary firmware in house, or grow into a generic GRC, ISO 27001 or NIS2 tool. It has no storefront, checkout, marketplace or consumer app. It never backdates evidence, deletes a VEX decision, or hides a vulnerability to turn a dashboard green.

**Detail lives in:**

- [architectural-blueprint.md](architectural-blueprint.md): the product contract and the system engineers build.
- [licensing.md](licensing.md): Apache CLI, FSL ledger, kit licence, trademarks.
