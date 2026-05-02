# Philippines Mission Intel Report

Automated daily generation of a 700+ word report titled:

**Philippines Mission Intel Status Report**

## Mission
At 0001Z daily, generate a structured report using configured public sources, validate it, save archive and latest outputs, and upload them to the target Google Drive folder.

## Core outputs
- DOCX archive
- DOCX latest
- PDF archive
- PDF latest
- source log JSON
- validation JSON
- manifest JSON

## Required report sections
1. Strategic Situation
2. Priority Intelligence
3. U.S. Embassy (Manila) travel advisories
4. U.S. State Department travel advisories for Americans
5. Immunization recommendations
6. Weather forecast
7. NAIA publications and announcements
8. Geothermal activity reported in the country
9. Chinese hostility towards Philippine Navy or Coastguard in the China Sea or disputed territories
10. The effect of global conflicts affecting flights in and out of the country
11. PAGASA updates and announcements
12. Operational Environment

## Deployment target
- Scheduler: GitHub Actions
- Storage: Google Drive
- Publication timestamp: 0001Z daily
- Target folder ID: `1KdRuyLOb4z89Vsi_M6MLYbOIJUivhfiF`

## Quick start
1. Create GitHub repository
2. Add all project files
3. Configure GitHub secrets
4. Confirm Google Drive service account access
5. Run workflow_dispatch once
6. Validate archive and latest outputs in Drive

## Notes
- UTC/Zulu is the master report time basis
- PAGASA is the correct agency name even if older prompt text uses PEGASA
- Failed reports do not overwrite `LATEST`