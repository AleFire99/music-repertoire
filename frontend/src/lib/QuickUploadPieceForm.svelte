<script lang="ts">
  import { quickUploadPiece, type Piece } from './api'

  let { onUploaded, onCancel }: { onUploaded: (piece: Piece) => void; onCancel?: () => void } =
    $props()

  let file = $state<File | null>(null)
  let submitting = $state(false)
  let formError = $state<string | null>(null)

  function handleFileChange(event: Event): void {
    file = (event.target as HTMLInputElement).files?.[0] ?? null
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    if (!file) return
    submitting = true
    formError = null
    try {
      const piece = await quickUploadPiece(file)
      onUploaded(piece)
      file = null
    } catch (err) {
      formError = err instanceof Error ? err.message : String(err)
    } finally {
      submitting = false
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <label>
    PDF file
    <input type="file" accept="application/pdf" onchange={handleFileChange} required />
  </label>
  <p class="hint">
    We'll guess the title and composer from the PDF, then let you review and fill in the rest.
  </p>

  {#if formError}
    <p class="error">{formError}</p>
  {/if}

  <div class="actions">
    <button type="submit" disabled={submitting || file === null}>
      {submitting ? 'Uploading…' : 'Upload'}
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
  .hint {
    margin: 0;
    font-size: var(--text-sm);
    color: var(--ink-soft);
  }
</style>
