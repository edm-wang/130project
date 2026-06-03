// [GenAI Usage] Prompt:
// The four action buttons in ReadingListRow (↗ Open, ✦ Text summary, Edit category, Remove)
// were rendering but not doing anything on click. Wire them up: Open and Text summary should
// navigate to /papers/:id and /papers/:id?tab=text respectively using callbacks passed from
// the parent. Remove should call an onRemove callback. Edit category should toggle an inline
// editor that lets the user add new categories (with duplicate guard) and remove existing ones
// via a × button — keep the category state local to the row since there's no backend endpoint
// for per-paper category edits.
// [GenAI Usage] Response Starts:
import { useState } from 'react';

import Badge from '../../components/atoms/Badge.jsx';
import styles from './ReadingListRow.module.css';

export default function ReadingListRow({ paper, index, onOpen, onTextSummary, onRemove }) {
  const [editingCats, setEditingCats] = useState(false);
  const [categories, setCategories] = useState(paper.categories);
  const [catInput, setCatInput] = useState('');

  function addCategory(e) {
    e.preventDefault();
    const val = catInput.trim();
    if (val && !categories.includes(val)) {
      setCategories([...categories, val]);
    }
    setCatInput('');
  }

  function removeCategory(cat) {
    setCategories(categories.filter((c) => c !== cat));
  }

  return (
    <div className={styles.row}>
      <div className={styles.num}>{index + 1}</div>
      <div className={styles.content}>
        <button
          type="button"
          className={styles.title}
          onClick={onOpen}
        >
          {paper.title}
        </button>
        <div className={styles.meta}>{paper.meta}</div>
        <div className={styles.badges}>
          {categories.map((c) => (
            <Badge key={c} variant="cat">
              {c}
            </Badge>
          ))}
          {paper.isNew ? <Badge variant="new">New</Badge> : null}
          {paper.read ? <Badge variant="read">Read</Badge> : null}
        </div>

        {editingCats && (
          <div className={styles.catEditor}>
            <div className={styles.catChips}>
              {categories.map((c) => (
                <span key={c} className={styles.catChip}>
                  {c}
                  <button
                    type="button"
                    className={styles.catChipRemove}
                    onClick={() => removeCategory(c)}
                    aria-label={`Remove ${c}`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <form onSubmit={addCategory} className={styles.catForm}>
              <input
                className={styles.catInput}
                value={catInput}
                onChange={(e) => setCatInput(e.target.value)}
                placeholder="Add category…"
              />
              <button type="submit" className={styles.catAdd}>Add</button>
              <button type="button" className={styles.catDone} onClick={() => setEditingCats(false)}>Done</button>
            </form>
          </div>
        )}

        <div className={styles.actions}>
          <button type="button" className={styles.action} onClick={onOpen}>
            ↗ Open
          </button>
          <button type="button" className={styles.action} onClick={onTextSummary}>
            ✦ Text summary
          </button>
          <button
            type="button"
            className={styles.action}
            onClick={() => setEditingCats((v) => !v)}
          >
            Edit category
          </button>
          <button type="button" className={`${styles.action} ${styles.actionRemove}`} onClick={onRemove}>
            Remove
          </button>
        </div>
      </div>
    </div>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code here because wiring all four buttons at once meant touching the component
// signature, adding local state, and writing a small inline form — all in one go, which is easy
// to get subtly wrong. A few things I checked manually: the duplicate guard in addCategory uses
// Array.includes so it won't silently add the same tag twice; the × remove button has an
// aria-label so it's accessible; and the Edit category toggle uses a functional setState updater
// (v => !v) rather than closing over the stale value. I also confirmed the onOpen/onTextSummary
// callbacks come from ReadingListPage rather than being constructed inside the row, so they don't
// create a new function reference on every render.
