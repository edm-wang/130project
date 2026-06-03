// [GenAI Usage] Prompt:
// The three action buttons in SavedPaperRow (↗ Open, ✦ Summary, Edit category) were rendering
// but not doing anything on click. Wire them up: Open should open the paper's arXiv source URL
// in a new tab (falling back to /papers/:id if no URL), Summary should navigate to
// /papers/:id?tab=text, and Edit category should toggle an inline tag editor that lets the user
// add or remove categories per row with a duplicate guard — same pattern as ReadingListRow.
// Accept onOpen and onTextSummary as callbacks from the parent so routing stays out of the row.
// [GenAI Usage] Response Starts:
import { useState } from 'react';

import Badge from '../../components/atoms/Badge.jsx';
import styles from './SavedPaperRow.module.css';

export default function SavedPaperRow({ paper, onOpen, onTextSummary }) {
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
      <button
        type="button"
        className={styles.title}
        onClick={onOpen}
      >
        {paper.title}
      </button>
      <div className={styles.meta}>{paper.meta}</div>
      <div>
        {categories.map((cat) => (
          <Badge key={cat} variant="cat" style={{ marginRight: 4 }}>
            {cat}
          </Badge>
        ))}
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
          ✦ Summary
        </button>
        <button
          type="button"
          className={styles.action}
          onClick={() => setEditingCats((v) => !v)}
        >
          Edit category
        </button>
      </div>
    </div>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code here to mirror the same button-wiring pattern already done in ReadingListRow,
// keeping the two components consistent. The main difference is SavedPaperRow has no Remove button
// since the profile page is a preview of the reading list, not a full manager. I verified the
// onOpen/onTextSummary callbacks come from ProfilePage so the row stays route-agnostic, and
// confirmed the duplicate guard and functional setState toggle are carried over correctly.
