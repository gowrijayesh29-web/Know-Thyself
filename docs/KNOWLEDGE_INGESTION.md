# Know Thyself - Knowledge Base Ingestion Strategy

## Overview

This document describes the strategy for building, maintaining, and updating the evidence-based knowledge base that powers Know Thyself's educational content and AI recommendations.

## Principles

1. **Evidence-Based**: All content must be backed by credible sources
2. **Transparency**: Every claim must have traceable citations
3. **Quality Grading**: Explicit evidence quality ratings
4. **Currency**: Regular verification and updates
5. **Accessibility**: Multiple difficulty levels
6. **Personalization**: AI-curated relevance

## Source Hierarchy

### Tier 1: Highest Quality (Evidence Quality: HIGH)
- **Systematic Reviews & Meta-Analyses**
  - Cochrane Library
  - Campbell Collaboration
  - JAMA Network Meta-Analyses
  - BMJ Systematic Reviews

- **Clinical Practice Guidelines**
  - USPSTF (US Preventive Services Task Force)
  - NICE (UK National Institute for Health and Care Excellence)
  - ACC/AHA (Cardiology)
  - ADA (Diabetes)
  - WHO Guidelines

- **Major Medical Institutions**
  - Mayo Clinic
  - Cleveland Clinic
  - Johns Hopkins Medicine
  - Harvard Health Publishing

- **Government Health Agencies**
  - CDC (Centers for Disease Control)
  - NIH (National Institutes of Health)
  - FDA (Food and Drug Administration)
  - Health Canada
  - NHS (UK National Health Service)

### Tier 2: High Quality (Evidence Quality: HIGH/MODERATE)
- **Peer-Reviewed Journals (Top Tier)**
  - New England Journal of Medicine
  - The Lancet
  - JAMA
  - BMJ
  - Nature Medicine
  - Annals of Internal Medicine

- **Randomized Controlled Trials (RCTs)**
  - Phase 3/4 trials
  - Large sample sizes (>1000)
  - Published in top journals

### Tier 3: Moderate Quality (Evidence Quality: MODERATE)
- **Peer-Reviewed Journals (Specialty)**
  - Sleep Medicine Reviews
  - Journal of Nutrition
  - Medicine & Science in Sports & Exercise
  - Journal of Behavioral Medicine
  - Computers in Human Behavior

- **Cohort Studies**
  - Large prospective cohorts (>10,000)
  - Long follow-up (>5 years)
  - Adjustment for confounders

- **Case-Control Studies**
  - Well-matched controls
  - Clear exposure definitions

### Tier 4: Emerging/Low Quality (Evidence Quality: LOW/EMERGING)
- **Cross-Sectional Studies**
- **Case Reports/Series**
- **Expert Opinion/Commentary**
- **Preprints (not peer-reviewed)**
- **Industry-Funded Studies** (flagged)

### Excluded Sources
- Blog posts without citations
- Commercial websites selling products
- Anecdotal evidence
- Social media posts
- Non-peer-reviewed content

## Ingestion Pipeline

### 1. Source Identification
```
Automated Discovery:
├── PubMed/MEDLINE API queries (scheduled)
├── ClinicalTrials.gov monitoring
├── Cochrane Library RSS
├── Guideline clearinghouse APIs
├── Journal RSS feeds (top 50 journals)
└── Manual curation queue

Manual Curation:
├── Expert recommendations
├── User-requested topics
├── Gap analysis from user queries
└── Trending health topics
```

### 2. Metadata Extraction
For each source, extract:
```json
{
  "title": "Full publication title",
  "authors": ["Author One", "Author Two"],
  "publication": "Journal Name",
  "publication_date": "2024-01-15",
  "doi": "10.1001/jama.2024.1234",
  "pmid": "38231234",
  "url": "https://pubmed.ncbi.nlm.nih.gov/...",
  "source_type": "rct",
  "study_design": "parallel_group",
  "sample_size": 2500,
  "population": "adults 40-65 with hypertension",
  "intervention": "Mediterranean diet vs control",
  "outcome": "SBP reduction at 12 months",
  "key_findings": [
    "Mean SBP reduction: 4.2 mmHg (95% CI 2.1-6.3)",
    "Greater effect in those with baseline SBP >140"
  ],
  "methodology": "Multi-center, randomized, controlled...",
  "funding_sources": ["NIH", "American Heart Association"],
  "conflicts_of_interest": "None reported",
  "limitations": [
    "Predominantly white population",
    "12-month follow-up only"
  ],
  "quality_assessment": {
    "risk_of_bias": "low",
    "applicability": "high",
    "consistency": "high"
  }
}
```

### 3. Quality Assessment (GRADE-inspired)

| Domain | HIGH | MODERATE | LOW | EMERGING |
|--------|------|----------|-----|----------|
| Study Design | SR/MA, RCT | Cohort, RCT (small) | Case-control, Cross-sectional | Case report, Expert opinion |
| Risk of Bias | Low | Some concerns | High | Very high |
| Inconsistency | None | Minor | Substantial | N/A |
| Indirectness | None | Minor | Major | N/A |
| Imprecision | None | Minor | Major | N/A |
| Publication Bias | Unlikely | Possible | Likely | N/A |

**Final Quality**: Lowest rating across domains, with upgrades for:
- Large effect size (+1)
- Dose-response gradient (+1)
- All plausible confounding would reduce effect (+1)

### 4. Article Generation

For each topic, create structured article:

