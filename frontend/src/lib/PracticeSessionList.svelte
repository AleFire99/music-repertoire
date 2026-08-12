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
  <p>No practice sessions logged yet.</p>
{:else}
  <ul>
    {#each sessions as session (session.id)}
      <li>
        {pieceTitle(session.piece_id)} — {session.duration_minutes} min
        <span class="when">{formatDate(session.practiced_at)}</span>
        {#if session.section}
          <span class="section">{session.section}</span>
        {/if}
        {#if session.rating}
          <span class="rating">{'★'.repeat(session.rating)}</span>
        {/if}
        {#if session.notes}
          <p class="notes">{session.notes}</p>
        {/if}
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
  .when {
    margin-left: 0.5rem;
    color: #666;
    font-size: 0.8rem;
  }
  .section {
    margin-left: 0.5rem;
    padding: 0.1rem 0.5rem;
    border-radius: 0.75rem;
    background: #e0e0e0;
    font-size: 0.8rem;
  }
  .rating {
    margin-left: 0.5rem;
    color: #c9a227;
  }
  .notes {
    margin: 0.25rem 0 0;
    color: #444;
    font-size: 0.9rem;
  }
</style>
