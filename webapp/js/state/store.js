// ─── Application State ────────────────────────────────────────
// Single centralized state object for the frontend.
// All modules import and mutate this shared object.

const state = {
  /** Bug data fetched from the backend (mirrors bugzilla_data.json). */
  data: null,

  /** Configuration fetched from the backend (mirrors bugzilla_config.json). */
  config: null,

  /** Currently active sub-tab in the All Bugs panel. */
  activeTab: 'to_work',

  /** Current sort column in the bug table (null = default order). */
  sortCol: null,

  /** Sort direction: 1 = ascending, -1 = descending. */
  sortDir: 1,

  /** Countdown seconds until next auto-refresh. */
  countdown: 60,

  /** Which optional columns are visible in the bug table. */
  visibleCols: {
    Priority: true,
    Assignee: true,
    Product: false,
    Activity: false,
    'Sub-Activity': false,
    Importance: false,
    Version: false,
    Deadline: false
  }
};

export default state;
