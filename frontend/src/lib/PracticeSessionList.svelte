<script lang="ts">
  import type { Piece, PracticeSession } from './api'
  import Icon from './Icon.svelte'

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
          <span class="tag tag-neutral">
            <span class="readout">{session.duration_minutes}</span> min{#if session.section}
              &middot; {session.section}{/if}
          </span>
          {#if session.rating}
            {@const rating = session.rating}
            <span class="rating">
              {#each [0, 1, 2, 3, 4] as n (n)}
                <Icon name={n < rating ? 'star-filled' : 'star'} size={13} />
              {/each}
            </span>
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
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-2);
  }
  .title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    font-size: var(--text-base);
  }
  .rating {
    display: inline-flex;
    gap: 2px;
    color: var(--accent);
  }
  .notes {
    margin: var(--space-2) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-sm);
  }
</style>
