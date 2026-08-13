<script lang="ts">
  import type { PracticeStats } from './api'

  let { stats }: { stats: PracticeStats } = $props()

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString()
  }
</script>

{#if stats.pieces.length === 0}
  <p>No practice sessions logged yet.</p>
{:else}
  <p>Total practice time: <strong>{stats.total_minutes} min</strong></p>
  <p>
    This week: <strong>{stats.minutes_this_week} min</strong>
    &middot;
    This month: <strong>{stats.minutes_this_month} min</strong>
  </p>
  <p>
    Current streak: <strong>{stats.current_streak_days} day{stats.current_streak_days === 1 ? '' : 's'}</strong>
    &middot;
    Longest streak: <strong>{stats.longest_streak_days} day{stats.longest_streak_days === 1 ? '' : 's'}</strong>
  </p>
  <ul>
    {#each stats.pieces as piece (piece.piece_id)}
      <li>
        {piece.piece_title} — {piece.total_minutes} min
        <span class="count">{piece.session_count} session{piece.session_count === 1 ? '' : 's'}</span>
        <span class="when">last: {formatDate(piece.last_practiced_at)}</span>
        {#if piece.sections.length > 0}
          <details>
            <summary>By section</summary>
            <ul>
              {#each piece.sections as section (section.section)}
                <li>{section.section} — {section.total_minutes} min</li>
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
  <ul>
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
  <ul>
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
  ul {
    padding-left: 0;
    list-style: none;
  }
  li {
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
  }
  .count {
    margin-left: 0.5rem;
    padding: 0.1rem 0.5rem;
    border-radius: 0.75rem;
    background: #e0e0e0;
    font-size: 0.8rem;
  }
  .when {
    margin-left: 0.5rem;
    color: #666;
    font-size: 0.8rem;
  }
</style>
