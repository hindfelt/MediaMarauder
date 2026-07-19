# Privacy Policy — MediaMarauder Chrome Extension

_Last updated: 2026-07-19_

## Summary

This extension sends the URL of the page you are viewing to a server that **you** run and configure. It collects no analytics, sets no cookies, and sends nothing to the extension developer or any third party.

## What data the extension handles

| Data | Purpose | Where it goes |
|---|---|---|
| Current tab URL | Submitted for download when you click a button in the popup | Only to the server address you configured |
| Server URL | Remembers your own backend address | Stored locally via `chrome.storage.local` |
| API token | Authenticates requests to your own server | Stored locally via `chrome.storage.local`, sent only to your configured server |

## What the extension does NOT do

- No browsing history collection — the tab URL is read only at the moment you click, never in the background
- No page content reading — only the URL
- No analytics, telemetry, or tracking of any kind
- No data sent to the developer or any third party
- No cookies, no fingerprinting
- No selling or sharing of data (there is nothing to sell)

## Data storage and retention

All settings (server URL, API token) are stored locally in your browser using Chrome's extension storage. They persist until you remove them or uninstall the extension. Uninstalling deletes all stored data. What happens to URLs after they reach your server is governed by your own server — you operate it, you control it.

## Your consent

By configuring a server URL and clicking a send button, you direct the extension to transmit the current tab URL to that server. No transmission happens without that explicit action.

## Contact

Questions: open an issue at https://github.com/hindfelt/MediaMarauder/issues
