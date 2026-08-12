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
  <p>No repertoire lists yet.</p>
{:else}
  <ul>
    {#each lists as list (list.id)}
      <li>
        <div class="row">
          <button type="button" class="expand" onclick={() => toggleExpand(list)}>
            {expandedId === list.id ? '▾' : '▸'} {list.name}
          </button>
          <span class="count">{list.piece_count} piece{list.piece_count === 1 ? '' : 's'}</span>
          <span class="row-actions">
            <button type="button" onclick={() => onEdit(list)} disabled={deletingId === list.id}>
              Rename
            </button>
            <button
              type="button"
              class="delete"
              onclick={() => handleDelete(list)}
              disabled={deletingId === list.id}
            >
              {deletingId === list.id ? 'Deleting…' : 'Delete'}
            </button>
          </span>
        </div>

        {#if expandedId === list.id}
          <div class="detail">
            {#if expandError}
              <p class="error">{expandError}</p>
            {/if}
            {#if expandedDetail}
              {#if expandedDetail.pieces.length === 0}
                <p>No pieces on this list yet.</p>
              {:else}
                <ul class="pieces">
                  {#each expandedDetail.pieces as piece (piece.id)}
                    <li>
                      {piece.title}{piece.composer ? ` — ${piece.composer}` : ''}
                      <button
                        type="button"
                        class="delete"
                        onclick={() => handleRemovePiece(piece.id)}
                        disabled={removingPieceId === piece.id}
                      >
                        {removingPieceId === piece.id ? 'Removing…' : 'Remove'}
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
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .error {
    color: #b00020;
  }
  .row {
    display: flex;
    align-items: center;
  }
  .expand {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    font-size: 1rem;
    text-align: left;
  }
  .count {
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
  .detail {
    margin: 0.5rem 0 1rem 1.5rem;
  }
  .pieces li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .add-piece {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
</style>
