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
        <span class="title">{piece.title}</span>
        <span class="chip chip-accent">{piece.status}</span>
        {#if piece.goal_text}
          <span class="goal">{piece.goal_text}</span>
        {/if}
        {#if piece.goal_target_date}
          <span class="goal-date">by {piece.goal_target_date}</span>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .title {
    font-weight: 600;
  }
  .goal,
  .goal-date {
    margin-left: var(--space-2);
    color: var(--ink-soft);
    font-size: var(--text-sm);
    font-style: italic;
  }
  .note {
    color: var(--ink-soft);
  }
</style>
