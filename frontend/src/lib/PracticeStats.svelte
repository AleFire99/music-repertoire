<script lang="ts">
  import type { PracticeGoal, PracticeStats } from './api'
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
</script>

{#if goal}
  <div class="goal-row">
    <div class="goal-rule">
      <span class="goal-fill" style={`width: ${goalPct}%`}></span>
    </div>
    <span class="goal-fraction numeral">
      {formatHours(goal.minutes_this_week)} / {formatHours(goal.target_minutes)}
      <span class="unit caption">hrs this week</span>
    </span>
  </div>
{/if}

{#if stats.pieces.length === 0}
  <p class="empty">No practice sessions logged yet.</p>
{:else}
  <div class="stat-strip">
    <div class="stat-cell">
      <span class="numeral">{stats.total_minutes}</span>
      <span class="caption">min total</span>
    </div>
    <div class="stat-cell">
      <span class="numeral">{stats.minutes_this_week}</span>
      <span class="caption">min this week</span>
    </div>
    <div class="stat-cell">
      <span class="numeral">{stats.minutes_this_month}</span>
      <span class="caption">min this month</span>
    </div>
    <div class="stat-cell">
      <span class="numeral accent">{stats.current_streak_days}</span>
      <span class="caption">day{stats.current_streak_days === 1 ? '' : 's'} streak</span>
    </div>
    <div class="stat-cell">
      <span class="numeral">{stats.longest_streak_days}</span>
      <span class="caption">best streak</span>
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
  <div class="editorial-columns" class:single={stats.recently_practiced.length === 0 || stats.neglected.length === 0}>
    {#if stats.recently_practiced.length > 0}
      <div class="col">
        <h3>Recently practiced</h3>
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
        <h3>Neglected</h3>
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
  .goal-row {
    display: flex;
    align-items: baseline;
    gap: var(--space-4);
    margin-bottom: var(--space-5);
    flex-wrap: wrap;
  }
  .goal-rule {
    position: relative;
    flex: 1 1 10rem;
    min-width: 6rem;
    height: 1px;
    background: var(--border);
  }
  .goal-fill {
    position: absolute;
    top: -1px;
    left: 0;
    height: 3px;
    background: var(--accent);
    width: 0;
    transition: width 200ms ease;
  }
  @media (prefers-reduced-motion: reduce) {
    .goal-fill {
      transition: none;
    }
  }
  .goal-fraction {
    font-size: var(--text-lg);
    white-space: nowrap;
  }
  .unit {
    margin-left: var(--space-2);
  }

  .stat-strip {
    display: flex;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    margin-bottom: var(--space-5);
  }
  .stat-cell {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: var(--space-4) var(--space-4) var(--space-3) var(--space-4);
    border-left: 1px solid var(--border);
  }
  .stat-cell:first-child {
    border-left: none;
    padding-left: 0;
  }
  .stat-cell .numeral {
    font-size: var(--text-2xl);
  }

  .index-table {
    margin-bottom: var(--space-5);
  }
  .piece-title {
    font-family: var(--font-serif);
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
  .editorial-columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 var(--space-6);
  }
  .editorial-columns.single {
    grid-template-columns: 1fr;
  }
  .editorial-columns .col + .col {
    border-left: 1px solid var(--border);
    padding-left: var(--space-6);
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
    border-bottom: 1px solid var(--border);
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
