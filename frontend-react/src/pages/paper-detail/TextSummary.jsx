import PillButton from '../../components/atoms/PillButton.jsx';
import styles from './TextSummary.module.css';

/**
 * Render a paragraph that contains {hl:...} markers as highlighted runs.
 * Keeps the markup data-driven rather than embedding <span>s in the mock.
 */
function renderParagraph(text) {
  const parts = [];
  const regex = /\{hl:([^}]+)\}/g;
  let lastIndex = 0;
  let match;
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
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

export default function TextSummary({ summary }) {
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
