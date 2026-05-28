/**
 * JSDoc typedefs mirroring the FastAPI/Supabase response shapes.
 * VS Code reads these for autocomplete without committing to TypeScript.
 *
 * Backend reference: backend/app/routers/recommendation_batch.py
 * Schema reference: supabase-nextjs/supabase/migrations/20260517055912_create_initial_schema.sql
 */

/**
 * @typedef {Object} Paper
 * @property {string} id
 * @property {'arxiv'|'semantic_scholar'|'manual'} source
 * @property {string} source_id
 * @property {string} title
 * @property {string} [abstract]
 * @property {string} [authors_text]
 * @property {string[]} categories
 * @property {string} source_url
 * @property {string} [pdf_url]
 * @property {string} [published_at]
 * @property {string} [source_updated_at]
 */

/**
 * @typedef {Object} Recommendation
 * @property {string} id
 * @property {string} batch_id
 * @property {string} paper_id
 * @property {number} rank_position
 * @property {number} final_score
 * @property {string} [explanation_summary]
 * @property {Paper} paper
 */

/**
 * @typedef {Object} RecommendationBatch
 * @property {string} id
 * @property {'pending'|'completed'|'failed'} status
 * @property {string} algorithm_version
 * @property {string} created_at
 * @property {string} [completed_at]
 * @property {number} [final_count]
 */

/**
 * @typedef {Object} Interest
 * @property {string} id
 * @property {'field'|'topic'|'author'|'keyword'|'category'} interest_type
 * @property {string} value
 * @property {number} preference_weight
 */

/**
 * @typedef {Object} SavedPaper
 * @property {string} id
 * @property {string} paper_id
 * @property {string} [category]
 * @property {string} created_at
 * @property {Paper} paper
 */

export {};
