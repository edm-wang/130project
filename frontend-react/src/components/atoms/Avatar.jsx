import styles from './Avatar.module.css';

/**
 * @param {Object} props
 * @param {string} props.initials
 * @param {'sm'|'md'|'lg'} [props.size='md']
 * @param {'green'|'mint'|'lilac'|'peach'} [props.color='green']
 */
export default function Avatar({ initials, size = 'md', color = 'green' }) {
  return (
    <div className={[styles.avatar, styles[size], styles[color]].join(' ')}>
      {initials}
    </div>
  );
}
