<script lang="ts">
  import { deletePiece, updatePiece, type Piece } from './api'
  import Icon from './Icon.svelte'

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
  <ul class="row-list">
    {#each pieces as piece (piece.id)}
      <li class:accented={piece.is_favorite}>
        <div class="line">
          <button
            type="button"
            class="icon-btn favorite"
            class:favorited={piece.is_favorite}
            onclick={() => toggleFavorite(piece)}
            disabled={togglingFavoriteId === piece.id}
            aria-label={piece.is_favorite ? 'Unmark as favorite' : 'Mark as favorite'}
          >
            <Icon name={piece.is_favorite ? 'bookmark-filled' : 'bookmark'} />
          </button>
          <span class="title">{piece.title}</span>
          {#if piece.composer}<span class="composer">{piece.composer}</span>{/if}
          <span class="status small-caps">
            {piece.status}{#if piece.difficulty}<span class="dot-sep"> &middot; </span>{piece.difficulty}{/if}
          </span>
          <span class="row-actions">
            <button
              type="button"
              class="icon-btn"
              onclick={() => onEdit(piece)}
              disabled={deletingId === piece.id}
              aria-label="Edit"
            >
              <Icon name="edit" />
            </button>
            <button
              type="button"
              class="icon-btn danger"
              onclick={() => handleDelete(piece)}
              disabled={deletingId === piece.id}
              aria-label="Delete"
            >
              <Icon name="delete" />
            </button>
          </span>
        </div>
        {#if piece.key || piece.tempo_bpm != null || piece.instrument || piece.tags.length > 0}
          <div class="meta-line">
            {#if piece.key}<span>{piece.key}</span>{/if}
            {#if piece.tempo_bpm != null}<span><span class="readout">{piece.tempo_bpm}</span> bpm</span>{/if}
            {#if piece.instrument}<span>{piece.instrument}</span>{/if}
            {#each piece.tags as tag (tag)}<span>{tag}</span>{/each}
          </div>
        {/if}
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
    align-items: baseline;
    flex-wrap: wrap;
    gap: var(--space-2);
  }
  .title {
    font-family: var(--font-serif);
    font-size: var(--text-md);
  }
  .composer {
    font-style: italic;
    color: var(--ink-soft);
    font-size: var(--text-sm);
  }
  .status {
    color: var(--ink-faint);
    font-size: var(--text-sm);
  }
  .dot-sep {
    color: var(--ink-faint);
  }
  .row-actions {
    margin-left: auto;
    display: flex;
    gap: var(--space-1);
    align-self: center;
  }
  .goal {
    margin: var(--space-1) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-sm);
    font-style: italic;
  }
  .favorite {
    opacity: 1;
    color: var(--ink-faint);
  }
  .favorite:hover:not(:disabled) {
    color: var(--accent);
  }
  .favorite.favorited {
    color: var(--accent);
  }
</style>
