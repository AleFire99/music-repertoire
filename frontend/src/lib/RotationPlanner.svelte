<script lang="ts">
  import type { Piece } from './api'

  const FOCUS_CAP = 3

  let { pieces }: { pieces: Piece[] } = $props()
</script>

{#if pieces.length === 0}
  <p>No pieces in focus yet. Set a status of "learning" or "maintaining" and a goal to add one.</p>
{:else}
  {#if pieces.length > FOCUS_CAP}
    <p class="note">
      {pieces.length} pieces in focus — more than the suggested {FOCUS_CAP}. Consider narrowing down.
    </p>
  {/if}
  <ul>
    {#each pieces as piece (piece.id)}
      <li>
        {piece.title} <span class="status">{piece.status}</span>
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
  ul {
    padding-left: 0;
    list-style: none;
  }
  li {
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
  }
  .status {
    margin-left: 0.5rem;
    padding: 0.1rem 0.5rem;
    border-radius: 0.75rem;
    background: #e0e0e0;
    font-size: 0.8rem;
  }
  .goal,
  .goal-date {
    margin-left: 0.5rem;
    color: #666;
    font-size: 0.8rem;
  }
  .note {
    color: #666;
  }
</style>
