<script lang="ts">
  import { deletePiece, type Piece } from './api'

  let {
    pieces,
    onEdit,
    onDeleted,
  }: {
    pieces: Piece[]
    onEdit: (piece: Piece) => void
    onDeleted: (id: number) => void
  } = $props()

  let deletingId = $state<number | null>(null)
  let deleteError = $state<string | null>(null)

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
</script>

{#if deleteError}
  <p class="error">{deleteError}</p>
{/if}

{#if pieces.length === 0}
  <p>No pieces yet.</p>
{:else}
  <ul>
    {#each pieces as piece (piece.id)}
      <li>
        {piece.title}{piece.composer ? ` — ${piece.composer}` : ''}
        <span class="status">{piece.status}</span>
        {#if piece.tags.length > 0}
          <span class="tags">{piece.tags.join(', ')}</span>
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
</style>
