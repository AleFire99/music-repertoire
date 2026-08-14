<script lang="ts">
  import {
    addPieceToRepertoireList,
    deleteRepertoireList,
    getRepertoireList,
    removePieceFromRepertoireList,
    type Piece,
    type RepertoireList,
    type RepertoireListDetail,
  } from './api'
  import Icon from './Icon.svelte'

  let {
    lists,
    pieces,
    onEdit,
    onDeleted,
    onCountChanged,
  }: {
    lists: RepertoireList[]
    pieces: Piece[]
    onEdit: (list: RepertoireList) => void
    onDeleted: (id: number) => void
    onCountChanged: (id: number, pieceCount: number) => void
  } = $props()

  let deletingId = $state<number | null>(null)
  let deleteError = $state<string | null>(null)

  let expandedId = $state<number | null>(null)
  let expandedDetail = $state<RepertoireListDetail | null>(null)
  let expandError = $state<string | null>(null)

  let addPieceId = $state<number | ''>('')
  let addError = $state<string | null>(null)
  let addingPiece = $state(false)
  let removingPieceId = $state<number | null>(null)
  let removeError = $state<string | null>(null)

  const availablePieces = $derived(
    pieces.filter((p) => !expandedDetail?.pieces.some((ep) => ep.id === p.id)),
  )

  async function handleDelete(list: RepertoireList): Promise<void> {
    if (!window.confirm(`Delete list "${list.name}"? Pieces on it are kept.`)) return
    deletingId = list.id
    deleteError = null
    try {
      await deleteRepertoireList(list.id)
      onDeleted(list.id)
      if (expandedId === list.id) {
        expandedId = null
        expandedDetail = null
      }
    } catch (err) {
      deleteError = err instanceof Error ? err.message : String(err)
    } finally {
      deletingId = null
    }
  }

  async function toggleExpand(list: RepertoireList): Promise<void> {
    if (expandedId === list.id) {
      expandedId = null
      expandedDetail = null
      return
    }
    expandError = null
    addError = null
    removeError = null
    addPieceId = ''
    try {
      expandedDetail = await getRepertoireList(list.id)
      expandedId = list.id
    } catch (err) {
      expandError = err instanceof Error ? err.message : String(err)
    }
  }

  async function handleAddPiece(): Promise<void> {
    if (expandedId === null || addPieceId === '') return
    addingPiece = true
    addError = null
    try {
      expandedDetail = await addPieceToRepertoireList(expandedId, Number(addPieceId))
      onCountChanged(expandedId, expandedDetail.pieces.length)
      addPieceId = ''
    } catch (err) {
      addError = err instanceof Error ? err.message : String(err)
    } finally {
      addingPiece = false
    }
  }

  async function handleRemovePiece(pieceId: number): Promise<void> {
    if (expandedId === null) return
    removingPieceId = pieceId
    removeError = null
    try {
      await removePieceFromRepertoireList(expandedId, pieceId)
      expandedDetail = {
        ...expandedDetail!,
        pieces: expandedDetail!.pieces.filter((p) => p.id !== pieceId),
      }
      onCountChanged(expandedId, expandedDetail.pieces.length)
    } catch (err) {
      removeError = err instanceof Error ? err.message : String(err)
    } finally {
      removingPieceId = null
    }
  }
</script>

{#if deleteError}
  <p class="error">{deleteError}</p>
{/if}

{#if lists.length === 0}
  <p class="empty">No repertoire lists yet.</p>
{:else}
  <div class="list-grid">
    {#each lists as list (list.id)}
      <div class="card elev-sm">
        <div class="card-head">
          <button type="button" class="expand" onclick={() => toggleExpand(list)}>
            <span class="card-title">{list.name}</span>
          </button>
          <span class="tag tag-accent">{list.piece_count} piece{list.piece_count === 1 ? '' : 's'}</span>
        </div>

        {#if expandedId === list.id}
          <div class="detail">
            {#if expandError}
              <p class="error">{expandError}</p>
            {/if}
            {#if expandedDetail}
              {#if expandedDetail.pieces.length === 0}
                <p class="empty">No pieces on this list yet.</p>
              {:else}
                <ul class="pieces">
                  {#each expandedDetail.pieces as piece (piece.id)}
                    <li>
                      <span class="piece-title">{piece.title}{piece.composer ? ` — ${piece.composer}` : ''}</span>
                      <button
                        type="button"
                        class="icon-btn danger always"
                        onclick={() => handleRemovePiece(piece.id)}
                        disabled={removingPieceId === piece.id}
                        aria-label="Remove"
                      >
                        <Icon name="close" size={15} />
                      </button>
                    </li>
                  {/each}
                </ul>
              {/if}
              {#if removeError}
                <p class="error">{removeError}</p>
              {/if}

              {#if availablePieces.length > 0}
                <div class="add-piece">
                  <select bind:value={addPieceId}>
                    <option value="">Add a piece…</option>
                    {#each availablePieces as piece (piece.id)}
                      <option value={piece.id}>{piece.title}</option>
                    {/each}
                  </select>
                  <button
                    type="button"
                    class="secondary"
                    onclick={handleAddPiece}
                    disabled={addingPiece || addPieceId === ''}
                  >
                    Add
                  </button>
                </div>
              {/if}
              {#if addError}
                <p class="error">{addError}</p>
              {/if}
            {/if}
          </div>
        {:else if list.piece_count > 0}
          <p class="card-body">Click the name to view and manage pieces.</p>
        {/if}

        <div class="row-actions">
          <button type="button" class="icon-btn always" onclick={() => onEdit(list)} disabled={deletingId === list.id} aria-label="Rename">
            <Icon name="edit" size={15} />
          </button>
          <button type="button" class="icon-btn danger always" onclick={() => handleDelete(list)} disabled={deletingId === list.id} aria-label="Delete">
            <Icon name="delete" size={15} />
          </button>
        </div>
      </div>
    {/each}
  </div>
{/if}

<style>
  .list-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-5);
    align-items: start;
  }
  .card-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: var(--space-2);
  }
  .expand {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    color: inherit;
    text-align: left;
  }
  .expand:hover:not(:disabled) {
    background: none;
  }
  .expand:hover:not(:disabled) .card-title {
    text-decoration: underline;
  }
  .detail {
    padding-top: var(--space-2);
    border-top: var(--border-width) solid var(--border);
  }
  .pieces {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
  .pieces li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    font-size: var(--text-sm);
  }
  .piece-title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
  }
  .add-piece {
    display: flex;
    gap: var(--space-2);
    margin-top: var(--space-3);
  }
  .row-actions {
    display: flex;
    gap: var(--space-1);
    justify-content: flex-end;
    margin-top: auto;
  }
</style>
