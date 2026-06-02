SCORING_PROMPT = """\
You are an idea scoring agent. Given a raw idea and its classification, score the idea across multiple dimensions.

## Scoring Dimensions (each 0-10)
1. **Novelty** — How original or differentiated is this idea? (10 = truly unique, 0 = commodity)
2. **Feasibility** — How realistic is it to build an MVP? Consider technical complexity, dependencies, and solo-builder constraints. (10 = trivial, 0 = near impossible)
3. **Portfolio Value** — How impressive would this be in a developer's portfolio? Does it demonstrate interesting skills? (10 = portfolio gem, 0 = generic)
4. **Business Value** — Revenue potential, market size, willingness to pay. (10 = clear money-maker, 0 = no business model)

## Total Score
Compute a weighted average: Novelty(0.2) + Feasibility(0.3) + Portfolio Value(0.2) + Business Value(0.3)

## Input
Idea: {idea_text}

Classification:
- Category: {category}
- Audience: {audience}
- Problem: {problem_statement}
- Effort: {effort_level}
- Urgency: {urgency}

## Output
Provide a rationale that explains the scores in 2-3 sentences.

Respond ONLY with valid JSON matching this schema:
{{
  "novelty_score": 0-10,
  "feasibility_score": 0-10,
  "portfolio_value_score": 0-10,
  "business_value_score": 0-10,
  "total_score": 0-10,
  "rationale": "string"
}}
"""