```markdown
---
slug: "mediterranean-diet-cardiovascular-health"
title: "Mediterranean Diet for Cardiovascular Health"
subtitle: "Evidence-based guide to heart-healthy eating patterns"
category: "nutrition"
subcategory: "dietary_patterns"
tags: ["mediterranean diet", "cardiovascular", "prevention", "dietary patterns"]
evidence_quality: "high"
evidence_sources: [...]
primary_source_type: "systematic_review"
doi: "10.1001/jama.2023.12345"
pmid: "37845672"
applicable_populations: ["general", "cardiovascular_risk", "metabolic_syndrome"]
applicable_conditions: ["hypertension", "dyslipidemia", "type_2_diabetes"]
limitations: "Most studies in Mediterranean populations; applicability to other ethnicities needs verification"
contraindications: "None for general population; individual allergies apply"
reading_time_minutes: 8
difficulty_level: 2
is_published: true
is_featured: true
---

# Mediterranean Diet for Cardiovascular Health

## Summary
The Mediterranean dietary pattern is one of the most extensively studied and consistently beneficial dietary approaches for cardiovascular disease prevention...

## Key Takeaways
1. **Strong evidence** supports Mediterranean diet for primary and secondary CVD prevention
2. **Core components**: Olive oil, nuts, fruits, vegetables, whole grains, fish, moderate wine
3. **Risk reduction**: ~30% lower CVD events in high-quality trials

## Practical Tips
1. Replace butter with extra virgin olive oil
2. Eat fish 2-3 times per week
3. Include handful of nuts daily
...

## Evidence
[Structured evidence table with citations]
```

### 5. Verification & Updates

**Automated Checks** (Monthly):
- Link validation (DOI, PMID, URL accessibility)
- Retraction watch monitoring
- New version detection (guideline updates)
- Citation count tracking

**Manual Review** (Quarterly):
- Clinical guideline updates
- New landmark trials
- Safety alerts (FDA, EMA)
- Population-specific applicability changes

**Scheduled Re-verification**:
- Guidelines: 6 months
- Systematic reviews: 12 months
- RCTs: 24 months
- Emerging research: 6 months

### 6. Vector Embedding for Semantic Search

For each article, generate embeddings:
```python
# Using NV-EmbedQA-E5-V5
text_for_embedding = f"""
Title: {article.title}
Category: {article.category}
Summary: {article.summary}
Key Takeaways: {' '.join(article.key_takeaways)}
Content: {article.content[:2000]}
Tags: {' '.join(article.tags)}
"""

embedding = model.encode(text_for_embedding)
# Store in pgvector column (1024 dimensions)
```

### 7. Personalization Signals

Track user interactions for recommendation engine:
- View time & scroll depth
- Completion rate
- Helpful ratings
- Shares & bookmarks
- Search queries
- Goal context
- Pattern triggers

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Set up evidence source database
- [ ] Build PubMed API integration
- [ ] Create quality assessment framework
- [ ] Build article generation pipeline
- [ ] Implement vector embedding

### Phase 2: Content Population (Weeks 5-12)
- [ ] Ingest Tier 1 sources (guidelines, SRs)
- [ ] Ingest Tier 2 sources (top RCTs)
- [ ] Build initial article library (200+ articles)
- [ ] Implement verification scheduler
- [ ] Build admin review interface

### Phase 3: Personalization (Weeks 13-16)
- [ ] Build interaction tracking
- [ ] Implement recommendation engine
- [ ] A/B test recommendation relevance
- [ ] Build feedback loops

### Phase 4: Advanced Features (Weeks 17-20)
- [ ] Multi-language support
- [ ] Audio versions of articles
- [ ] Interactive evidence tables
- [ ] Citation network visualization
- [ ] Expert review workflow

## Quality Metrics

### Content Quality
- **Coverage**: % of user queries answered by KB
- **Accuracy**: Expert review score (target > 4.5/5)
- **Currency**: % articles verified < 12 months
- **Completeness**: Key takeaways + practical tips + evidence table

### User Engagement
- **View-to-completion rate**: > 60%
- **Helpful rating**: > 4.0/5.0
- **Share rate**: > 5%
- **Return visits**: > 30% within 30 days

### AI Integration
- **Recommendation relevance**: > 80% user acceptance
- **Citation accuracy**: 100% traceable
- **Hallucination rate**: < 1% (via structured output validation)

## Governance

### Editorial Board
- 2 Physicians (different specialties)
- 1 Registered Dietitian
- 1 Exercise Physiologist
- 1 Behavioral Psychologist
- 1 Medical Librarian
- 1 Patient Advocate

### Review Process
1. **Automated checks** pass
2. **Subject matter expert** reviews
3. **Editorial board** approves
4. **Published** with version tracking
5. **Monitored** for feedback/updates

### Conflict of Interest
- All contributors disclose COI
- Industry-funded studies flagged
- No commercial sponsorship of content
- Transparent funding disclosure

## API for External Access

```yaml
GET /api/v1/knowledge/articles
  - Filter by category, quality, difficulty
  - Search full-text
  - Pagination

GET /api/v1/knowledge/articles/{id}
  - Full article with evidence table
  - Structured citations

GET /api/v1/knowledge/evidence-sources
  - Browse citation database
  - Filter by study design, quality

GET /api/v1/knowledge/recommendations
  - Personalized (authenticated)
  - Context-aware
```

## Future Enhancements

1. **Living Systematic Reviews**: Auto-update when new trials publish
2. **Multilingual Support**: Spanish, Chinese, Arabic
3. **Audio Narration**: TTS for all articles
4. **Interactive Tools**: Risk calculators, meal planners
4. **Clinical Decision Support**: Integration with EHR
5. **Researcher Portal**: Data export for studies
6. **Community Contributions**: Peer-reviewed user submissions