<script lang="ts">
  import type { DayPracticeMinutes, PracticeGoal, PracticeStats } from './api'
  import Icon from './Icon.svelte'

  let { stats, goal = null }: { stats: PracticeStats; goal?: PracticeGoal | null } = $props()

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString()
  }

  function formatHours(minutes: number): string {
    return (minutes / 60).toFixed(1)
  }

  const goalPct = $derived(
    goal ? Math.min(100, (goal.minutes_this_week / goal.target_minutes) * 100) : 0,
  )

  const HEAT_LEVELS = ['var(--border)', 'var(--accent-200)', 'var(--accent-400)', 'var(--accent)', 'var(--accent-700)']

  function heatLevel(day: DayPracticeMinutes): string {
    const m = day.total_minutes
    const level = m === 0 ? 0 : m < 15 ? 1 : m < 30 ? 2 : m < 60 ? 3 : 4
    return HEAT_LEVELS[level]
  }
</script>

{#if stats.pieces.length === 0}
  <p class="empty">No practice sessions logged yet.</p>
{:else}
  <div class="stat-strip">
    <div class="stat-cell">
      <span class="caption">Total practice</span>
      <span class="numeral">{formatHours(stats.total_minutes)}<span class="unit-inline">h</span></span>
    </div>
    <div class="stat-cell">
      <span class="caption">This week</span>
      <span class="numeral">{formatHours(stats.minutes_this_week)}<span class="unit-inline">h</span></span>
    </div>
    <div class="stat-cell">
      <span class="caption">This month</span>
      <span class="numeral">{formatHours(stats.minutes_this_month)}<span class="unit-inline">h</span></span>
    </div>
    <div class="stat-cell highlight">
      <span class="caption"><Icon name="streak" size={13} /> Streak</span>
      <span class="numeral">{stats.current_streak_days}<span class="unit-inline">day{stats.current_streak_days === 1 ? '' : 's'}</span></span>
      <span class="best">Best ever is {stats.longest_streak_days}</span>
    </div>
  </div>

  <div class="stats-columns">
    <div>
      <div class="col-head">
        <h3>Weekly goal</h3>
        {#if goal}<span class="caption">{formatHours(goal.minutes_this_week)}h / {formatHours(goal.target_minutes)}h</span>{/if}
      </div>
      <div class="goal-track"><div class="goal-track-fill" style={`width: ${goalPct}%`}></div></div>
    </div>
    <div>
      <div class="col-head">
        <h3>Consistency</h3>
        <span class="caption">Last 14 weeks</span>
      </div>
      <div class="heatmap">
        {#each stats.consistency_heatmap as day (day.date)}
          <div class="heatmap-cell" style={`background:${heatLevel(day)}`} title="{day.date}: {day.total_minutes} min"></div>
        {/each}
      </div>
      <div class="heatmap-legend">
        <span class="caption">Less</span>
        <span class="legend-swatches">
          {#each HEAT_LEVELS as bg (bg)}
            <i style={`background:${bg}`}></i>
          {/each}
        </span>
        <span class="caption">More</span>
      </div>
    </div>
  </div>

  <table class="index-table">
    <thead>
      <tr>
        <th>Piece</th>
        <th class="num">Hours</th>
        <th class="num">Sessions</th>
        <th class="num">Last practiced</th>
      </tr>
    </thead>
    <tbody>
      {#each stats.pieces as piece (piece.piece_id)}
        <tr>
          <td>
            {#if piece.sections.length > 0}
              <details>
                <summary>
                  <span class="disclosure-icon" aria-hidden="true"><Icon name="disclose" size={12} /></span>
                  <span class="piece-title">{piece.piece_title}</span>
                </summary>
                <ul class="sections">
                  {#each piece.sections as section (section.section)}
                    <li>
                      {section.section}
                      <span class="readout">{section.total_minutes}</span> min
                    </li>
                  {/each}
                </ul>
              </details>
            {:else}
              <span class="piece-title no-disclosure">{piece.piece_title}</span>
            {/if}
          </td>
          <td class="num"><span class="readout">{formatHours(piece.total_minutes)}</span></td>
          <td class="num"><span class="readout">{piece.session_count}</span></td>
          <td class="num">{formatDate(piece.last_practiced_at)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}

{#if stats.recently_practiced.length > 0 || stats.neglected.length > 0}
  <div class="stats-columns" class:single={stats.recently_practiced.length === 0 || stats.neglected.length === 0}>
    {#if stats.recently_practiced.length > 0}
      <div class="col">
        <h3>Fresh in the hands</h3>
        <ul class="col-list">
          {#each stats.recently_practiced as piece (piece.piece_id)}
            <li>
              <span class="piece-title">{piece.piece_title}</span>
              <span class="when">{formatDate(piece.last_practiced_at)}</span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
    {#if stats.neglected.length > 0}
      <div class="col">
        <h3>Slipping away</h3>
        <ul class="col-list">
          {#each stats.neglected as piece (piece.piece_id)}
            <li>
              <span class="piece-title">{piece.piece_title}</span>
              <span class="when danger">
                {piece.last_practiced_at ? formatDate(piece.last_practiced_at) : 'never practiced'}
              </span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}
  </div>
{/if}

<style>
  .unit-inline {
    font-size: var(--text-md);
    opacity: 0.55;
    margin-left: 2px;
  }

  .stat-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    border-top: var(--border-width-strong) solid var(--ink);
    border-bottom: var(--border-width) solid var(--border);
    margin-bottom: var(--space-6);
  }
  .stat-cell {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: var(--space-4);
    border-left: var(--border-width) solid var(--border);
  }
  .stat-cell:first-child {
    border-left: none;
  }
  .stat-cell .numeral {
    font-size: var(--text-2xl);
  }
  .stat-cell.highlight {
    background: var(--accent);
    color: var(--accent-contrast);
  }
  .stat-cell.highlight .caption,
  .stat-cell.highlight .numeral,
  .stat-cell.highlight .best {
    color: var(--accent-contrast);
  }
  .stat-cell.highlight .caption {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    opacity: 0.9;
  }
  .best {
    font-size: var(--text-xs);
    color: var(--ink-faint);
  }

  .stats-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-6) var(--space-6);
    margin-bottom: var(--space-6);
    align-items: start;
  }
  .stats-columns.single {
    grid-template-columns: 1fr;
  }
  .stats-columns .col + .col {
    border-left: var(--border-width) solid var(--border);
    padding-left: var(--space-6);
  }
  .col-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: var(--space-3);
  }

  .goal-track {
    height: 10px;
    background: var(--border);
  }
  .goal-track-fill {
    height: 100%;
    background: var(--accent);
  }

  .heatmap {
    display: grid;
    grid-template-rows: repeat(7, 13px);
    grid-auto-flow: column;
    grid-auto-columns: 13px;
    gap: 4px;
  }
  .heatmap-cell {
    width: 13px;
    height: 13px;
  }
  .heatmap-legend {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-4);
  }
  .legend-swatches {
    display: flex;
    gap: 4px;
  }
  .legend-swatches i {
    width: 12px;
    height: 12px;
    display: block;
  }

  .index-table {
    margin-bottom: var(--space-6);
  }
  .piece-title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
  }
  .no-disclosure {
    padding-left: calc(12px + var(--space-1));
  }
  details summary {
    cursor: pointer;
    list-style: none;
    display: flex;
    align-items: baseline;
    gap: var(--space-1);
  }
  details summary::-webkit-details-marker {
    display: none;
  }
  .disclosure-icon {
    display: inline-flex;
    color: var(--ink-faint);
    transition: transform 150ms ease;
  }
  details[open] .disclosure-icon {
    transform: rotate(90deg);
  }
  @media (prefers-reduced-motion: reduce) {
    .disclosure-icon {
      transition: none;
    }
  }
  .sections {
    list-style: none;
    padding-left: calc(12px + var(--space-2));
    margin: var(--space-1) 0 0;
    font-size: var(--text-sm);
    color: var(--ink-soft);
  }
  .sections li {
    padding: var(--space-1) 0;
  }

  h3 {
    margin-bottom: var(--space-2);
  }
  .col-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .col-list li {
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-2) 0;
    border-bottom: var(--border-width) solid var(--border);
  }
  .col-list li:last-child {
    border-bottom: none;
  }
  .when {
    color: var(--ink-faint);
    font-size: var(--text-xs);
    white-space: nowrap;
  }
  .when.danger {
    color: var(--danger);
  }
</style>
