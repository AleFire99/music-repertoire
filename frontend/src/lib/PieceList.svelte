<script lang="ts">
  import { deletePiece, updatePiece, type Piece } from './api'

  let {
    pieces,
    onEdit,
    onDeleted,
    onUpdated,
  }: {
    pieces: Piece[]
    onEdit: (piece: Piece) => void
    onDeleted: (id: number) => void
    onUpdated: (piece: Piece) => void
  } = $props()

  let deletingId = $state<number | null>(null)
  let deleteError = $state<string | null>(null)
  let togglingFavoriteId = $state<number | null>(null)
  let favoriteError = $state<string | null>(null)

  async function handleDelete(piece: Piece): Promise<void> {
    if (!window.confirm(`Delete "${piece.title}"? This cannot be undone.`)) return
    deletingId = piece.id
    deleteError = null
    try {
      await deletePiece(piece.id)
      onDeleted(piece.id)
    } catch (err) {
      deleteError = err instanceof Error ? err.message : String(err)
    } finally {
      deletingId = null
    }
  }

  async function toggleFavorite(piece: Piece): Promise<void> {
    togglingFavoriteId = piece.id
    favoriteError = null
    try {
      const updated = await updatePiece(piece.id, { is_favorite: !piece.is_favorite })
      onUpdated(updated)
    } catch (err) {
      favoriteError = err instanceof Error ? err.message : String(err)
    } finally {
      togglingFavoriteId = null
    }
  }
</script>

{#if deleteError}
  <p class="error">{deleteError}</p>
{/if}
{#if favoriteError}
  <p class="error">{favoriteError}</p>
{/if}

{#if pieces.length === 0}
  <p class="empty">No pieces yet.</p>
{:else}
  <ul class="manuscript-list">
    {#each pieces as piece (piece.id)}
      <li class:accented={piece.is_favorite}>
        <div class="line">
          <button
            type="button"
            class="favorite"
            class:favorited={piece.is_favorite}
            onclick={() => toggleFavorite(piece)}
            disabled={togglingFavoriteId === piece.id}
            aria-label={piece.is_favorite ? 'Unmark as favorite' : 'Mark as favorite'}
          >
            {piece.is_favorite ? '★' : '☆'}
          </button>
          <span class="title">{piece.title}{piece.composer ? ` — ${piece.composer}` : ''}</span>
          <span class="chip chip-accent">{piece.status}</span>
          {#if piece.difficulty}
            <span class="chip">{piece.difficulty}</span>
          {/if}
          <span class="row-actions">
            <button type="button" class="secondary" onclick={() => onEdit(piece)} disabled={deletingId === piece.id}>
              Edit
            </button>
            <button
              type="button"
              class="danger"
              onclick={() => handleDelete(piece)}
              disabled={deletingId === piece.id}
            >
              {deletingId === piece.id ? 'Deleting…' : 'Delete'}
            </button>
          </span>
        </div>
        <div class="meta">
          {#if piece.key}
            <span class="chip chip-quiet">{piece.key}</span>
          {/if}
          {#if piece.tempo_bpm != null}
            <span class="chip chip-quiet tempo">&#9833; = {piece.tempo_bpm}</span>
          {/if}
          {#if piece.instrument}
            <span class="chip chip-quiet">{piece.instrument}</span>
          {/if}
          {#each piece.tags as tag (tag)}
            <span class="chip chip-quiet">{tag}</span>
          {/each}
        </div>
        {#if piece.goal_text || piece.goal_target_date}
          <p class="goal">
            Goal: {piece.goal_text ?? ''}{piece.goal_text && piece.goal_target_date
              ? ' — '
              : ''}{piece.goal_target_date ?? ''}
          </p>
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
    gap: var(--space-1);
  }
  .title {
    font-weight: 600;
  }
  .meta {
    margin-top: var(--space-1);
  }
  .meta .chip {
    margin-left: 0;
    margin-right: var(--space-2);
  }
  .tempo {
    font-family: var(--font-mono);
    font-variant-numeric: tabular-nums;
  }
  .row-actions {
    margin-left: auto;
    display: flex;
    gap: var(--space-1);
  }
  .goal {
    margin: var(--space-1) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-sm);
    font-style: italic;
  }
  .favorite {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    font-size: 1.05rem;
    color: var(--ink-faint);
    vertical-align: middle;
  }
  .favorite:hover:not(:disabled) {
    background: none;
    color: var(--brass);
  }
  .favorite.favorited {
    color: var(--brass);
  }
</style>
