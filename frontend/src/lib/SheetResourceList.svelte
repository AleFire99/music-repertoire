<script lang="ts">
  import { deleteSheetResource, type Piece, type SheetResource } from './api'

  let {
    resources,
    pieces,
    onDeleted,
  }: {
    resources: SheetResource[]
    pieces: Piece[]
    onDeleted: (id: number) => void
  } = $props()

  let deletingId = $state<number | null>(null)
  let deleteError = $state<string | null>(null)

  function pieceTitle(pieceId: number): string {
    return pieces.find((p) => p.id === pieceId)?.title ?? `Piece #${pieceId}`
  }

  async function handleDelete(resource: SheetResource): Promise<void> {
    if (!window.confirm(`Delete this sheet resource? This cannot be undone.`)) return
    deletingId = resource.id
    deleteError = null
    try {
      await deleteSheetResource(resource.id)
      onDeleted(resource.id)
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

{#if resources.length === 0}
  <p>No sheet resources yet.</p>
{:else}
  <ul>
    {#each resources as resource (resource.id)}
      <li>
        {pieceTitle(resource.piece_id)}
        <span class="kind">{resource.kind}</span>
        {#if resource.label}
          <strong>{resource.label}</strong>
        {/if}
        <span class="row-actions">
          <button
            type="button"
            class="delete"
            onclick={() => handleDelete(resource)}
            disabled={deletingId === resource.id}
          >
            {deletingId === resource.id ? 'Deleting…' : 'Delete'}
          </button>
        </span>
        <p class="reference">{resource.reference}</p>
        {#if resource.notes}
          <p class="notes">{resource.notes}</p>
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .error {
    color: #b00020;
  }
  ul {
    padding-left: 0;
    list-style: none;
  }
  li {
    margin-bottom: 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
  }
  .kind {
    margin-left: 0.5rem;
    padding: 0.1rem 0.5rem;
    border-radius: 0.75rem;
    background: #e0e0e0;
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
  .reference {
    margin: 0.25rem 0 0;
    color: #444;
    font-size: 0.9rem;
  }
  .notes {
    margin: 0.25rem 0 0;
    color: #666;
    font-size: 0.8rem;
  }
</style>
