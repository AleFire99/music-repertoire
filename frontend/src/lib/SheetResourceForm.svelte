<script lang="ts">
  import {
    createSheetResource,
    SHEET_RESOURCE_KINDS,
    type Piece,
    type SheetResource,
    type SheetResourceKind,
  } from './api'

  let {
    pieces,
    onSaved,
  }: {
    pieces: Piece[]
    onSaved: (resource: SheetResource) => void
  } = $props()

  let pieceId = $state<number | ''>('')
  let kind = $state<SheetResourceKind>('url')
  let reference = $state('')
  let label = $state('')
  let notes = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    submitting = true
    formError = null
    try {
      const payload = {
        piece_id: Number(pieceId),
        kind,
        reference: reference.trim(),
        label: label.trim() || null,
        notes: notes.trim() || null,
      }
      const saved = await createSheetResource(payload)
      onSaved(saved)
      reference = ''
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
  <label>
    Piece
    <select bind:value={pieceId} required>
      <option value="" disabled>Select a piece…</option>
      {#each pieces as piece (piece.id)}
        <option value={piece.id}>{piece.title}</option>
      {/each}
    </select>
  </label>
  <label>
    Kind
    <select bind:value={kind}>
      {#each SHEET_RESOURCE_KINDS as k (k)}
        <option value={k}>{k}</option>
      {/each}
    </select>
  </label>
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
    <button type="submit" disabled={submitting || pieceId === '' || reference.trim() === ''}>
      {submitting ? 'Saving…' : 'Add Resource'}
    </button>
  </div>
</form>

<style>
  form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    font-size: 0.9rem;
  }
  .actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.25rem;
  }
  .error {
    color: #b00020;
  }
</style>
