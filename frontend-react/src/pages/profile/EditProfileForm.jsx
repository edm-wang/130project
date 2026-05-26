import { useState } from 'react';

import Widget from '../../components/widgets/Widget.jsx';
import styles from './EditProfileForm.module.css';

function isValidUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === 'http:' || u.protocol === 'https:';
  } catch {
    return false;
  }
}

export default function EditProfileForm({ initial }) {
  const [form, setForm] = useState({ ...initial });

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  return (
    <Widget title="Edit Profile">
      <div className={styles.row}>
        <div className={styles.label}>Display name</div>
        <input
          className={styles.input}
          value={form.displayName}
          onChange={update('displayName')}
        />
      </div>
      <div className={styles.row}>
        <div className={styles.label}>Affiliation</div>
        <input
          className={styles.input}
          value={form.affiliation}
          onChange={update('affiliation')}
        />
      </div>
      <div className={styles.row}>
        <div className={styles.label}>Bio</div>
        <textarea
          className={[styles.input, styles.textarea].join(' ')}
          rows={3}
          value={form.bio}
          onChange={update('bio')}
        />
      </div>
      <div className={styles.row}>
        <div className={styles.label}>LinkedIn URL</div>
        <input
          className={styles.input}
          value={form.linkedIn}
          onChange={update('linkedIn')}
        />
        {isValidUrl(form.linkedIn) ? (
          <div
            className={[styles.urlStatus, styles.urlStatusValid].join(' ')}
          >
            ✓ Valid URL
          </div>
        ) : null}
      </div>
      <div className={styles.row}>
        <div className={styles.label}>Google Scholar URL</div>
        <input
          className={styles.input}
          value={form.scholar}
          onChange={update('scholar')}
        />
        {isValidUrl(form.scholar) ? (
          <div
            className={[styles.urlStatus, styles.urlStatusValid].join(' ')}
          >
            ✓ Valid URL
          </div>
        ) : null}
      </div>
      <div className={styles.row}>
        <div className={styles.label}>Contact email</div>
        <input
          className={styles.input}
          value={form.email}
          onChange={update('email')}
        />
      </div>
      <button type="button" className={styles.save}>
        Save changes
      </button>
    </Widget>
  );
}
