import { useState } from 'react';

import Chip from '../atoms/Chip.jsx';
import Toggle from '../atoms/Toggle.jsx';
import Widget from './Widget.jsx';
import styles from './Widget.module.css';

const FREQUENCIES = ['Daily', 'Weekly', 'Monthly'];

export default function EmailDigestWidget({
  initialEnabled = true,
  initialFrequency = 'Weekly',
}) {
  const [enabled, setEnabled] = useState(initialEnabled);
  const [frequency, setFrequency] = useState(initialFrequency);

  return (
    <Widget title="Email Digest">
      <div className={styles.emailRow}>
        <span style={{ fontSize: 12, color: 'var(--color-text-secondary)' }}>
          Enabled
        </span>
        <Toggle on={enabled} onChange={setEnabled} ariaLabel="Email digest toggle" />
      </div>
      <div
        style={{
          fontSize: 11,
          color: 'var(--color-text-tertiary)',
          marginBottom: 6,
        }}
      >
        Frequency
      </div>
      <div style={{ display: 'flex', gap: 4 }}>
        {FREQUENCIES.map((f) => (
          <Chip
            key={f}
            selected={frequency === f}
            onClick={() => setFrequency(f)}
          >
            {f}
          </Chip>
        ))}
      </div>
    </Widget>
  );
}
