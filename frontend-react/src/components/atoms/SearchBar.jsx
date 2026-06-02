// [GenAI Usage] Prompt: Create a reusable SearchBar component for the navbar that allows users
// to search through papers by title, authors, and abstract. The component should include a
// search icon that's clickable (not just decorative), proper form handling with Enter key
// support, and visual feedback on hover. I wanted the search icon to submit the form just
// like pressing Enter does, since users might expect to click it rather than use keyboard.
// [GenAI Usage] LLM response begins:
import { useState } from 'react';
import styles from './SearchBar.module.css';

export default function SearchBar({ onSearch, placeholder = 'Search papers...' }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleChange = (e) => {
    setQuery(e.target.value);
  };

  return (
    <form onSubmit={handleSubmit} className={styles.searchForm}>
      <div className={styles.searchWrapper}>
        <button
          type="submit"
          className={styles.searchIconButton}
          aria-label="Search"
        >
          <svg
            className={styles.searchIcon}
            width="14"
            height="14"
            viewBox="0 0 14 14"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M6 11C8.76142 11 11 8.76142 11 6C11 3.23858 8.76142 1 6 1C3.23858 1 1 3.23858 1 6C1 8.76142 3.23858 11 6 11Z"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M13 13L9.5 9.5"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
        <input
          type="text"
          value={query}
          onChange={handleChange}
          placeholder={placeholder}
          className={styles.searchInput}
          aria-label="Search papers"
        />
      </div>
    </form>
  );
}
// [GenAI Usage] LLM response ends
// [GenAI Reflection] I asked Claude Code to scaffold this search component because I needed
// to match the existing design system tokens and component patterns used throughout the app.
// Initially the search icon was just decorative (pointer-events: none), but after testing
// I realized users would naturally try to click it, so I had Claude convert it to a submit
// button with hover states. I verified the component integrates properly with the form's
// onSubmit handler and that the controlled input state updates correctly.
