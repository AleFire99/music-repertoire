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
  <ul class="row-list">
    {#each lists as list (list.id)}
      <li>
        <div class="line">
          <button type="button" class="expand" onclick={() => toggleExpand(list)}>
            <span class="disclosure" class:open={expandedId === list.id} aria-hidden="true">
              <Icon name="disclose" size={14} />
            </span>
            <span class="title">{list.name}</span>
          </button>
          <span class="tag small-caps">{list.piece_count} piece{list.piece_count === 1 ? '' : 's'}</span>
          <span class="row-actions">
            <button
              type="button"
              class="icon-btn"
              onclick={() => onEdit(list)}
              disabled={deletingId === list.id}
              aria-label="Rename"
            >
              <Icon name="edit" />
            </button>
            <button
              type="button"
              class="icon-btn danger"
              onclick={() => handleDelete(list)}
              disabled={deletingId === list.id}
              aria-label="Delete"
            >
              <Icon name="delete" />
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
                        <Icon name="close" size={16} />
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
        {/if}
      </li>
    {/each}
  </ul>
{/if}

<style>
  .line {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
  }
  .expand {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    color: var(--ink);
    text-align: left;
    display: inline-flex;
    align-items: baseline;
    gap: var(--space-1);
  }
  .expand:hover:not(:disabled) {
    background: none;
  }
  .expand:hover:not(:disabled) .title {
    text-decoration: underline;
  }
  .title {
    font-family: var(--font-serif);
    font-size: var(--text-md);
  }
  .disclosure {
    display: inline-flex;
    color: var(--ink-faint);
    transition: transform 150ms ease;
  }
  .disclosure.open {
    transform: rotate(90deg);
  }
  @media (prefers-reduced-motion: reduce) {
    .disclosure {
      transition: none;
    }
  }
  .tag {
    color: var(--ink-faint);
    font-size: var(--text-sm);
  }
  .row-actions {
    margin-left: auto;
    display: flex;
    gap: var(--space-1);
  }
  .detail {
    margin: var(--space-3) 0 var(--space-2) var(--space-5);
    padding-left: var(--space-3);
    border-left: 1px solid var(--border);
  }
  .pieces {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .pieces li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-2);
    padding: var(--space-1) 0;
  }
  .piece-title {
    font-family: var(--font-serif);
  }
  .icon-btn.always {
    opacity: 1;
  }
  .add-piece {
    display: flex;
    gap: var(--space-2);
    margin-top: var(--space-3);
  }
</style>
