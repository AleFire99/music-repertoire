<script lang="ts">
  import type { Piece, SuggestedPlanItem } from './api'
  import Icon from './Icon.svelte'

  const FOCUS_CAP = 3

  let {
    pieces,
    suggestedPlan = [],
    onStartSession,
    onAddPiece,
  }: {
    pieces: Piece[]
    suggestedPlan?: SuggestedPlanItem[]
    onStartSession?: () => void
    onAddPiece?: () => void
  } = $props()

  function dueLabel(targetDate: string): string {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const target = new Date(targetDate)
    const days = Math.round((target.getTime() - today.getTime()) / 86_400_000)
    if (days < 0) return `${-days} day${-days === 1 ? '' : 's'} overdue`
    if (days === 0) return 'Due today'
    return `Due in ${days} day${days === 1 ? '' : 's'}`
  }
</script>

<div class="focus-layout">
  {#if suggestedPlan.length > 0}
    <div class="card accented elev-sm suggested-plan">
      <div class="card-kicker">
        <Icon name="goal" size={13} /> Suggested next
      </div>
      <ul class="plan-items">
        {#each suggestedPlan as item (item.piece_id)}
          <li>
            <span class="plan-title">{item.piece_title}</span>
            <span class="plan-reason">{item.reason}</span>
          </li>
        {/each}
      </ul>
      {#if onStartSession}
        <button type="button" class="primary" onclick={onStartSession}>
          <Icon name="play" size={14} /> Start a session
        </button>
      {/if}
    </div>
  {/if}

  {#if pieces.length === 0}
    <p class="empty">No pieces in focus yet. Set a status of "learning" or "maintaining" and a goal to add one.</p>
  {:else}
    {#if pieces.length > FOCUS_CAP}
      <p class="note">
        {pieces.length} pieces in focus — more than the suggested {FOCUS_CAP}. Consider narrowing down.
      </p>
    {/if}
    <div class="focus-grid">
      {#each pieces as piece (piece.id)}
        <div class="card elev-sm">
          <div class="focus-card-head">
            <div>
              <div class="card-kicker">{piece.status}</div>
              <div class="card-title">{piece.title}</div>
              {#if piece.composer}<div class="composer">{piece.composer}</div>{/if}
            </div>
            {#if piece.is_favorite}<span class="favorite-star"><Icon name="star-filled" size={18} /></span>{/if}
          </div>
          {#if piece.goal_text}<p class="card-body">{piece.goal_text}</p>{/if}
          {#if piece.goal_target_date}
            <div class="due">
              <Icon name="clock" size={13} />
              {dueLabel(piece.goal_target_date)} &middot; {piece.goal_target_date}
            </div>
          {/if}
        </div>
      {/each}
      {#if onAddPiece}
        <button type="button" class="add-tile" onclick={onAddPiece}>
          <Icon name="add" size={20} />
          <span class="add-tile-title">Bring something into focus</span>
          <span class="add-tile-sub">Pick a tune you're learning or maintaining, then give it a goal and a date.</span>
        </button>
      {/if}
    </div>
  {/if}
</div>

<style>
  .focus-layout {
    display: flex;
    flex-direction: column;
    gap: var(--space-6);
  }
  .note {
    color: var(--ink-soft);
  }
  .suggested-plan {
    max-width: 32rem;
  }
  .plan-items {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }
  .plan-items li {
    display: flex;
    justify-content: space-between;
    gap: var(--space-3);
    font-size: var(--text-sm);
  }
  .plan-title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    color: var(--accent-900);
  }
  :root[data-theme='dark'] .plan-title {
    color: var(--accent-800);
  }
  .plan-reason {
    color: var(--accent-700);
    text-align: right;
    flex: none;
  }
  .suggested-plan button {
    align-self: flex-start;
  }

  .focus-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-5);
  }
  .focus-card-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: var(--space-3);
  }
  .focus-card-head .composer {
    color: var(--ink-soft);
    font-size: var(--text-sm);
    margin-top: 2px;
  }
  .favorite-star {
    flex: none;
    color: var(--accent);
  }
  .due {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    font-size: var(--text-xs);
    color: var(--ink-faint);
  }

  .add-tile {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    gap: var(--space-2);
    min-height: 12rem;
    padding: var(--space-4);
    background: transparent;
    border: 1px dashed var(--border);
    color: var(--ink);
    text-align: left;
  }
  .add-tile:hover:not(:disabled) {
    background: var(--surface-hover);
    border-color: var(--border);
  }
  .add-tile-title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    font-size: var(--text-base);
  }
  .add-tile-sub {
    font-size: var(--text-sm);
    color: var(--ink-soft);
  }
</style>
