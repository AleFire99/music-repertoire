<script lang="ts">
  import { deleteSheetResource, type Piece, type SheetResource } from './api'
  import Icon from './Icon.svelte'

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
  <p class="empty">No sheet resources yet.</p>
{:else}
  <ul class="row-list">
    {#each resources as resource (resource.id)}
      <li>
        <div class="line">
          <span class="title">{pieceTitle(resource.piece_id)}</span>
          <span class="tag small-caps">
            {resource.kind}{#if resource.label}<span class="dot-sep"> &middot; </span>{resource.label}{/if}
          </span>
          <span class="row-actions">
            <button
              type="button"
              class="icon-btn danger"
              onclick={() => handleDelete(resource)}
              disabled={deletingId === resource.id}
              aria-label="Delete"
            >
              <Icon name="delete" />
            </button>
          </span>
        </div>
        <p class="reference">{resource.reference}</p>
        {#if resource.notes}
          <p class="notes">{resource.notes}</p>
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
  .tag {
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
  }
  .reference {
    margin: var(--space-1) 0 0;
    color: var(--ink);
    font-size: var(--text-sm);
  }
  .notes {
    margin: var(--space-1) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-xs);
    font-style: italic;
  }
</style>
