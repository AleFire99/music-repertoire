<script lang="ts">
  import type { Piece } from './api'

  const FOCUS_CAP = 3

  let { pieces }: { pieces: Piece[] } = $props()
</script>

{#if pieces.length === 0}
  <p class="empty">No pieces in focus yet. Set a status of "learning" or "maintaining" and a goal to add one.</p>
{:else}
  {#if pieces.length > FOCUS_CAP}
    <p class="note">
      {pieces.length} pieces in focus — more than the suggested {FOCUS_CAP}. Consider narrowing down.
    </p>
  {/if}
  <ul class="row-list">
    {#each pieces as piece (piece.id)}
      <li class="accented">
        <div class="line">
          <span class="title">{piece.title}</span>
          <span class="status small-caps">{piece.status}</span>
        </div>
        {#if piece.goal_text || piece.goal_target_date}
          <div class="meta-line">
            {#if piece.goal_text}<span>{piece.goal_text}</span>{/if}
            {#if piece.goal_target_date}<span>by {piece.goal_target_date}</span>{/if}
          </div>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .line {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
  }
  .title {
    font-family: var(--font-serif);
    font-size: var(--text-md);
  }
  .status {
    color: var(--accent);
    font-size: var(--text-sm);
  }
  .note {
    color: var(--ink-soft);
  }
</style>
