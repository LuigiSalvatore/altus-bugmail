// ─── Shared Constants ─────────────────────────────────────────
// Centralized definitions used across multiple modules.

/** All optional columns available in the bug table. */
export const ALL_COLS = [
  'Priority', 'Assignee', 'Product', 'Activity',
  'Sub-Activity', 'Importance', 'Version', 'Deadline', 'Component'
];

/** Maps sub-tab keys to their data-store property names. */
export const TAB_KEYS = {
  assigned: 'assigned_bugs',
  review: 'review_bugs',
  resolved_fixed: 'resolved_fixed_bugs',
  resolved_implemented: 'resolved_implemented_bugs',
  all: 'all_bugs'
};

/** Maps display column names to bug object field names. */
export const COL_FIELD = {
  ID: 'id',
  Summary: 'summary',
  Status: 'status',
  Priority: 'priority',
  Assignee: 'assigned_to',
  Product: 'product',
  Activity: 'activity',
  'Sub-Activity': 'sub_activity',
  Importance: 'importance',
  Version: 'version',
  Deadline: 'deadline',
  Component: 'component'
};

// ─── LocalStorage Keys ────────────────────────────────────────

export const LS_SUB_PRIO = 'bz_local_sub_prio';
export const LS_CS       = 'bz_commit_state';
export const LS_BR       = 'bz_branches';
export const LS_RE       = 'bz_repos';
export const LS_FH       = 'bz_file_hist';
export const LS_SORT_COL = 'bz_sort_col';
export const LS_SORT_DIR = 'bz_sort_dir';

// ─── Defaults ─────────────────────────────────────────────────

export const DEF_BRANCH = 'v1.14.x.x/develop';
export const DEF_REPO   = 'linux-multi-target';
