// Mock data for FeedPage — used when VITE_USE_MOCK_DATA=true or when the
// backend is unavailable. Shapes match the typedefs in src/shapes/shapes.js.

export const userInterests = [
  { id: 'i1', interest_type: 'field', value: 'Machine Learning' },
  { id: 'i2', interest_type: 'field', value: 'NLP' },
  { id: 'i3', interest_type: 'topic', value: 'Transformers' },
  { id: 'i4', interest_type: 'topic', value: 'RLHF' },
  { id: 'i5', interest_type: 'author', value: 'Y. LeCun' },
  { id: 'i6', interest_type: 'keyword', value: 'diffusion models' },
  { id: 'i7', interest_type: 'keyword', value: 'alignment' },
];

export const weekStats = [
  { value: 48, label: 'Papers served' },
  { value: 7, label: 'Saved' },
  { value: 23, label: 'Upvotes given' },
  { value: 4, label: 'Summaries' },
];

export const similarResearchers = [
  { initials: 'LB', color: 'mint', name: 'L. Barros', affil: 'MIT CSAIL', shared: 'RLHF · alignment' },
  { initials: 'KP', color: 'lilac', name: 'K. Patel', affil: 'Stanford NLP', shared: 'NLP · Transformers' },
  { initials: 'RY', color: 'peach', name: 'R. Yamamoto', affil: 'DeepMind', shared: 'diffusion models' },
];

export const quickLinks = [
  { label: 'My Reading List (7)', to: '/reading-list' },
  { label: 'Edit Profile', to: '/profile' },
  { label: 'Past Digests', to: '/reading-list' },
];

export const mockBatch = {
  id: 'batch-mock',
  status: 'completed',
  algorithm_version: 'multi_vector_v1',
  created_at: '2026-04-23T06:00:00Z',
  completed_at: '2026-04-23T06:00:00Z',
};

export const mockRecommendations = [
  {
    id: 'rec-1',
    batch_id: 'batch-mock',
    paper_id: 'paper-1',
    rank_position: 1,
    final_score: 0.94,
    explanation_summary: 'Matches your topic interest "RLHF" and keyword "alignment"',
    paper: {
      id: 'paper-1',
      source: 'arxiv',
      source_id: '2604.00001',
      title: 'Scaling Laws for Reward Model Generalization in RLHF Training',
      authors_text: 'J. Schulman, I. Ziegler, O. Stiennon · OpenAI',
      abstract:
        'We study how reward model performance scales with model size, dataset size, and compute budget, finding consistent power-law behavior analogous to those observed in language model pretraining. Our results suggest that reward model capacity is a key bottleneck in...',
      categories: ['cs.LG'],
      source_url: 'https://arxiv.org/abs/2604.00001',
      published_at: '2026-04-23T00:00:00Z',
    },
  },
  {
    id: 'rec-2',
    batch_id: 'batch-mock',
    paper_id: 'paper-2',
    rank_position: 2,
    final_score: 0.89,
    explanation_summary: 'Matches your keyword "diffusion models" and field "NLP"',
    paper: {
      id: 'paper-2',
      source: 'arxiv',
      source_id: '2604.00002',
      title: 'Diffusion Language Models via Score Matching on Discrete Token Spaces',
      authors_text: 'Y. Song, C. Meng, S. Ermon · Stanford University',
      abstract:
        'We propose a framework for applying diffusion-based generative modeling to discrete sequences by defining noise processes on token embedding manifolds. This approach unifies autoregressive and diffusion paradigms and achieves competitive perplexity with...',
      categories: ['cs.CL'],
      source_url: 'https://arxiv.org/abs/2604.00002',
      published_at: '2026-04-23T00:00:00Z',
    },
  },
  {
    id: 'rec-3',
    batch_id: 'batch-mock',
    paper_id: 'paper-3',
    rank_position: 3,
    final_score: 0.84,
    explanation_summary: 'Matches your keyword "alignment" and topic "RLHF"',
    paper: {
      id: 'paper-3',
      source: 'arxiv',
      source_id: '2604.00003',
      title:
        'Constitutional AI at Scale: Lessons from Training Frontier Models with Human Feedback',
      authors_text: 'A. Bai, S. Kadavath, S. Kundu · Anthropic',
      abstract:
        'We present an updated analysis of Constitutional AI training across model scales from 1B to 100B parameters, examining how alignment properties emerge and degrade with scale. We find that larger models require more nuanced constitutional principles to avoid...',
      categories: ['cs.AI'],
      source_url: 'https://arxiv.org/abs/2604.00003',
      published_at: '2026-04-22T00:00:00Z',
    },
  },
];

export const mockResponse = {
  batch: mockBatch,
  recommendations: mockRecommendations,
};
