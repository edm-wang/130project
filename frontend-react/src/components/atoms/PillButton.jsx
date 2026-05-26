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
