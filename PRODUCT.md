# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Entry-level prospectors, freelancers, agencies, and small-business operators who
need to find relevant local businesses and develop a repeatable outbound pipeline.

## Product Purpose

Outrelis helps users define an offer and target market, discover business leads
from map data, organize those leads, and eventually prepare relevant outreach.
Early success means moving a new user from an account to a saved, usable lead
search without requiring prospecting expertise.

## Positioning

The product connects map-based lead discovery with pipeline management and guided
outreach in one workflow, with a first-lead path for beginners and a growth path
for users who already prospect.

## Operating Context

Users choose a starting path, describe the service they sell, select an outreach
language, identify a business category, and add one or more target locations.
The backend is FastAPI with PostgreSQL locally and Supabase planned for production.
The frontend is React and communicates with FastAPI through Axios.

## Capabilities and Constraints

- Authentication uses opaque bearer sessions.
- Prospecting setup supports one default offer, a current search draft, and 1–10
  ordered, unique locations.
- Google Maps discovery and lead results are not implemented yet.
- The product must not claim that leads were found until the search capability exists.
- BeUI is the component foundation; GSAP is available for purposeful animation.

## Brand Commitments

The product name is Outrelis. The existing interface uses a deep sage and warm
paper palette, restrained red actions, Instrument Serif for expressive headings,
and DM Sans for interface copy.

## Evidence on Hand

The repository contains authentication, starting-path onboarding, a prospecting
setup API, product planning documents, and existing Outrelis logo assets. It does
not yet contain customer testimonials or production lead-search results.

## Product Principles

- Help beginners reach a meaningful first result without hiding useful controls.
- Keep user-owned prospecting data isolated and resumable.
- Explain the difference between what the user sells and who they want to find.
- Make progress honest: saved configuration is not presented as generated leads.
- Prefer one clear task per stage over dense all-in-one dashboards.
