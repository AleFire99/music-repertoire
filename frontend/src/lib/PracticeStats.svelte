<script lang="ts">
  import type { PracticeGoal, PracticeStats } from './api'

  let { stats, goal = null }: { stats: PracticeStats; goal?: PracticeGoal | null } = $props()

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString()
  }

  function formatHours(minutes: number): string {
    return (minutes / 60).toFixed(1)
  }
</script>

{#if goal}
  <p class="goal-progress">
    Weekly goal:
    <strong>{formatHours(goal.minutes_this_week)} / {formatHours(goal.target_minutes)} hrs</strong>
    <span class="bar" style={`--pct: ${Math.min(100, (goal.minutes_this_week / goal.target_minutes) * 100)}%`}
      ><span class="bar-fill"></span></span
    >
  </p>
{/if}

{#if stats.pieces.length === 0}
  <p class="empty">No practice sessions logged yet.</p>
{:else}
  <div class="totals">
    <div class="stat">
      <span class="readout readout-lg">{stats.total_minutes}</span>
      <span class="stat-label">min total</span>
    </div>
    <div class="stat">
      <span class="readout readout-lg">{stats.minutes_this_week}</span>
      <span class="stat-label">min this week</span>
    </div>
    <div class="stat">
      <span class="readout readout-lg">{stats.minutes_this_month}</span>
      <span class="stat-label">min this month</span>
    </div>
    <div class="stat">
      <span class="readout readout-lg">{stats.current_streak_days}</span>
      <span class="stat-label">day{stats.current_streak_days === 1 ? '' : 's'} streak</span>
    </div>
    <div class="stat">
      <span class="readout readout-lg">{stats.longest_streak_days}</span>
      <span class="stat-label">best streak</span>
    </div>
  </div>
  <ul class="row-list">
    {#each stats.pieces as piece (piece.piece_id)}
      <li>
        <span class="title">{piece.piece_title}</span>
        <span class="chip chip-accent">{piece.total_minutes} min</span>
        <span class="chip">{piece.session_count} session{piece.session_count === 1 ? '' : 's'}</span>
        <span class="when">last: {formatDate(piece.last_practiced_at)}</span>
        {#if piece.sections.length > 0}
          <details>
            <summary>By section</summary>
            <ul class="sections">
              {#each piece.sections as section (section.section)}
                <li>{section.section} <span class="chip chip-quiet">{section.total_minutes} min</span></li>
              {/each}
            </ul>
          </details>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

{#if stats.recently_practiced.length > 0}
  <h3>Recently practiced</h3>
  <ul class="row-list">
    {#each stats.recently_practiced as piece (piece.piece_id)}
      <li>
        {piece.piece_title}
        <span class="when">{formatDate(piece.last_practiced_at)}</span>
      </li>
    {/each}
  </ul>
{/if}

{#if stats.neglected.length > 0}
  <h3>Neglected</h3>
  <ul class="row-list">
    {#each stats.neglected as piece (piece.piece_id)}
      <li>
        {piece.piece_title}
        <span class="when">
          {piece.last_practiced_at ? `last: ${formatDate(piece.last_practiced_at)}` : 'never practiced'}
        </span>
      </li>
    {/each}
  </ul>
{/if}

<style>
  h3 {
    margin-top: var(--space-5);
    margin-bottom: var(--space-2);
  }
  .goal-progress {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    flex-wrap: wrap;
  }
  .bar {
    --pct: 0%;
    flex: 1 1 8rem;
    min-width: 6rem;
    height: 6px;
    border-radius: 999px;
    background: var(--border);
    overflow: hidden;
  }
  .bar-fill {
    display: block;
    height: 100%;
    width: var(--pct);
    background: var(--accent);
    border-radius: 999px;
  }
  .totals {
    display: flex;
    gap: var(--space-5);
    flex-wrap: wrap;
    margin-bottom: var(--space-4);
    padding-bottom: var(--space-3);
    border-bottom: 1px solid var(--border);
  }
  .stat {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  .stat-label {
    font-size: var(--text-xs);
    color: var(--ink-soft);
    font-variant-caps: all-small-caps;
    letter-spacing: 0.03em;
  }
  .title {
    font-weight: 600;
  }
  .when {
    margin-left: var(--space-2);
    color: var(--ink-faint);
    font-size: var(--text-xs);
  }
  details {
    margin-top: var(--space-2);
  }
  summary {
    cursor: pointer;
    font-size: var(--text-sm);
    color: var(--ink-soft);
  }
  .sections {
    list-style: none;
    padding-left: var(--space-4);
    margin: var(--space-1) 0 0;
  }
  .sections li {
    padding: var(--space-1) 0;
    border-bottom: none;
  }
</style>
