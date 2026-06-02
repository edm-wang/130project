// [GenAI Usage] Prompt:
// Update TextSummary to handle both the real API shape (summary.summary_text plain string,
// summary.llm_model) and the existing mock shape (summary.sections array with heading/paragraphs,
// summary.generatedAt). Detect which format is present and branch accordingly. Accept an optional
// onRegenerate prop so the real data path can wire a regenerate button.
// [GenAI Usage] Response begins:

// [GenAI Usage 2] Prompt: The LLM summary service returns markdown-formatted text with headers,
// bold text, and section structure (e.g., "# Overall TL;DR", "## Section-by-section Summary"),
// but it was rendering as plain text with whiteSpace: pre-line. I needed proper markdown rendering
// so headings appear bold and hierarchical, and emphasized text shows correctly. I asked Claude
// to install react-markdown and replace the plain text rendering with <ReactMarkdown> component,
// then add CSS to style the markdown elements (h1/h2/h3, strong, em, lists) to match the app's
// design tokens. I verified that the markdown preserves the academic formatting from the LLM output.
// [GenAI Usage 2] LLM response begins:
import ReactMarkdown from 'react-markdown';
// [GenAI Usage 2] LLM response ends (import only)
import PillButton from '../../components/atoms/PillButton.jsx';
import styles from './TextSummary.module.css';

function renderParagraph(text) {
  const parts = [];
  const regex = /\{hl:([^}]+)\}/g;
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) parts.push(text.slice(lastIndex, match.index));
    parts.push(
      <span key={`hl-${match.index}`} className={styles.highlight}>
        {match[1]}
      </span>,
    );
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) parts.push(text.slice(lastIndex));
  return parts;
}

export default function TextSummary({ summary, onRegenerate }) {
  // Real API response: summary.summary_text is a plain text string
  if (summary.summary_text) {
    return (
      <div>
        <div className={styles.genStatus}>
          <div className={styles.genDot} />
          AI summary generated · {summary.llm_model || 'gpt-4o-mini'}
        </div>
        {/* [GenAI Usage 2] Changed from plain div with whiteSpace: pre-line to ReactMarkdown */}
        {/* [GenAI Usage 2] LLM response begins */}
        <div className={styles.summary}>
          <ReactMarkdown>{summary.summary_text}</ReactMarkdown>
        </div>
        {/* [GenAI Usage 2] LLM response ends */}
        <div className={styles.footerRow}>
          {onRegenerate && (
            <PillButton style={{ fontSize: 11 }} onClick={onRegenerate}>
              Regenerate summary
            </PillButton>
          )}
        </div>
      </div>
    );
  }

  // Mock data path: summary.sections array with heading/paragraphs
  return (
    <div>
      <div className={styles.genStatus}>
        <div className={styles.genDot} />
        AI summary generated · {summary.generatedAt}
      </div>
      <div className={styles.summary}>
        {summary.sections.map((section) => (
          <div key={section.heading}>
            <div className={styles.sectionTitle}>{section.heading}</div>
            {section.paragraphs.map((p, i) => (
              <p key={i}>{renderParagraph(p)}</p>
            ))}
          </div>
        ))}
      </div>
      <div className={styles.footerRow}>
        <PillButton style={{ fontSize: 11 }}>Regenerate summary</PillButton>
        <PillButton style={{ fontSize: 11 }}>Copy summary</PillButton>
      </div>
    </div>
  );
}
// [GenAI Usage] Response ends
// [GenAI Reflection] The dual-format branch (summary_text check first, sections fallback)
// keeps backward compatibility with mock mode without touching the mock rendering path.
// Using whiteSpace: pre-line for the plain text path preserves the bullet-point line breaks
// that gpt-4o-mini returns without needing to parse the text into structured data.