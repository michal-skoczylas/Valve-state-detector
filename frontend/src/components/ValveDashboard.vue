<template>
  <section class="panel status-dashboard">
    <h3>Status Zaworów (ROI)</h3>
    <div class="valve-grid">
      <div v-if="valves.length === 0" class="empty-state">
        Rozpocznij konfigurację (wybierz źródło i narysuj strefy).
      </div>
      
      <ValveCard 
        v-for="v in valves" 
        :key="v.id" 
        :valve="v" 
        :highlighted="highlightedIndex === v.id"
        @toggle-highlight="$emit('toggle-highlight', $event)"
        @edit="$emit('edit', $event)"
      />
    </div>
  </section>
</template>

<script setup>
import ValveCard from './ValveCard.vue'

const props = defineProps({
  valves: Array,
  highlightedIndex: Number
})

defineEmits(['toggle-highlight', 'edit'])
</script>

<style scoped>
.status-dashboard {
    flex: 1;
}

.valve-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
}

.empty-state {
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
    font-size: 0.9rem;
    grid-column: 1 / -1;
}
</style>
