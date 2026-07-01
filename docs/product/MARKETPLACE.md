# Marketplace

**Status:** Product overview (customer-facing)  
**Normative detail:** [../architecture/PLATFORM_GLOSSARY.md](../architecture/PLATFORM_GLOSSARY.md) · [../architecture/PLATFORM_UX_MODEL.md](../architecture/PLATFORM_UX_MODEL.md)

---

## Overview

The **Marketplace** is how customers and partners discover, certify, and install **Provider Plugins** — connectors, partner agents, and automation Providers — without modifying Platform Core source code.

## What customers install

| Artefact | Description |
|----------|-------------|
| **Connector Plugin** | `provider_kind: connector` — GitHub, Jira, CI/CD, etc. |
| **Partner agent** | `provider_kind: ai-agent` — certified third-party Providers |
| **Solution Pack** | Composed metadata bundle (Workflows, Policies, Profiles) |

## Install flow (target)

1. Browse Marketplace catalogue (Platform UX — PI-09)
2. Entitlement check (PI-08)
3. Metadata Engine publish + registry index (PI-02 / PI-09)
4. Optional `auto_register` for connector Providers

## Engineering roadmap

| Phase | PI |
|-------|-----|
| Marketplace preparation | PI-08-Solution-Packs |
| Install pipeline + Builders | PI-09-Platform-UX |
| Partner certification at scale | PI-10-General-Availability |
