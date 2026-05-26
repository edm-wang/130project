/**
 * Mock paper-detail records keyed by paper id. The post_recommendation.html
 * mock only shows one paper; we provide a single default but the page falls
 * back to it when the :id segment doesn't match.
 */

export const paperDetails = {
  'paper-1': {
    source: 'arXiv',
    category: 'cs.LG',
    publishedAt: '2026-04-23',
    title: 'Scaling Laws for Reward Model Generalization in RLHF Training',
    authors: 'J. Patel, S. Nakamura, L. Rivera, M. Osei',
    affiliation: 'Crestfield Institute of Technology · Bayside University',
    metaPills: ['cs.LG', 'cs.AI', '8 pages', 'Apr 23, 2026'],
    reason:
      'Matches your topic interest "RLHF" and keyword "reward modeling". Score: 0.94 — top 3% of today\'s candidates.',
    sourceUrl: 'https://arxiv.org/abs/2604.00001',
    upvotes: 142,
    downvotes: 8,
    userVote: 1,
    userSaved: true,
    autoCategories: ['Alignment', 'Scaling'],
    savedDate: 'Apr 23',
    readingListSize: 7,
    summary: {
      generatedAt: 'Apr 23, 2026 at 6:02 AM',
      sections: [
        {
          heading: 'What this paper is about',
          paragraphs: [
            'This paper investigates how {hl:reward models} used in RLHF training behave as model size, dataset size, and compute budget scale up. The authors find consistent {hl:power-law scaling relationships} — similar to those observed in base language model pretraining — governing reward model accuracy and generalization to held-out preference data.',
          ],
        },
        {
          heading: 'Key findings',
          paragraphs: [
            'Larger reward models generalize better across distribution shifts in human preference data, but exhibit diminishing returns past a critical parameter threshold. The paper identifies {hl:reward model capacity} as a primary bottleneck in RLHF pipelines, suggesting that practitioners who scale the policy model without proportionally scaling the reward model may see degraded alignment outcomes. The authors propose a compute-optimal allocation formula balancing policy and reward model budgets.',
          ],
        },
        {
          heading: 'Why it matters',
          paragraphs: [
            'For researchers working on {hl:alignment and RLHF}, this work provides actionable guidance on how to allocate training compute. It challenges the common practice of using a small reward model with a large policy model, and offers empirical evidence that reward model under-investment is a key cause of reward hacking at scale.',
          ],
        },
        {
          heading: 'Limitations',
          paragraphs: [
            'Experiments are limited to text-only preference data and a single reward model architecture family. The scaling laws may not transfer directly to multimodal or code-generation settings. The paper also does not evaluate downstream policy quality after full RLHF fine-tuning.',
          ],
        },
      ],
    },
    video: {
      generatedAt: 'Apr 23, 2026 at 6:18 AM',
      lengthLabel: '4 min 12 sec',
      currentLabel: '1:21 / 4:12',
      progress: 0.32,
      chapters: [
        { time: '0:00', label: 'Introduction — Why reward model scaling matters' },
        { time: '1:10', label: 'Experimental setup and scaling methodology', active: true },
        { time: '2:05', label: 'Power-law findings across model and data scale' },
        { time: '3:10', label: 'Compute-optimal allocation formula' },
        { time: '3:48', label: 'Limitations and future directions' },
      ],
    },
    related: [
      {
        cat: 'cs\nLG',
        title: 'RLHF from Imperfect Human Feedback: A Robust Training Framework',
        meta: 'Okonkwo et al. · Westlake Univ. · Apr 21',
      },
      {
        cat: 'cs\nAI',
        title: 'Reward Model Ensembles for Preference Uncertainty Estimation',
        meta: 'Hargrove et al. · Northgate Tech · Apr 19',
      },
      {
        cat: 'cs\nCL',
        title: 'Constitutional Reward Shaping at Scale',
        meta: 'Delacroix et al. · Crestfield Inst. · Apr 17',
      },
    ],
  },
};

export function getPaperDetail(id) {
  return paperDetails[id] || paperDetails['paper-1'];
}
