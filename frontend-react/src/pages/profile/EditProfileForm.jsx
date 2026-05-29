// [GenAI Usage] Prompt:
// Rewrite EditProfileForm to add an onSave prop that the parent can wire to the backend. Wire
// the Save button with saving/saved UI states (shows "Saving…" during the async call, "Saved!"
// briefly on success). Remove the LinkedIn and Google Scholar URL fields and their isValidUrl
// validation. Make the email field read-only since it comes from Supabase Auth.
// [GenAI Usage] Response Starts:
import { useState } from 'react';

import Widget from '../../components/widgets/Widget.jsx';
import styles from './EditProfileForm.module.css';

export default function EditProfileForm({ initial, onSave }) {
  const [form, setForm] = useState({
    displayName: (initial && initial.displayName) || '',
    affiliation: (initial && initial.affiliation) || '',
    bio: (initial && initial.bio) || '',
    email: (initial && initial.email) || '',
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function handleSave() {
    if (!onSave) return;
    setSaving(true);
    setSaved(false);
    try {
      await onSave({ displayName: form.displayName, affiliation: form.affiliation, bio: form.bio });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  }

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
        <div className={styles.label}>Email <span style={{ fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>(login)</span></div>
        <input
          className={[styles.input, styles.inputReadOnly].join(' ')}
          value={form.email}
          readOnly
        />
      </div>
      <button
        type="button"
        className={styles.save}
        onClick={handleSave}
        disabled={saving}
      >
        {saving ? 'Saving…' : saved ? 'Saved!' : 'Save changes'}
      </button>
    </Widget>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code to rewrite EditProfileForm because the changes were straightforward but
// spread across multiple parts of the file (removing fields, wiring the button, adding state).
// I verified that the form initialises with safe fallbacks ((initial && initial.x) || '')
// so it doesn't crash if rendered before the profile loads, and confirmed that the try/finally
// pattern always clears the saving flag even when onSave throws.
