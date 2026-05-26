import { useState } from 'react';

import styles from './AddInterestForm.module.css';

const KINDS = ['Field', 'Topic', 'Keyword', 'Author'];

/**
 * @param {Object} props
 * @param {(value: string, kind: string) => void} [props.onAdd]
 */
export default function AddInterestForm({ onAdd }) {
  const [value, setValue] = useState('');
  const [kind, setKind] = useState('Keyword');

  const submit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    onAdd && onAdd(trimmed, kind.toLowerCase());
    setValue('');
  };

  return (
    <div className={styles.section}>
      <div className={styles.label}>Add a new interest</div>
      <form className={styles.row} onSubmit={submit}>
        <input
          className={styles.input}
          placeholder="e.g. contrastive learning"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <select
          className={styles.select}
          value={kind}
          onChange={(e) => setKind(e.target.value)}
        >
          {KINDS.map((k) => (
            <option key={k}>{k}</option>
          ))}
        </select>
        <button type="submit" className={styles.submit}>
          Add
        </button>
      </form>
    </div>
  );
}
