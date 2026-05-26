import styles from './Slides.module.css';

export default function IntroSlide({ active }) {
  return (
    <div
      className={[styles.slide, styles.s0, active ? styles.active : ''].join(' ').trim()}
    >
      <div className={styles.s0Badge}>DAILY DIGEST · APR 23, 2026</div>
      <div className={styles.s0Title}>
        Today's Research Feed
        <br />
        12 Papers · AI &amp; Machine Learning
      </div>
      <div className={styles.s0Sub}>WESTLAKE UNIVERSITY OF SCIENCE · ALEX CHEN</div>
    </div>
  );
}
