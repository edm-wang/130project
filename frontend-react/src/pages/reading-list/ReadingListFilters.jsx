import Chip from '../../components/atoms/Chip.jsx';
import styles from './ReadingListFilters.module.css';

export default function ReadingListFilters({ chips, active, onChange }) {
  return (
    <div className={styles.row}>
      {chips.map((c) => (
        <Chip
          key={c}
          outline
          selected={active === c}
          onClick={() => onChange(c)}
        >
          {c}
        </Chip>
      ))}
    </div>
  );
}
