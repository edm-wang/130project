import { useState } from 'react';

import PageTabs from '../../components/chrome/PageTabs.jsx';
import ActivityStats from './ActivityStats.jsx';
import AddInterestForm from './AddInterestForm.jsx';
import EditProfileForm from './EditProfileForm.jsx';
import InterestSection from './InterestSection.jsx';
import NotificationSettings from './NotificationSettings.jsx';
import ProfileHero from './ProfileHero.jsx';
import SavedPaperRow from './SavedPaperRow.jsx';
import {
  activity,
  editFields,
  interests,
  profile,
  savedPapers,
} from './mockData.js';
import styles from './ProfilePage.module.css';

const TABS = [
  { id: 'interests', label: 'Research Interests' },
  { id: 'reading', label: 'Reading List' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'edit', label: 'Edit Profile' },
];

export default function ProfilePage() {
  const [tab, setTab] = useState('interests');

  return (
    <div>
      <h2 className="sr-only">Paper Aggregator — user profile page</h2>

      <ProfileHero profile={profile} />
      <PageTabs tabs={TABS} active={tab} onChange={setTab} />

      <div className={styles.body}>
        <div>
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.cardTitle}>Research Interests</div>
              <button type="button" className={styles.cardAction}>
                + Add new
              </button>
            </div>

            <InterestSection
              label="Fields"
              kind="field"
              values={interests.field}
            />
            <InterestSection
              label="Topics"
              kind="topic"
              values={interests.topic}
            />
            <InterestSection
              label="Authors"
              kind="author"
              values={interests.author}
            />
            <InterestSection
              label="Keywords"
              kind="keyword"
              values={interests.keyword}
            />

            <AddInterestForm />
          </div>

          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <div className={styles.cardTitle}>
                Reading List · {savedPapers.length} saved
              </div>
              <button type="button" className={styles.cardAction}>
                View all →
              </button>
            </div>
            {savedPapers.map((p) => (
              <SavedPaperRow key={p.id} paper={p} />
            ))}
          </div>
        </div>

        <aside>
          <ActivityStats stats={activity} />
          <NotificationSettings />
          <EditProfileForm initial={editFields} />
        </aside>
      </div>

      {/* Note: PageTabs are visual-only in this port; switching tabs doesn't
          reroute or rerender different content. Wire up once back-end is
          ready. */}
      {tab === '__unused__' ? null : null}
    </div>
  );
}
