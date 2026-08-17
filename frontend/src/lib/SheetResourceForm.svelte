<script lang="ts">
  import {
    createSheetResource,
    uploadSheetResource,
    SHEET_RESOURCE_KINDS,
    type Piece,
    type SheetResource,
    type SheetResourceKind,
  } from './api'

  let {
    pieces,
    fixedPieceId,
    onSaved,
    onCancel,
  }: {
    pieces: Piece[]
    fixedPieceId?: number
    onSaved: (resource: SheetResource) => void
    onCancel?: () => void
  } = $props()

  let selectedPieceId = $state<number | ''>('')
  const pieceId = $derived(fixedPieceId ?? selectedPieceId)
  let kind = $state<SheetResourceKind>('url')
  let reference = $state('')
  let file = $state<File | null>(null)
  let label = $state('')
  let notes = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)
  const isUpload = $derived(kind === 'uploaded')

  function handleFileChange(event: Event): void {
    file = (event.target as HTMLInputElement).files?.[0] ?? null
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    submitting = true
    formError = null
    try {
      const saved = isUpload
        ? await uploadSheetResource({
            piece_id: Number(pieceId),
            file: file as File,
            label: label.trim() || null,
            notes: notes.trim() || null,
          })
        : await createSheetResource({
            piece_id: Number(pieceId),
            kind,
            reference: reference.trim(),
            label: label.trim() || null,
            notes: notes.trim() || null,
          })
      onSaved(saved)
      reference = ''
      file = null
      label = ''
      notes = ''
    } catch (err) {
      formError = err instanceof Error ? err.message : String(err)
    } finally {
      submitting = false
    }
  }
</script>

<form onsubmit={handleSubmit}>
  {#if fixedPieceId === undefined}
    <label>
      Piece
      <select bind:value={selectedPieceId} required>
        <option value="" disabled>Select a piece…</option>
        {#each pieces as piece (piece.id)}
          <option value={piece.id}>{piece.title}</option>
        {/each}
      </select>
    </label>
  {/if}
  <label>
    Kind
    <select bind:value={kind}>
      {#each SHEET_RESOURCE_KINDS as k (k)}
        <option value={k}>{k}</option>
      {/each}
    </select>
  </label>
  {#if isUpload}
    <label>
      PDF file
      <input type="file" accept="application/pdf" onchange={handleFileChange} required />
    </label>
  {:else}
    <label>
      Reference
      <input
        type="text"
        bind:value={reference}
        maxlength="1000"
        placeholder="URL, book + page, or file path"
        required
      />
    </label>
  {/if}
  <label>
    Label (optional)
    <input type="text" bind:value={label} maxlength="200" placeholder="IMSLP edition" />
  </label>
  <label>
    Notes (optional)
    <textarea bind:value={notes} maxlength="2000" rows="3"></textarea>
  </label>

  {#if formError}
    <p class="error">{formError}</p>
  {/if}

  <div class="actions">
    <button
      type="submit"
      disabled={submitting ||
        pieceId === '' ||
        (isUpload ? file === null : reference.trim() === '')}
    >
      {submitting ? 'Saving…' : 'Add Resource'}
    </button>
    <button type="button" class="secondary" onclick={onCancel} disabled={submitting}>Cancel</button>
  </div>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }
</style>
