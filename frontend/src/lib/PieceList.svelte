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
  <p>No pieces yet.</p>
{:else}
  <ul>
    {#each pieces as piece (piece.id)}
      <li>
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
        {piece.title}{piece.composer ? ` — ${piece.composer}` : ''}
        <span class="status">{piece.status}</span>
        {#if piece.difficulty}
          <span class="status">{piece.difficulty}</span>
        {/if}
        {#if piece.tags.length > 0}
          <span class="tags">{piece.tags.join(', ')}</span>
        {/if}
        {#if piece.key}
          <span class="tags">Key: {piece.key}</span>
        {/if}
        {#if piece.tempo_bpm != null}
          <span class="tags">{piece.tempo_bpm} BPM</span>
        {/if}
        {#if piece.instrument}
          <span class="tags">{piece.instrument}</span>
        {/if}
        <span class="row-actions">
          <button type="button" onclick={() => onEdit(piece)} disabled={deletingId === piece.id}>
            Edit
          </button>
          <button
            type="button"
            class="delete"
            onclick={() => handleDelete(piece)}
            disabled={deletingId === piece.id}
          >
            {deletingId === piece.id ? 'Deleting…' : 'Delete'}
          </button>
        </span>
      </li>
    {/each}
  </ul>
{/if}

<style>
  .error {
    color: #b00020;
  }
  .status {
    margin-left: 0.5rem;
    padding: 0.1rem 0.5rem;
    border-radius: 0.75rem;
    background: #e0e0e0;
    font-size: 0.8rem;
  }
  .tags {
    margin-left: 0.5rem;
    color: #666;
    font-size: 0.8rem;
  }
  .row-actions {
    margin-left: 0.5rem;
  }
  .row-actions button {
    margin-left: 0.25rem;
    font-size: 0.8rem;
  }
  .delete {
    color: #b00020;
  }
  .favorite {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    font-size: 1rem;
    color: #999;
    vertical-align: middle;
  }
  .favorite.favorited {
    color: #d4a017;
  }
</style>
