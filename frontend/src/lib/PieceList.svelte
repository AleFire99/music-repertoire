<script lang="ts">
  import {
    deletePiece,
    listSheetResources,
    updatePiece,
    type Piece,
    type PiecePracticeStats,
    type SheetResource,
  } from './api'
  import Icon from './Icon.svelte'
  import SheetResourceForm from './SheetResourceForm.svelte'
  import SheetResourceList from './SheetResourceList.svelte'

  const KNOWN_GENRES = ['Jazz', 'Classical', 'Anime', 'Film', 'Contemporary', 'Mine']
  const DIFFICULTY_RANK: Record<string, number> = {
    beginner: 1,
    intermediate: 2,
    advanced: 3,
    expert: 4,
  }

  let {
    pieces,
    stats = [],
    onEdit,
    onDeleted,
    onUpdated,
    onPreview,
  }: {
    pieces: Piece[]
    stats?: PiecePracticeStats[]
    onEdit: (piece: Piece) => void
    onDeleted: (id: number) => void
    onUpdated: (piece: Piece) => void
    onPreview: (resource: SheetResource) => void
  } = $props()

  let deletingId = $state<number | null>(null)
  let deleteError = $state<string | null>(null)
  let togglingFavoriteId = $state<number | null>(null)
  let favoriteError = $state<string | null>(null)

  let expandedId = $state<number | null>(null)
  let expandedResources = $state<SheetResource[]>([])
  let expandError = $state<string | null>(null)
  let addResourceOpen = $state(false)

  const statsByPiece = $derived(new Map(stats.map((s) => [s.piece_id, s])))

  function genre(piece: Piece): string | null {
    if (piece.tags.length === 0) return null
    const known = piece.tags.find((t) => KNOWN_GENRES.some((g) => g.toLowerCase() === t.toLowerCase()))
    return known ?? piece.tags[0]
  }

  function formatMinutes(minutes: number): string {
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return h > 0 ? `${h}h ${String(m).padStart(2, '0')}m` : `${m}m`
  }

  function formatLastPracticed(iso: string): string {
    const date = new Date(iso)
    const now = new Date()
    const sameDay = (a: Date, b: Date) =>
      a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
    if (sameDay(date, now)) return 'Today'
    const yesterday = new Date(now)
    yesterday.setDate(now.getDate() - 1)
    if (sameDay(date, yesterday)) return 'Yesterday'
    return date.toLocaleDateString()
  }

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

  async function toggleExpand(piece: Piece): Promise<void> {
    if (expandedId === piece.id) {
      expandedId = null
      return
    }
    expandError = null
    addResourceOpen = false
    try {
      expandedResources = await listSheetResources({ piece_id: piece.id })
      expandedId = piece.id
    } catch (err) {
      expandError = err instanceof Error ? err.message : String(err)
    }
  }

  function handleResourceSaved(resource: SheetResource): void {
    expandedResources = [resource, ...expandedResources]
    addResourceOpen = false
  }

  function handleResourceDeleted(id: number): void {
    expandedResources = expandedResources.filter((r) => r.id !== id)
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
  <div class="table-scroll">
    <table class="table">
      <thead>
        <tr>
          <th style="width:2rem"></th>
          <th>Piece</th>
          <th style="width:8rem">Status</th>
          <th style="width:6rem">Difficulty</th>
          <th style="width:6rem">Key</th>
          <th style="width:4.5rem">Tempo</th>
          <th style="width:7rem">Last practiced</th>
          <th class="num" style="width:5rem">Total</th>
          <th style="width:4.5rem"></th>
        </tr>
      </thead>
      <tbody>
        {#each pieces as piece (piece.id)}
          {@const pieceGenre = genre(piece)}
          {@const pieceStats = statsByPiece.get(piece.id)}
          <tr class="row-hover">
            <td>
              <button
                type="button"
                class="icon-btn favorite always"
                class:favorited={piece.is_favorite}
                onclick={() => toggleFavorite(piece)}
                disabled={togglingFavoriteId === piece.id}
                aria-label={piece.is_favorite ? 'Unmark as favorite' : 'Mark as favorite'}
              >
                <Icon name={piece.is_favorite ? 'star-filled' : 'star'} size={16} />
              </button>
            </td>
            <td>
              <div class="title-row">
                <button
                  type="button"
                  class="icon-btn disclose always"
                  class:expanded={expandedId === piece.id}
                  onclick={() => toggleExpand(piece)}
                  aria-label={expandedId === piece.id ? 'Hide sheet resources' : 'Show sheet resources'}
                >
                  <Icon name="disclose" size={14} />
                </button>
                <span class="title">{piece.title}</span>
                {#if pieceGenre}<span class="tag tag-neutral">{pieceGenre}</span>{/if}
              </div>
              {#if piece.composer}<div class="composer">{piece.composer}</div>{/if}
              {#if piece.goal_text || piece.goal_target_date}
                <div class="goal-chip">
                  <Icon name="goal" size={12} />
                  {piece.goal_text ?? ''}{piece.goal_text && piece.goal_target_date ? ' — ' : ''}{piece.goal_target_date ?? ''}
                </div>
              {/if}
            </td>
            <td><span class="tag tag-accent">{piece.status}</span></td>
            <td>
              {#if piece.difficulty}
                <span class="diff-dots">
                  {#each [0, 1, 2, 3] as n (n)}
                    <i class:filled={n < DIFFICULTY_RANK[piece.difficulty]}></i>
                  {/each}
                </span>
                {piece.difficulty}
              {/if}
            </td>
            <td>{piece.key ?? ''}</td>
            <td class="readout">{piece.tempo_bpm ?? ''}</td>
            <td>{pieceStats ? formatLastPracticed(pieceStats.last_practiced_at) : 'Never'}</td>
            <td class="num readout">{pieceStats ? formatMinutes(pieceStats.total_minutes) : ''}</td>
            <td class="row-actions">
              <button type="button" class="icon-btn" onclick={() => onEdit(piece)} disabled={deletingId === piece.id} aria-label="Edit">
                <Icon name="edit" size={16} />
              </button>
              <button type="button" class="icon-btn danger" onclick={() => handleDelete(piece)} disabled={deletingId === piece.id} aria-label="Delete">
                <Icon name="delete" size={16} />
              </button>
            </td>
          </tr>
          {#if expandedId === piece.id}
            <tr class="disclosure-row">
              <td colspan="9">
                <div class="disclosure">
                  {#if expandError}
                    <p class="error">{expandError}</p>
                  {/if}
                  <SheetResourceList
                    resources={expandedResources}
                    onDeleted={handleResourceDeleted}
                    {onPreview}
                  />
                  {#if addResourceOpen}
                    <SheetResourceForm
                      {pieces}
                      fixedPieceId={piece.id}
                      onSaved={handleResourceSaved}
                      onCancel={() => (addResourceOpen = false)}
                    />
                  {:else}
                    <button type="button" class="secondary add-resource" onclick={() => (addResourceOpen = true)}>
                      <Icon name="add" size={14} /> Add a resource
                    </button>
                  {/if}
                </div>
              </td>
            </tr>
          {/if}
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .table-scroll {
    overflow-x: auto;
    overflow-y: hidden;
    background: var(--surface-container);
    border-radius: var(--radius-md);
    box-shadow: var(--elevation-1);
  }
  .table {
    min-width: 52rem;
  }
  .title-row {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
    flex-wrap: wrap;
  }
  .title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    font-size: var(--text-base);
  }
  .disclose {
    color: var(--ink-faint);
    transition: transform 120ms ease, color 120ms ease;
  }
  .disclose:hover:not(:disabled) {
    color: var(--ink);
  }
  .disclose.expanded {
    transform: rotate(90deg);
  }
  .disclosure-row td {
    padding-top: 0;
  }
  .disclosure {
    padding: var(--space-4);
    margin-bottom: var(--space-3);
    background: var(--surface-container-high);
    border-radius: var(--radius-sm);
    box-shadow: var(--elevation-1);
  }
  .add-resource {
    margin-top: var(--space-3);
  }
  .composer {
    color: var(--ink-soft);
    font-size: var(--text-sm);
    margin-top: 2px;
  }
  .goal-chip {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    margin-top: var(--space-2);
    font-size: var(--text-xs);
    color: var(--accent-700);
    background: var(--accent-100);
    padding: 3px 10px;
    border-radius: var(--radius-full);
  }
  .favorite {
    color: var(--ink-faint);
  }
  .favorite:hover:not(:disabled) {
    color: var(--accent);
  }
  .favorite.favorited {
    color: var(--accent);
  }
  .row-actions {
    display: flex;
    gap: var(--space-1);
    justify-content: flex-end;
  }
</style>
