# KCAP — Korea Central Asia Platform

Business Gateway Platform. First release candidate, English / Korean / Russian.

This repository contains only website source and public-source content. Synced Brief documents and internal research are outside the repository.

## Build

Python 3.12; no external packages required.

```sh
python build.py
python verify.py
python -m http.server 8770 --directory dist
```

GitHub Pages build uses `BASE_PATH=/kcap-site` and `SITE_ORIGIN=https://eldarmustafayev456.github.io`.
For a custom domain or root hosting, use an empty `BASE_PATH` and the confirmed `SITE_ORIGIN`.

## Content updates without editing code

Open `/kcap-site/admin/`. Select pages, projects, news or sectors. Edit the fields, including EN / 한국어 / RU. Save the update file, then upload it to the repository's `content` folder, replacing the same filename. Commit the update in GitHub. The build validates links and produces the updated pages.

The editor prepares a file locally; it does not directly save to GitHub. GitHub sign-in and write permission are required for uploading it. To edit an existing draft, import the corresponding original content file from GitHub. Only published records are served in the website editor. Project and news records support `draft` / `published`; featured projects appear on the homepage.

All content and history in this repository are public. Do not store confidential materials or credentials here.

## Release controls

Pushes to main run the build, checks and deployment automatically. GitHub Pages source must be GitHub Actions. The workflow can also be run manually.

Korean review and public launch were confirmed by the user on October 13, 2026. GitHub builds use `PUBLIC_RELEASE=1`. The builder requires `korean_review_approved` in `content/release.json`; local preview defaults to noindex. Legal placeholder pages are excluded from indexing until final texts are supplied.

## Current content

8 source-based projects: 4 Kyrgyzstan, 4 Uzbekistan. Project source links and source IDs are retained. Financial figures remain source-stated values, not financing requests. Stages are not invented to diversify filters.

9 sectors and 3 news articles. The June 15, 2026 Uzbekistan–Korea forum article uses the photo provided for KCAP. KTI is described as a forum organizer, not a KCAP partner.

## Contact

General: info@koreacentralasia.com. Projects: project@koreacentralasia.com.

The form prepares an email with visitor language and project reference in the visitor's mail client. It does not send a server-side message and never claims delivery. Server-side delivery, spam protection and delivery testing remain to be connected with an agreed provider.

## Remaining before full acceptance

- Confirm operator name/registration information; supply privacy and legal texts.
- Connect server-side form delivery and anti-spam; verify received test messages.
- Replace the file-upload editing workflow with direct authenticated saving if required.
- Confirm primary domain and connect DNS/HTTPS.

The website currently has no analytics or tracking cookies. HTTPS for the GitHub Pages URL is provided by hosting. A custom domain has not been configured.
