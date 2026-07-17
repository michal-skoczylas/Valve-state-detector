<template>
  <div class="valve-card" :class="{'highlighted-card': highlighted}" @click="$emit('toggle-highlight', valve.id)">
    <div class="valve-header">
      <span>{{ valve.name }}</span>
      <span class="status-badge" :class="valve.state === 'Otwarty' ? 'status-open' : 'status-closed'">
        {{ valve.state }}
      </span>
    </div>
    <div class="valve-desc">{{ valve.desc }}</div>
    <div class="valve-fill">
      <span>Pokrycie: <strong>{{ valve.fill }}%</strong></span>
      <button class="btn-edit" @click.stop="$emit('edit', valve.id)">⚙️ Edytuj</button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  valve: Object,
  highlighted: Boolean
})
defineEmits(['toggle-highlight', 'edit'])
</script>

<style scoped>
.valve-card {
    background: #f8fafc;
    border: 2px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.valve-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: #cbd5e1;
}

.valve-card.highlighted-card {
    border-color: var(--highlight);
    background: #fffbeb;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
    transform: translateY(-2px);
}

.valve-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    font-size: 0.9rem;
    margin-bottom: 4px;
}

.valve-desc {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-style: italic;
    min-height: 14px;
}

.valve-fill {
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
    border-top: 1px solid var(--border);
    padding-top: 8px;
}

.status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
}

.status-open {
    background-color: #d1fae5;
    color: #047857;
    border: 1px solid #34d399;
}

.status-closed {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #f87171;
}
</style>
