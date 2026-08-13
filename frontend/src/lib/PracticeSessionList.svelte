<script lang="ts">
  import type { Piece, PracticeSession } from './api'

  let {
    sessions,
    pieces,
  }: {
    sessions: PracticeSession[]
    pieces: Piece[]
  } = $props()

  function pieceTitle(pieceId: number): string {
    return pieces.find((p) => p.id === pieceId)?.title ?? `Piece #${pieceId}`
  }

  function formatDate(iso: string): string {
    return new Date(iso).toLocaleString()
  }
</script>

{#if sessions.length === 0}
  <p class="empty">No practice sessions logged yet.</p>
{:else}
  <ul class="manuscript-list">
    {#each sessions as session (session.id)}
      <li>
        <span class="title">{pieceTitle(session.piece_id)}</span>
        <span class="chip chip-accent">{session.duration_minutes} min</span>
        {#if session.section}
          <span class="chip">{session.section}</span>
        {/if}
        {#if session.rating}
          <span class="rating">{'★'.repeat(session.rating)}</span>
        {/if}
        <span class="when">{formatDate(session.practiced_at)}</span>
        {#if session.notes}
          <p class="notes">{session.notes}</p>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .title {
    font-weight: 600;
  }
  .when {
    display: block;
    margin-top: var(--space-1);
    color: var(--ink-faint);
    font-size: var(--text-xs);
  }
  .rating {
    margin-left: var(--space-2);
    color: var(--brass);
  }
  .notes {
    margin: var(--space-2) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-sm);
    font-style: italic;
  }
</style>
