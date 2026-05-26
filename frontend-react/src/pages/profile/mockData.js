export const profile = {
  initials: 'AC',
  name: 'Alex Chen',
  affiliation:
    'PhD Candidate · Westlake University of Science · Advised by Prof. R. Holloway',
  bio:
    'Researching scalable alignment methods and reward model generalization for large language models. Interested in the intersection of NLP, RLHF, and diffusion models.',
  publicProfile: true,
  links: [
    { label: 'LinkedIn', color: '#0077B5' },
    { label: 'Scholar profile', color: '#4285F4' },
    { label: 'X / Twitter', color: '#111' },
    { label: 'Personal site', color: '#1D9E75' },
  ],
};

export const interests = {
  field: ['Machine Learning', 'Natural Language Processing', 'Computer Vision'],
  topic: ['Transformers', 'RLHF', 'In-context Learning', 'Mechanistic Interpretability'],
  author: ['T. Hargrove', 'M. Delacroix', 'S. Okonkwo'],
  keyword: ['diffusion models', 'alignment', 'reward modeling', 'sparse attention'],
};

export const savedPapers = [
  {
    id: 'paper-1',
    title: 'Scaling Laws for Reward Model Generalization in RLHF Training',
    meta: 'Patel et al. · Crestfield Institute of Technology · arXiv Apr 23',
    categories: ['Alignment', 'Scaling'],
  },
  {
    id: 'paper-2',
    title: 'Diffusion Language Models via Score Matching on Discrete Token Spaces',
    meta: 'Nakamura et al. · Bayside University · arXiv Apr 23',
    categories: ['Generative Models'],
  },
  {
    id: 'paper-3',
    title: 'FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-Precision',
    meta: 'Rivera et al. · Northgate Technical University · arXiv Apr 18',
    categories: ['Efficiency'],
  },
];

export const activity = [
  { label: 'Papers seen', value: 284 },
  { label: 'Saved papers', value: 7 },
  { label: 'Upvotes given', value: 41 },
  { label: 'Downvotes given', value: 12 },
  { label: 'Summaries viewed', value: 9 },
  { label: 'Member since', value: 'Jan 2025' },
];

export const editFields = {
  displayName: 'Alex Chen',
  affiliation: 'Westlake University of Science',
  bio:
    'Researching scalable alignment methods and reward model generalization for LLMs.',
  linkedIn: 'https://linkedin.com/in/alexchen',
  scholar: 'https://scholar.google.com/alexchen',
  email: 'alex@wus.edu',
};
