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
  <ul>
    {#each stats.pieces as piece (piece.piece_id)}
      <li>
        {piece.piece_title} — {piece.total_minutes} min
        <span class="count">{piece.session_count} session{piece.session_count === 1 ? '' : 's'}</span>
        <span class="when">last: {formatDate(piece.last_practiced_at)}</span>
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
