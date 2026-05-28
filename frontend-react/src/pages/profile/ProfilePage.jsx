// [GenAI Usage] Prompt:
// Rewire ProfilePage to replace all mock data imports with useProfile, useInterests, and
// useSavedPapers hooks. Implement functional tab switching (Research Interests / Reading List /
// Edit Profile — remove Notifications tab). Wire EditProfileForm.onSave, AddInterestForm.onAdd,
// and InterestSection.onRemove to the real hook callbacks. Show a "complete your profile" banner
// when useProfile returns no-profile status. Replace ActivityStats with a "coming soon" widget.
// [GenAI Usage] Response Starts:
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import PageTabs from '../../components/chrome/PageTabs.jsx';
import Widget from '../../components/widgets/Widget.jsx';
import AddInterestForm from './AddInterestForm.jsx';
import EditProfileForm from './EditProfileForm.jsx';
import InterestSection from './InterestSection.jsx';
import ProfileHero from './ProfileHero.jsx';
import SavedPaperRow from './SavedPaperRow.jsx';
import useInterests from './useInterests.js';
import useProfile from './useProfile.js';
import useSavedPapers from '../reading-list/useSavedPapers.js';
import styles from './ProfilePage.module.css';

const TABS = [
  { id: 'interests', label: 'Research Interests' },
  { id: 'reading', label: 'Reading List' },
  { id: 'edit', label: 'Edit Profile' },
];

function computeInitials(displayName, email) {
  const source = displayName || email || '';
  return source
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase() || '?';
}

export default function ProfilePage() {
  const [searchParams] = useSearchParams();
  const [tab, setTab] = useState(searchParams.get('tab') || 'interests');

  const { status: profileStatus, profile, save: saveProfile } = useProfile();
  const { status: interestsStatus, interests, add: addInterest, remove: removeInterest } = useInterests();
  const { savedPapers } = useSavedPapers();

  const heroProfile = {
    initials: computeInitials(profile?.display_name, profile?.email),
    name: profile?.display_name || 'Your Profile',
    affiliation: profile?.institution || '',
    bio: profile?.bio || '',
    publicProfile: false,
    links: [],
  };

  // Group flat interests list by type for InterestSection display.
  const byType = { field: [], topic: [], author: [], keyword: [] };
  interests.forEach((i) => {
    if (byType[i.interest_type]) byType[i.interest_type].push(i);
  });

  function makeRemoveHandler(type) {
    return (val) => {
      const found = byType[type].find((i) => i.value === val);
      if (found) removeInterest(found.id);
    };
  }

  const editInitial = {
    displayName: profile?.display_name || '',
    affiliation: profile?.institution || '',
    bio: profile?.bio || '',
    email: profile?.email || '',
  };

  return (
    <div>
      <h2 className="sr-only">Paper Aggregator — user profile page</h2>

      {profileStatus === 'no-profile' && (
        <div style={{ padding: '10px 16px', background: 'var(--color-surface-raised)', borderBottom: '1px solid var(--color-border)', fontSize: 13 }}>
          Welcome! Complete your profile to get personalized recommendations.{' '}
          <button type="button" className={styles.cardAction} onClick={() => setTab('edit')}>
            Set up now →
          </button>
        </div>
      )}

      <ProfileHero profile={heroProfile} onEditClick={() => setTab('edit')} />
      <PageTabs tabs={TABS} active={tab} onChange={setTab} />

      <div className={styles.body}>
        <div>
          {/* RESEARCH INTERESTS TAB */}
          {tab === 'interests' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <div className={styles.cardTitle}>Research Interests</div>
              </div>

              {interestsStatus === 'loading' && (
                <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
                  Loading interests…
                </div>
              )}

              {interestsStatus === 'ready' && (
                <>
                  <InterestSection
                    label="Fields"
                    kind="field"
                    values={byType.field.map((i) => i.value)}
                    onRemove={makeRemoveHandler('field')}
                  />
                  <InterestSection
                    label="Topics"
                    kind="topic"
                    values={byType.topic.map((i) => i.value)}
                    onRemove={makeRemoveHandler('topic')}
                  />
                  <InterestSection
                    label="Authors"
                    kind="author"
                    values={byType.author.map((i) => i.value)}
                    onRemove={makeRemoveHandler('author')}
                  />
                  <InterestSection
                    label="Keywords"
                    kind="keyword"
                    values={byType.keyword.map((i) => i.value)}
                    onRemove={makeRemoveHandler('keyword')}
                  />
                  <AddInterestForm onAdd={(val, kind) => addInterest(val, kind)} />
                </>
              )}

              {interestsStatus === 'no-token' && (
                <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
                  Sign in to manage your research interests.
                </div>
              )}

              {(interestsStatus === 'error' || interestsStatus === 'network-error' || interestsStatus === 'unauthorized') && (
                <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
                  Could not load interests. Try refreshing.
                </div>
              )}
            </div>
          )}

          {/* READING LIST TAB */}
          {tab === 'reading' && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <div className={styles.cardTitle}>
                  Reading List · {savedPapers.length} saved
                </div>
                <button type="button" className={styles.cardAction}>
                  View all →
                </button>
              </div>
              {savedPapers.length === 0 && (
                <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
                  No saved papers yet.
                </div>
              )}
              {savedPapers.map((p) => (
                <SavedPaperRow key={p.id} paper={p} />
              ))}
            </div>
          )}

          {/* EDIT PROFILE TAB */}
          {tab === 'edit' && profileStatus === 'loading' && (
            <div className={styles.card}>
              <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
                Loading profile…
              </div>
            </div>
          )}
          {tab === 'edit' && (profileStatus === 'ready' || profileStatus === 'no-profile') && (
            <EditProfileForm initial={editInitial} onSave={saveProfile} />
          )}
          {tab === 'edit' && (profileStatus === 'no-token' || profileStatus === 'unauthorized') && (
            <div className={styles.card}>
              <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
                Sign in to edit your profile.
              </div>
            </div>
          )}
        </div>

        <aside>
          <Widget title="Activity">
            <div style={{ fontSize: 13, color: 'var(--color-text-tertiary)', padding: '8px 0' }}>
              Activity stats coming soon.
            </div>
          </Widget>
        </aside>
      </div>
    </div>
  );
}
// [GenAI Usage] Response Ends
// [GenAI Usage] Reflection:
// I used Claude Code for this rewrite because it required coordinating three hooks, restructuring
// the entire tab-conditional layout, and removing a significant amount of dead code — all at once.
// I reviewed the interest grouping logic (byType + makeRemoveHandler) to confirm that finding an
// interest by value within a type is safe given the unique constraint on (user_id, interest_type,
// normalized_value). I also checked that EditProfileForm is only rendered when profileStatus is
// 'ready' or 'no-profile', which guarantees the form mounts with correct initial values and
// avoids a stale-state issue from useState only reading its initialiser once.
