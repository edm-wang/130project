import { useState } from 'react';

import Chip from '../../components/atoms/Chip.jsx';
import Toggle from '../../components/atoms/Toggle.jsx';
import Widget from '../../components/widgets/Widget.jsx';

const FREQUENCIES = ['Daily', 'Weekly', 'Monthly'];

const ROW_STYLES = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: '8px 0',
  borderBottom: '0.5px solid var(--color-border-tertiary)',
  fontSize: 13,
  color: 'var(--color-text-secondary)',
};

export default function NotificationSettings() {
  const [emailOn, setEmailOn] = useState(true);
  const [publicProfile, setPublicProfile] = useState(true);
  const [frequency, setFrequency] = useState('Weekly');

  return (
    <Widget title="Notifications">
      <div style={ROW_STYLES}>
        Email digest
        <Toggle on={emailOn} onChange={setEmailOn} ariaLabel="Email digest" />
      </div>
      <div style={{ padding: '6px 0 10px' }}>
        <div
          style={{
            fontSize: 11,
            color: 'var(--color-text-tertiary)',
            marginBottom: 5,
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
      </div>
      <div
        style={{
          ...ROW_STYLES,
          borderTop: '0.5px solid var(--color-border-tertiary)',
          borderBottom: 'none',
        }}
      >
        Profile public
        <Toggle
          on={publicProfile}
          onChange={setPublicProfile}
          ariaLabel="Profile public"
        />
      </div>
    </Widget>
  );
}
