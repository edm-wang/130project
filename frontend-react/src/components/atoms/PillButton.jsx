// [GenAI Usage] Prompt: Across the feed cards, paper detail page, and reading list rows there
// are a bunch of small rounded buttons: upvote, downvote, save, view summary, open on arXiv.
// In the static HTML they were all separate styled <button> or <a> tags with slightly
// inconsistent markup. I want one PillButton component that covers all of these, supports an
// "active" state for toggle buttons like upvote/save, a "large" variant for the paper detail
// page, and can render as a link (for the arXiv "open source" button) instead of a button when
// an href is passed in.
// [GenAI Usage] Response Starts:
import styles from './PillButton.module.css';

/**
 * Rounded pill action button. Used for vote/save/summary/source-link buttons
 * across the feed, paper detail, and reading list rows.
 *
 * @param {Object} props
 * @param {'up'|'down'|'save'|'summary'|'arxiv'|'ghost'|undefined} [props.variant]
 * @param {boolean} [props.active]
 * @param {boolean} [props.large]
 * @param {React.ReactNode} props.children
 * @param {() => void} [props.onClick]
 * @param {string} [props.href]   when present renders an <a> instead of <button>
 * @param {string} [props.title]
 * @param {React.CSSProperties} [props.style]
 */
export default function PillButton({
  variant,
  active,
  large,
  children,
  onClick,
  href,
  title,
  style,
}) {
  const className = [
    styles.btn,
    variant ? styles[variant] : '',
    active ? styles.active : '',
    large ? styles.lg : '',
  ]
    .join(' ')
    .trim();

  if (href) {
    return (
      <a
        className={className}
        href={href}
        target="_blank"
        rel="noreferrer"
        title={title}
        style={style}
      >
        {children}
      </a>
    );
  }
  return (
    <button
      type="button"
      className={className}
      onClick={onClick}
      title={title}
      style={style}
    >
      {children}
    </button>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Reflection] I went with Claude Code on this one because the href branch (rendering an
// <a> with target="_blank" and rel="noreferrer" instead of a <button>) wasn't something I'd
// thought to handle until I tried passing an href prop to a plain button and realized clicking
// it didn't navigate anywhere. The variant/active/large class list mirrors the modifier classes
// already in PillButton.module.css, so I went through and checked each variant name against the
// CSS file to make sure I wasn't introducing a class name that doesn't exist (styles[variant]
// silently returns undefined for typos, which would've been annoying to debug).
