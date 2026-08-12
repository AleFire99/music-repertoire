<script lang="ts">
  import { createRepertoireList, updateRepertoireList, type RepertoireList } from './api'

  let {
    list = null,
    onSaved,
    onCancel,
  }: {
    list?: RepertoireList | null
    onSaved: (list: RepertoireList) => void
    onCancel?: () => void
  } = $props()

  let name = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)

  $effect(() => {
    name = list?.name ?? ''
    formError = null
  })

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    submitting = true
    formError = null
    try {
      const saved = list
        ? await updateRepertoireList(list.id, { name: name.trim() })
        : await createRepertoireList({ name: name.trim() })
      onSaved(saved)
      if (!list) name = ''
    } catch (err) {
      formError = err instanceof Error ? err.message : String(err)
    } finally {
      submitting = false
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <label>
    Name
    <input type="text" bind:value={name} required maxlength="200" />
  </label>

  {#if formError}
    <p class="error">{formError}</p>
  {/if}

  <div class="actions">
    <button type="submit" disabled={submitting}>
      {#if submitting}Saving…{:else}{list ? 'Save' : 'Add List'}{/if}
    </button>
    {#if list}
      <button type="button" onclick={onCancel} disabled={submitting}>Cancel</button>
    {/if}
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
