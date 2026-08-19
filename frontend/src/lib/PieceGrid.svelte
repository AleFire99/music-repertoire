<script lang="ts">
  import {
    listSheetResources,
    sheetResourceThumbnailUrl,
    type Piece,
    type SheetResource,
    type SheetResourceKind,
  } from './api'
  import Icon from './Icon.svelte'
  import SheetResourceForm from './SheetResourceForm.svelte'
  import SheetResourceList from './SheetResourceList.svelte'

  const DIFFICULTY_RANK: Record<string, number> = {
    beginner: 1,
    intermediate: 2,
    advanced: 3,
    expert: 4,
  }

  const KIND_ICON: Record<SheetResourceKind, string> = {
    url: 'link',
    physical: 'book',
    'local-doc': 'sheet',
    uploaded: 'download',
  }

  const KIND_LABEL: Record<SheetResourceKind, string> = {
    url: 'Has a linked URL',
    physical: 'Has a physical copy',
    'local-doc': 'Has a local file',
    uploaded: 'Has an uploaded file',
  }

  let {
    pieces,
    onPreview,
  }: {
    pieces: Piece[]
    onPreview: (resource: SheetResource) => void
  } = $props()

  let expandedId = $state<number | null>(null)
  let expandedResources = $state<SheetResource[]>([])
  let expandError = $state<string | null>(null)
  let addResourceOpen = $state(false)

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

{#if pieces.length === 0}
  <p class="empty">No pieces yet.</p>
{:else}
  <div class="grid">
    {#each pieces as piece (piece.id)}
      <div class="tile card">
        {#if piece.preview_sheet_resource_id}
          <img
            class="tile-thumb"
            src={sheetResourceThumbnailUrl(piece.preview_sheet_resource_id)}
            alt=""
          />
        {/if}
        <button
          type="button"
          class="tile-trigger"
          onclick={() => toggleExpand(piece)}
          aria-expanded={expandedId === piece.id}
        >
          <span class="tag tag-accent">{piece.status}</span>
          <span class="tile-title">{piece.title}</span>
          {#if piece.composer}<span class="tile-composer">{piece.composer}</span>{/if}
          {#if piece.difficulty}
            <span class="diff-dots">
              {#each [0, 1, 2, 3] as n (n)}
                <i class:filled={n < DIFFICULTY_RANK[piece.difficulty]}></i>
              {/each}
            </span>
          {/if}
          {#if piece.goal_text || piece.goal_target_date}
            <span class="goal-chip">
              <Icon name="goal" size={12} />
              {piece.goal_text ?? ''}{piece.goal_text && piece.goal_target_date ? ' — ' : ''}{piece.goal_target_date ?? ''}
            </span>
          {/if}
        </button>

        {#if piece.sheet_resource_kinds.length > 0 || piece.wiki_reference}
          <div class="badge-row">
            {#each piece.sheet_resource_kinds.slice(0, 3) as kind (kind)}
              <button type="button" class="badge" title={KIND_LABEL[kind]} onclick={() => toggleExpand(piece)}>
                <Icon name={KIND_ICON[kind]} size={11} />
              </button>
            {/each}
            {#if piece.wiki_reference}
              <a
                class="badge"
                href={piece.wiki_reference}
                target="_blank"
                rel="noopener noreferrer"
                title="Open wiki reference"
              >
                <Icon name="link" size={11} />
              </a>
            {/if}
          </div>
        {/if}

        {#if expandedId === piece.id}
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
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--space-5);
    align-items: start;
  }
  .tile {
    padding: 0;
    overflow: hidden;
    cursor: default;
  }
  .tile-thumb {
    display: block;
    width: 100%;
    height: 140px;
    object-fit: cover;
    background: var(--surface-container-high);
    border-bottom: var(--border-width) solid var(--outline-variant);
  }
  .tile-trigger {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
    width: 100%;
    padding: var(--space-4);
    background: none;
    border: none;
    border-radius: 0;
    color: inherit;
    text-align: left;
    cursor: pointer;
  }
  .tile-trigger:hover:not(:disabled) {
    background: none;
  }
  .tile-title {
    font-family: var(--font-heading);
    font-weight: var(--font-heading-weight);
    font-size: var(--text-base);
    line-height: 1.25;
  }
  .tile-composer {
    color: var(--ink-soft);
    font-size: var(--text-sm);
    margin-top: -4px;
  }
  .goal-chip {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1);
    font-size: var(--text-xs);
    color: var(--accent-700);
    background: var(--accent-100);
    padding: 3px 10px;
    border-radius: var(--radius-full);
  }
  .badge-row {
    display: flex;
    gap: var(--space-2);
    padding: 0 var(--space-4) var(--space-4);
  }
  .badge {
    width: 20px;
    height: 20px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--surface-container-high);
    color: var(--ink-soft);
    border: none;
    border-radius: var(--radius-full);
    opacity: 1;
  }
  .badge:hover:not(:disabled) {
    background: color-mix(in srgb, var(--ink) calc(var(--state-hover) * 100%), var(--surface-container-high));
    color: var(--ink);
  }
  .disclosure {
    margin: 0 var(--space-4) var(--space-4);
    padding: var(--space-4);
    background: var(--surface-container-high);
    border-radius: var(--radius-sm);
    box-shadow: var(--elevation-1);
  }
  .add-resource {
    margin-top: var(--space-3);
  }
</style>
