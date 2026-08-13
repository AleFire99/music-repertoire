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
  <ul class="row-list">
    {#each sessions as session (session.id)}
      <li>
        <div class="line">
          <span class="title">{pieceTitle(session.piece_id)}</span>
          <span class="tag small-caps">
            <span class="readout">{session.duration_minutes}</span> min{#if session.section}
              <span class="dot-sep"> &middot; </span>{session.section}{/if}
          </span>
          {#if session.rating}
            <span class="rating">{'★'.repeat(session.rating)}</span>
          {/if}
        </div>
        <div class="meta-line"><span>{formatDate(session.practiced_at)}</span></div>
        {#if session.notes}
          <p class="notes">{session.notes}</p>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .line {
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    gap: var(--space-2);
  }
  .title {
    font-family: var(--font-serif);
    font-size: var(--text-md);
  }
  .tag {
    color: var(--ink-faint);
    font-size: var(--text-sm);
  }
  .dot-sep {
    color: var(--ink-faint);
  }
  .rating {
    color: var(--accent);
    font-size: var(--text-sm);
  }
  .notes {
    margin: var(--space-2) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-sm);
    font-style: italic;
  }
</style>
