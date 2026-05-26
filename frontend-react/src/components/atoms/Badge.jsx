import styles from './Badge.module.css';

/**
 * @param {Object} props
 * @param {'cat'|'new'|'read'|'shared'|'batch'} props.variant
 * @param {React.ReactNode} props.children
 * @param {React.CSSProperties} [props.style]
 */
export default function Badge({ variant, children, style }) {
  return (
    <span className={[styles.badge, styles[variant]].join(' ')} style={style}>
      {children}
    </span>
  );
}
