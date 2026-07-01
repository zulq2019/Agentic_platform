# Solution Packs

**Status:** Product overview (customer-facing)  
**Normative detail:** [../architecture/PLATFORM_GLOSSARY.md](../architecture/PLATFORM_GLOSSARY.md) · [../architecture/PLATFORM_PRIMITIVES.md](../architecture/PLATFORM_PRIMITIVES.md)

---

## Overview

**Solution Packs** are versioned, distributable bundles of Platform Object metadata — Workflows, Providers, Policies, Execution Profiles, and Studios — that let enterprises adopt proven engineering operating models without custom platform development.

## Pack types

| Type | Example | Audience |
|------|---------|----------|
| **Engineering Pack** | Greenfield product development | Software engineering orgs |
| **Industry Pack** | Regulated banking SDLC | Compliance-heavy verticals |
| **Partner Pack** | SI-certified migration methodology | Systems integrators |

## Composition

Solution Packs **compose** primitives; they do not embed engine logic. A pack references member objects via the relationship model ([PLATFORM_META_MODEL.md](../architecture/PLATFORM_META_MODEL.md)).

## Commercial relationship

Solution Packs are often distributed through **Commercial Packs** and the **Marketplace**. Entitlements control which packs a tenant may activate ([COMMERCIAL_MODEL.md](./COMMERCIAL_MODEL.md)).

## Engineering roadmap

Primary PI: [PI-08-Solution-Packs](../engineering/implementation-roadmap/PI-08-Solution-Packs/)
