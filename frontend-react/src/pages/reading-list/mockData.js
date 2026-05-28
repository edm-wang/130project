// Reading list rows.
export const readingList = [
  {
    id: 'paper-1',
    title: 'Scaling Laws for Reward Model Generalization in RLHF Training',
    meta: 'Patel et al. · Crestfield Inst. of Technology · Apr 23',
    categories: ['Alignment', 'Scaling'],
    isNew: true,
  },
  {
    id: 'paper-2',
    title: 'Diffusion Language Models via Score Matching on Discrete Token Spaces',
    meta: 'Nakamura et al. · Bayside University · Apr 23',
    categories: ['Generative Models'],
    isNew: true,
  },
  {
    id: 'paper-3',
    title: 'FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-Precision',
    meta: 'Rivera et al. · Northgate Technical University · Apr 18',
    categories: ['Efficiency'],
    read: true,
  },
];

export const filterChips = [
  'All',
  'Alignment',
  'Generative Models',
  'Efficiency',
  'Unread',
];

export const stats = [
  { label: 'Total saved', value: 3 },
  { label: 'Read', value: 1 },
  { label: 'Unread', value: 2 },
  { label: 'With summaries', value: 3 },
  { label: 'Categories', value: 3 },
];

export const categoryCounts = [
  { label: 'Alignment', count: 1 },
  { label: 'Generative Models', count: 1 },
  { label: 'Efficiency', count: 1 },
];

// --- Digest video player state ---
export const TOTAL_SECONDS = 1120; // 18:40
export const chapters = [
  { start: 0,    slide: 0, label: "Intro — Today's feed overview",                       sub: '12 papers · Apr 23, 2026' },
  { start: 80,   slide: 1, label: 'Paper 1 — Scaling Laws for Reward Model Generalization', sub: 'Patel et al. · Crestfield Inst.' },
  { start: 285,  slide: 2, label: 'Paper 2 — Diffusion Language Models via Score Matching', sub: 'Nakamura et al. · Bayside University' },
  { start: 490,  slide: 3, label: 'Paper 3 — FlashAttention-3',                              sub: 'Rivera et al. · Northgate Technical Univ.' },
  { start: 690,  slide: 4, label: 'Papers 4–12 — Key themes overview',                      sub: 'Alignment · Generative Models · Efficiency' },
  { start: 1040, slide: 5, label: 'Feed summary & stats',                                   sub: '12 papers reviewed today' },
];

// One entry per slide-index (0..5). Body shape is per-slide so they don't all
// share the same template; PaperSlide handles the shared header.
export const slides = [
  { kind: 'intro' },
  {
    kind: 'paper',
    label: 'PAPER 1 OF 12',
    title: 'Scaling Laws for Reward Model\nGeneralization in RLHF Training',
    authors: 'Patel et al. · Crestfield Inst. of Technology',
    body: {
      type: 'insight',
      text:
        'Reward model capacity is the primary bottleneck in RLHF — scaling it proportionally to the policy model reduces reward hacking by 2.3× on held-out evals.',
    },
  },
  {
    kind: 'paper',
    label: 'PAPER 2 OF 12',
    title: 'Diffusion Language Models via Score\nMatching on Discrete Token Spaces',
    authors: 'Nakamura et al. · Bayside University',
    body: {
      type: 'bars',
      bars: [
        { label: 'AR\nbaseline', value: 78, color: 'rgba(29,158,117,0.35)' },
        { label: 'Masked\ndiffusion', value: 81, color: 'rgba(29,158,117,0.55)' },
        { label: 'Score\nmatching', value: 87, color: '#1D9E75' },
      ],
      caption: 'LAMBADA next-word accuracy',
    },
  },
  {
    kind: 'paper',
    label: 'PAPER 3 OF 12',
    title: 'FlashAttention-3: Fast and Accurate\nAttention with Asynchrony',
    authors: 'Rivera et al. · Northgate Technical University',
    body: {
      type: 'stats',
      stats: [
        { num: '1.8×', label: 'faster on H100' },
        { num: '740',  label: 'TFLOPS/s' },
        { num: '−41%', label: 'memory use' },
      ],
    },
  },
  { kind: 'themes' },
  { kind: 'summary' },
];
