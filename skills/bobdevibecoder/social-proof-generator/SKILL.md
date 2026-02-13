# social-proof-generator

Generates and maintains social proof elements (testimonials, usage stats, trust badges) for all products.

## Overview

Collects real usage data, generates social proof content, and creates embeddable components for product landing pages. Social proof increases conversion rates by 15-30%.

## Usage

- "social proof PRODUCT-SLUG" - Generate social proof elements for a product
- "social proof stats" - Update live usage counters across all products
- "social proof testimonials PRODUCT-SLUG" - Collect and format testimonials
- "social proof badges PRODUCT-SLUG" - Generate trust badge components

## Social Proof Types

### 1. Live Usage Counters
Track and display real metrics:
- "X files converted today"
- "Y users this month"
- "Z total conversions"

Pull from product analytics or Stripe customer count:
POST http://host.docker.internal:18790/stripe-query
Headers: Content-Type: application/json, X-Bridge-Secret: DEPLOY_BRIDGE_SECRET
Body: { "type": "customers", "product": "PRODUCT-SLUG" }

### 2. Testimonial Collection
Sources for testimonials:
- Positive Stripe customer notes
- GitHub stars and positive issues
- Social media mentions (via web search)
- Direct feedback submissions

Format each testimonial:
- Quote (max 2 sentences)
- Name or "Verified User"
- Role/company if available
- Star rating (1-5)

### 3. Trust Badges
Generate badges based on real data:
- "Free Forever Plan Available"
- "No Credit Card Required"
- "256-bit SSL Encrypted"
- "99.9% Uptime"
- "Used by X+ professionals"
- "Rated 4.8/5 by users"

### 4. Activity Feed (FOMO)
Generate recent activity notifications:
- "Someone from New York just converted a file"
- "12 people are using this tool right now"
- Uses anonymized data, never real names

## Output

For each product, generate:
- src/components/SocialProofBar.tsx (counter bar)
- src/components/Testimonials.tsx (testimonial carousel)
- src/components/TrustBadges.tsx (badge row)
- src/components/ActivityFeed.tsx (live activity popup)
- src/data/social-proof.json (all collected proof data)

## Rules

- ONLY use real data, never fabricate testimonials or inflate numbers
- If no real testimonials exist yet, use usage stats instead
- Round numbers up to nearest milestone: 47 users becomes "45+ users"
- Update social proof data weekly
- Archive old testimonials, keep the 5 best visible
- Never use real customer names without consent, default to "Verified User"

## Integration

- Pull positive feedback from user-feedback-collector skill
- Update counters from Stripe subscriber data
- Push updated components via deploy bridge
- Run weekly to refresh stats
