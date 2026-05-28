import { Link } from 'react-router-dom';

import Widget from './Widget.jsx';
import styles from './Widget.module.css';

/**
 * @param {Object} props
 * @param {{ label: string, to: string }[]} props.links
 */
export default function QuickLinksWidget({ links }) {
  return (
    <Widget title="Quick Links">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {links.map((link) => (
          <Link key={link.label} to={link.to} className={styles.linkBtn}>
            → {link.label}
          </Link>
        ))}
      </div>
    </Widget>
  );
}
