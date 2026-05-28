import Avatar from '../../components/atoms/Avatar.jsx';
import styles from './ProfileHero.module.css';

export default function ProfileHero({ profile, onEditClick }) {
  return (
    <div className={styles.hero}>
      <div className={styles.inner}>
        <div className={styles.top}>
          <Avatar initials={profile.initials} size="lg" color="green" />
          <div className={styles.identity}>
            <div className={styles.nameRow}>
              <div className={styles.name}>{profile.name}</div>
              <button type="button" className={styles.privacy}>
                ● {profile.publicProfile ? 'Public' : 'Private'}
              </button>
            </div>
            <div className={styles.affil}>{profile.affiliation}</div>
            <div className={styles.bio}>{profile.bio}</div>
            <div className={styles.linkRow}>
              {profile.links.map((link) => (
                <button
                  key={link.label}
                  type="button"
                  className={styles.linkChip}
                >
                  <span className={styles.dot} style={{ background: link.color }} />
                  {link.label}
                </button>
              ))}
            </div>
          </div>
          <button type="button" className={styles.editBtn} onClick={onEditClick}>
            Edit profile
          </button>
        </div>
      </div>
    </div>
  );
}
