<script lang="ts">
  import { setPracticeGoal, type PracticeGoal } from './api'

  let {
    goal = null,
    onSaved,
    onCancel,
  }: {
    goal?: PracticeGoal | null
    onSaved: (goal: PracticeGoal) => void
    onCancel?: () => void
  } = $props()

  let targetMinutes = $state('')
  let submitting = $state(false)
  let formError = $state<string | null>(null)

  $effect(() => {
    targetMinutes = goal ? String(goal.target_minutes) : ''
    formError = null
  })

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault()
    submitting = true
    formError = null
    try {
      const saved = await setPracticeGoal({ target_minutes: Number(targetMinutes) })
      onSaved(saved)
    } catch (err) {
      formError = err instanceof Error ? err.message : String(err)
    } finally {
      submitting = false
    }
  }
</script>

<form onsubmit={handleSubmit}>
  <label>
    Weekly target (minutes)
    <input type="number" bind:value={targetMinutes} required min="1" step="1" />
  </label>

  {#if formError}
    <p class="error">{formError}</p>
  {/if}

  <div class="actions">
    <button type="submit" disabled={submitting}>
      {#if submitting}Saving…{:else}{goal ? 'Update Goal' : 'Set Goal'}{/if}
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
